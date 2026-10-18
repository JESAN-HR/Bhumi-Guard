"""Validated append-only geographic reference import; independent of scenarios."""

import argparse
import hashlib
import json
from collections import Counter
from datetime import date
from pathlib import Path
from urllib.parse import urlparse
from sqlalchemy import select
from .db import Session
from .models import Location

KINDS = ("district", "upazila", "mouza")


def validate_dataset(data):
    if data.get("schema_version") != 1:
        raise ValueError("Unsupported schema_version; expected 1")
    sources = data.get("sources", [])
    rows = data.get("locations", [])
    if not rows or not sources:
        raise ValueError("locations and sources cannot be empty")
    for entries, label in [(sources, "source"), (rows, "location")]:
        ids = [r["id"] for r in entries]
        if len(ids) != len(set(ids)):
            raise ValueError(f"Duplicate {label} IDs")
    source_by_id = {s["id"]: s for s in sources}
    nodes = {r["id"]: r for r in rows}
    for s in sources:
        if urlparse(s.get("url", "")).scheme not in ("https", "http"):
            raise ValueError("Every source needs a public reference URL")
        date.fromisoformat(s["retrieved_at"])
        if (
            not s.get("title")
            or not s.get("evidence")
            or s.get("verification_status") != "verified_public_authoritative_text"
        ):
            raise ValueError("Source verification, title and evidence are required")
    for row in rows:
        if row["kind"] not in KINDS:
            raise ValueError(
                "Unsupported location kind; villages/unions are not mouzas"
            )
        if not row["id"].startswith("loc-") or len(row["id"]) > 64:
            raise ValueError(
                "Use a stable internal loc- identifier of at most 64 characters"
            )
        if any(
            not isinstance(row.get(k), str) or not row[k].strip() or len(row[k]) > 120
            for k in ("name_en", "name_bn")
        ):
            raise ValueError("Both stored names are required (maximum 120 characters)")
        if row.get("verification_status") != "verified":
            raise ValueError("Unverified rows cannot be enabled")
        if not row.get("source_ids") or any(
            s not in source_by_id for s in row["source_ids"]
        ):
            raise ValueError("Missing source reference")
        expected = {"district": None, "upazila": "district", "mouza": "upazila"}[
            row["kind"]
        ]
        parent = nodes.get(row.get("parent_id"))
        if (expected is None and row.get("parent_id") is not None) or (
            expected and (not parent or parent["kind"] != expected)
        ):
            raise ValueError(
                "Invalid parent hierarchy; include ancestors in the import"
            )
        if row.get("official_code") is not None or row.get("jl_number") is not None:
            raise ValueError(
                "This importer intentionally excludes official/JL codes; use documented internal IDs"
            )
    # No nationwide-complete flag is accepted merely because a file has many rows.
    return source_by_id, nodes


def coverage(rows):
    counts = Counter(r["kind"] for r in rows)
    parents = {r.get("parent_id") for r in rows}
    return {
        "counts": {kind: counts[kind] for kind in KINDS},
        "national_complete": False,
        "unpopulated_parents": [
            r["id"] for r in rows if r["kind"] != "mouza" and r["id"] not in parents
        ],
        "meaning": "Imported verified rows, not a claim that every child or nationwide record is present.",
    }


def import_locations(db, path):
    data = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    sources, nodes = validate_dataset(data)
    # Check collisions before writing anything: preserve IDs referenced by saved cases.
    existing = {r.id: r for r in db.scalars(select(Location))}
    for row in nodes.values():
        old = existing.get(row["id"])
        if old and any(
            getattr(old, k) != row[k]
            for k in ("kind", "parent_id", "name_en", "name_bn")
        ):
            raise ValueError(
                f"Existing identity differs: {row['id']}. Use a reviewed migration, not silent replacement."
            )
    added = 0
    for kind in KINDS:
        for row in nodes.values():
            if row["kind"] == kind and row["id"] not in existing:
                db.add(
                    Location(
                        id=row["id"],
                        kind=kind,
                        parent_id=row["parent_id"],
                        name_en=row["name_en"],
                        name_bn=row["name_bn"],
                        provenance={
                            "verification_status": "verified",
                            "sources": [sources[s] for s in row["source_ids"]],
                        },
                    )
                )
                added += 1
        db.flush()
    return added


def main():
    parser = argparse.ArgumentParser(
        description="Validate an approved geography file; write only with --apply. Does not create accounts or reset cases."
    )
    parser.add_argument("file", type=Path)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    raw = args.file.read_bytes()
    data = json.loads(raw.decode("utf-8-sig"))
    validate_dataset(data)
    report = coverage(data["locations"]) | {
        "sha256": hashlib.sha256(raw).hexdigest(),
        "applied": args.apply,
    }
    with Session() as db:
        report["new_rows"] = import_locations(db, args.file)
        if args.apply:
            db.commit()
        else:
            db.rollback()
    if args.report:
        args.report.write_text(
            json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
