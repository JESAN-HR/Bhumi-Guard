"""One-time manual transcription of the National Portal district reference.

No crawler, guessed children, official codes or scraped personal data.
English values are stored human transliterations, not official spellings.
"""

import json
from pathlib import Path

DISTRICTS = """Dhaka|ঢাকা
Faridpur|ফরিদপুর
Gazipur|গাজীপুর
Gopalganj|গোপালগঞ্জ
Kishoreganj|কিশোরগঞ্জ
Madaripur|মাদারীপুর
Manikganj|মানিকগঞ্জ
Munshiganj|মুন্সীগঞ্জ
Narayanganj|নারায়ণগঞ্জ
Narsingdi|নরসিংদী
Rajbari|রাজবাড়ী
Shariatpur|শরীয়তপুর
Tangail|টাঙ্গাইল
Bagerhat|বাগেরহাট
Chuadanga|চুয়াডাঙ্গা
Jashore|যশোর
Jhenaidah|ঝিনাইদহ
Khulna|খুলনা
Kushtia|কুষ্টিয়া
Magura|মাগুরা
Meherpur|মেহেরপুর
Narail|নড়াইল
Satkhira|সাতক্ষীরা
Bandarban|বান্দরবান
Brahmanbaria|ব্রাহ্মণবাড়িয়া
Chandpur|চাঁদপুর
Chattogram|চট্টগ্রাম
Cumilla|কুমিল্লা
Cox's Bazar|কক্সবাজার
Feni|ফেনী
Khagrachhari|খাগড়াছড়ি
Lakshmipur|লক্ষ্মীপুর
Noakhali|নোয়াখালী
Rangamati|রাঙ্গামাটি
Bogura|বগুড়া
Joypurhat|জয়পুরহাট
Naogaon|নওগাঁ
Natore|নাটোর
Chapainawabganj|চাঁপাইনবাবগঞ্জ
Pabna|পাবনা
Rajshahi|রাজশাহী
Sirajganj|সিরাজগঞ্জ
Habiganj|হবিগঞ্জ
Moulvibazar|মৌলভীবাজার
Sunamganj|সুনামগঞ্জ
Sylhet|সিলেট
Dinajpur|দিনাজপুর
Gaibandha|গাইবান্ধা
Kurigram|কুড়িগ্রাম
Lalmonirhat|লালমনিরহাট
Nilphamari|নীলফামারী
Panchagarh|পঞ্চগড়
Rangpur|রংপুর
Thakurgaon|ঠাকুরগাঁও
Jamalpur|জামালপুর
Mymensingh|ময়মনসিংহ
Netrokona|নেত্রকোণা
Sherpur|শেরপুর
Barguna|বরগুনা
Barishal|বরিশাল
Bhola|ভোলা
Jhalakathi|ঝালকাঠি
Patuakhali|পটুয়াখালী
Pirojpur|পিরোজপুর"""


def expand():
    path = Path("data/locations/locations.json")
    data = json.loads(path.read_text(encoding="utf-8"))
    source = dict(
        id="geo-national-districts-2026",
        title="Bangladesh National Portal — district directory",
        url="https://bangladesh.gov.bd/views/district-list",
        retrieved_at="2026-10-17",
        verification_status="verified_public_authoritative_text",
        evidence="64 district names manually checked against the official directory. English names are human transliterations. This does not establish upazila or mouza completeness.",
    )
    upazila_source = dict(
        id="geo-national-dhaka-upazilas-2026",
        title="Bangladesh National Portal — Dhaka district upazilas",
        url="https://bangladesh.gov.bd/views/upazila-list/উপজেলাসমূহ/",
        retrieved_at="2026-10-17",
        verification_status="verified_public_authoritative_text",
        evidence="Dhaka district section explicitly lists Dhamrai, Dohar, Keraniganj, Nawabganj and Savar. Cached page header says 495 nationwide; the newer district portal header says 500. Nationwide completeness is unresolved.",
    )
    for item in [source, upazila_source]:
        if not any(s["id"] == item["id"] for s in data["sources"]):
            data["sources"].append(item)

    def add(id, kind, parent, en, bn, src):
        if not any(n["id"] == id for n in data["locations"]):
            data["locations"].append(
                dict(
                    id=id,
                    kind=kind,
                    parent_id=parent,
                    name_en=en,
                    name_bn=bn,
                    official_code=None,
                    jl_number=None,
                    verification_status="verified",
                    source_ids=[src],
                )
            )

    for line in DISTRICTS.splitlines():
        en, bn = line.split("|")
        slug = en.lower().replace("'", "").replace(" ", "-")
        add("loc-" + slug, "district", None, en, bn, source["id"])
    for en, bn in [
        ("Dohar", "দোহার"),
        ("Keraniganj", "কেরাণীগঞ্জ"),
        ("Nawabganj", "নবাবগঞ্জ"),
    ]:
        add(
            "loc-dhaka-" + en.lower(),
            "upazila",
            "loc-dhaka",
            en,
            bn,
            upazila_source["id"],
        )
    data["scope"] = (
        "64 districts; curated upazila references; three verified mouzas. Nationwide upazila and mouza completeness is not established."
    )
    data["curated_on"] = "2026-10-17"
    assert sum(n["kind"] == "district" for n in data["locations"]) == 64
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    expand()
