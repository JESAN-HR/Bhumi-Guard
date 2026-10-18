"""Build reference JSON from reviewed manual transcription, without network access."""

import json
from pathlib import Path
from backend.app.geography import validate_dataset, coverage


def expand():
    root = Path(__file__).resolve().parents[1]
    path = root / "data/locations/locations.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    source = dict(
        id="geo-national-upazilas-snapshot-2026",
        title="Bangladesh National Portal — district-grouped upazila directory snapshot",
        url="https://bangladesh.gov.bd/views/upazila-list/উপজেলাসমূহ/",
        retrieved_at="2026-10-17",
        verification_status="verified_public_authoritative_text",
        evidence="Manually transcribed district sections from the cached May 2026 directory (header 495). The newer district directory header says 500; completeness is not established. Duplicate Shaistaganj labels are represented once. Jiyanagar is separately supported by the March 2026 upazila portal renaming notice. English names are human transliterations, not official codes or certified spellings.",
    )
    if not any(s["id"] == source["id"] for s in data["sources"]):
        data["sources"].append(source)
    else:
        data["sources"] = [
            source if s["id"] == source["id"] else s for s in data["sources"]
        ]
    nodes = {r["id"]: r for r in data["locations"]}
    for line in (
        (root / "data/locations/upazilas-curated.txt")
        .read_text(encoding="utf-8")
        .splitlines()
    ):
        if not line or line.startswith("#"):
            continue
        district, entries = line.split(":", 1)
        for entry in entries.split(";"):
            en, bn = entry.split("|")
            slug = en.lower().replace(" ", "-")
            id = "loc-" + (
                slug
                if district == "dhaka" and slug in ("savar", "dhamrai")
                else district + "-" + slug
            )
            if id not in nodes:
                nodes[id] = dict(
                    id=id,
                    kind="upazila",
                    parent_id="loc-" + district,
                    name_en=en,
                    name_bn=bn,
                    official_code=None,
                    jl_number=None,
                    verification_status="verified",
                    source_ids=[source["id"]],
                )
    notice = dict(
        id="geo-jiyanagar-2026",
        title="Jiyanagar Upazila — notice on renaming Indurkani to Jiyanagar",
        url="https://indurkani.pirojpur.gov.bd/pages/notices/69b2d2a70e394cfb3829fcd7",
        retrieved_at="2026-10-18",
        verification_status="verified_public_authoritative_text",
        evidence="Official portal indexed notice published 12 March 2026 explicitly names Pirojpur district and renaming Indurkani upazila to Jiyanagar. National directory also lists Jiyanagar. Direct fetch failed; indexed notice text was read, attachment not inspected. No separate Indurkani node or automatic survey identity mapping is created.",
    )
    if not any(s["id"] == notice["id"] for s in data["sources"]):
        data["sources"].append(notice)
    nodes["loc-pirojpur-jiyanagar"] = dict(
        id="loc-pirojpur-jiyanagar",
        kind="upazila",
        parent_id="loc-pirojpur",
        name_en="Jiyanagar",
        name_bn="জিয়ানগর",
        official_code=None,
        jl_number=None,
        verification_status="verified",
        source_ids=[source["id"], notice["id"]],
    )
    data["locations"] = list(nodes.values())
    data["scope"] = (
        "64 districts; dated upazila directory snapshot; three verified mouzas. Nationwide upazila and mouza completeness is NOT established."
    )
    validate_dataset(data)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(coverage(data["locations"])["counts"])


if __name__ == "__main__":
    expand()
