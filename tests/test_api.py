import io
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from argon2 import PasswordHasher
from PIL import Image
from backend.app.main import app, db_session
from backend.app.db import Base, ROOT
from backend.app.models import User, Party, ReviewCase, Document
from backend.app.seed import import_locations


@pytest.fixture
def client(tmp_path):
    engine = create_engine(
        "sqlite:///" + str(tmp_path / "test.db"),
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(engine, expire_on_commit=False)
    with factory() as db:
        import_locations(db, ROOT / "data/locations/locations.json")
        db.add_all(
            [
                Party(id="DEMO-PARTY-A", label_en="Demo A", label_bn="ডেমো ক"),
                Party(id="DEMO-PARTY-B", label_en="Demo B", label_bn="ডেমো খ"),
            ]
        )
        db.add_all(
            [
                User(
                    username="tester",
                    password_hash=PasswordHasher().hash("test-only-password"),
                ),
                User(
                    username="other",
                    password_hash=PasswordHasher().hash("test-only-password"),
                ),
            ]
        )
        db.commit()

    def override():
        with factory() as db:
            yield db

    app.dependency_overrides[db_session] = override
    with TestClient(app) as c:
        r = c.post(
            "/api/login", json={"username": "tester", "password": "test-only-password"}
        )
        c.headers["x-csrf-token"] = r.json()["csrf"]
        yield c
    app.dependency_overrides.clear()
    engine.dispose()


def create(c, scenario="valid"):
    r = c.post(
        "/api/cases",
        json={"scenario_id": scenario, "mouza_id": "loc-birulia", "fictional": True},
    )
    assert r.status_code == 200, r.text
    return r.json()


def confirm(c, case, area=None):
    fields = case["fields"].copy()
    if area:
        fields["area"] = area
    r = c.put(
        "/api/cases/" + case["id"] + "/fields",
        json={"fields": fields, "confirmed": True, "version": case["version"]},
    )
    assert r.status_code == 200, r.text
    return r.json()


def test_full_persistence_correction_staleness(client):
    c = client
    case = create(c, "correction")
    url = "/api/cases/" + case["id"]
    assert c.post(url + "/analyze").status_code == 409
    case = confirm(c, case)
    case = c.post(url + "/analyze").json()
    old = case["analyses"][-1]
    assert old["outcome"] == "conflict"
    case = confirm(c, case, "২০")
    assert case["analyses"][-1]["stale"]
    assert (
        c.post(
            url + "/decisions",
            json={
                "analysis_id": old["id"],
                "action": "reviewed",
                "notes": "Verified fictional evidence.",
            },
        ).status_code
        == 409
    )
    case = c.post(url + "/analyze").json()
    new = case["analyses"][-1]
    assert new["outcome"] == "clear"
    decision = c.post(
        url + "/decisions",
        json={
            "analysis_id": new["id"],
            "action": "reviewed",
            "notes": "Verified fictional evidence.",
        },
    )
    assert decision.status_code == 200
    saved = c.get(url).json()
    assert len(saved["analyses"]) == 2 and len(saved["decisions"]) == 1
    assert saved["holding"]["area"] == "100.000000"
    assert saved["extractions"][0]["result"]["fields"]["area"] == "120"
    assert saved["corrections"][-1]["after"]["area"] == "২০"


def test_authorization_and_csrf(client):
    case = create(client)
    doc = case["documents"][0]["id"]
    assert (
        client.post(
            "/api/cases/" + case["id"] + "/analyze", headers={"x-csrf-token": ""}
        ).status_code
        == 403
    )
    r = client.post(
        "/api/login", json={"username": "other", "password": "test-only-password"}
    )
    client.headers["x-csrf-token"] = r.json()["csrf"]
    assert client.get("/api/cases/" + case["id"]).status_code == 404
    assert client.get("/api/documents/" + doc).status_code == 404
    assert client.get("/api/cases").json() == []
    client.cookies.clear()
    assert client.get("/api/cases").status_code == 401


def test_unreadable_cannot_confirm(client):
    case = create(client, "unreadable")
    assert (
        client.put(
            "/api/cases/" + case["id"] + "/fields",
            json={"fields": case["fields"], "confirmed": True, "version": 1},
        ).status_code
        == 400
    )


def test_missing_api_manual_fallback(client, monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    case = create(client)
    image = io.BytesIO()
    Image.new("RGB", (20, 20), "white").save(image, format="PNG")
    r = client.post(
        "/api/cases/" + case["id"] + "/documents",
        files={"file": ("fictional.png", image.getvalue(), "image/png")},
        data={"fictional": "true"},
    )
    assert r.status_code == 200
    case = r.json()
    doc = case["documents"][-1]["id"]
    assert client.post("/api/documents/" + doc + "/extract").status_code == 503
    assert client.get("/api/documents/" + doc).status_code == 200
    assert confirm(client, case)["confirmed"]


def test_upload_validation(client):
    case = create(client)
    url = "/api/cases/" + case["id"] + "/documents"
    assert (
        client.post(
            url,
            files={"file": ("fake.pdf", b"bad", "application/pdf")},
            data={"fictional": "true"},
        ).status_code
        == 400
    )
    assert (
        client.post(
            url,
            files={"file": ("fake.html", b"<script>", "text/html")},
            data={"fictional": "true"},
        ).status_code
        == 400
    )


def test_optimistic_version(client):
    case = create(client)
    confirm(client, case)
    r = client.put(
        "/api/cases/" + case["id"] + "/fields",
        json={"fields": case["fields"], "confirmed": True, "version": 1},
    )
    assert r.status_code == 409


def test_fictional_and_geography_validation(client):
    assert len(client.get("/api/locations?kind=district").json()) == 64
    children = client.get("/api/locations?kind=upazila&parent_id=loc-chattogram").json()
    assert len(children) == 15
    assert all(row["parent_id"] == "loc-chattogram" for row in children)
    assert (
        client.get("/api/locations?kind=mouza&parent_id=loc-chattogram-anwara").json()
        == []
    )
    assert client.get("/api/locations?kind=village").status_code == 422
    assert (
        client.post(
            "/api/cases", json={"mouza_id": "loc-birulia", "fictional": False}
        ).status_code
        == 400
    )
    assert (
        client.post(
            "/api/cases", json={"mouza_id": "loc-dhaka", "fictional": True}
        ).status_code
        == 400
    )
