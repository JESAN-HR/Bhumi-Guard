import copy
import json
import pytest
from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import Session
from backend.app.db import Base, ROOT
from backend.app.models import Location
from backend.app.geography import validate_dataset, coverage, import_locations


@pytest.fixture
def dataset():
    return json.loads(
        (ROOT / "data/locations/locations.json").read_text(encoding="utf-8")
    )


def test_reference_snapshot(dataset):
    _, nodes = validate_dataset(dataset)
    report = coverage(nodes.values())
    assert report["counts"] == {"district": 64, "upazila": 495, "mouza": 3}
    assert not report["national_complete"]
    assert "loc-chattogram-anwara" in report["unpopulated_parents"]
    assert nodes["loc-savar"]["parent_id"] == "loc-dhaka"
    assert nodes["loc-birulia"]["parent_id"] == "loc-savar"
    assert nodes["loc-pirojpur-jiyanagar"]["parent_id"] == "loc-pirojpur"
    # Same names in different districts remain distinct identities.
    assert (
        nodes["loc-gazipur-kaliganj"]["parent_id"]
        != nodes["loc-jhenaidah-kaliganj"]["parent_id"]
    )


@pytest.mark.parametrize(
    "defect", ["duplicate", "parent", "source", "unverified", "code", "names"]
)
def test_invalid_import_rejected(dataset, defect):
    row = next(r for r in dataset["locations"] if r["kind"] == "mouza")
    if defect == "duplicate":
        dataset["locations"].append(copy.deepcopy(row))
    elif defect == "parent":
        row["parent_id"] = "loc-dhaka"
    elif defect == "source":
        row["source_ids"] = ["unknown"]
    elif defect == "unverified":
        row["verification_status"] = "unverified"
    elif defect == "code":
        row["official_code"] = "invented"
    elif defect == "names":
        row["name_bn"] = ""
    with pytest.raises(ValueError):
        validate_dataset(dataset)


def test_import_idempotent_and_preserves_identity(dataset, tmp_path):
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    path = tmp_path / "locations.json"
    path.write_text(json.dumps(dataset), encoding="utf-8")
    with Session(engine) as db:
        assert import_locations(db, path) == 562
        db.commit()
        assert import_locations(db, path) == 0
        assert db.scalar(select(func.count()).select_from(Location)) == 562
        dataset["locations"][0]["name_en"] = "Silent replacement"
        path.write_text(json.dumps(dataset), encoding="utf-8")
        with pytest.raises(ValueError, match="Existing identity differs"):
            import_locations(db, path)
        db.rollback()
        assert (
            db.get(Location, dataset["locations"][0]["id"]).name_en
            != "Silent replacement"
        )
    engine.dispose()
