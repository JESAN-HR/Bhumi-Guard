"""Twenty labeled, entirely synthetic scenarios. No official record identifiers."""

import copy

SPECS = [
    ("valid", "Valid transfer", "সঙ্গত হস্তান্তর", "20", [], {}),
    (
        "excess",
        "Excess proposed area",
        "অতিরিক্ত প্রস্তাবিত জমি",
        "110",
        ["EXCESS_AREA"],
        {},
    ),
    (
        "overlap",
        "Overlapping commitment",
        "পরস্পরবিরোধী অঙ্গীকার",
        "40",
        ["OVERLAPPING_TRANSFER"],
        {"pending": "70"},
    ),
    (
        "mutation-area",
        "Deed / mutation area mismatch",
        "দলিল / নামজারির পরিমাণে অমিল",
        "20",
        ["AREA_MISMATCH"],
        {"mutation_area": "90"},
    ),
    (
        "seller",
        "Seller reference mismatch",
        "বিক্রেতার রেফারেন্সে অমিল",
        "20",
        ["SELLER_MISMATCH"],
        {"seller": "DEMO-PARTY-B"},
    ),
    (
        "other-mouza",
        "Same dag, another mouza",
        "একই দাগ, অন্য মৌজা",
        "20",
        [],
        {"mouza": "loc-uttar-paragao"},
    ),
    (
        "partial",
        "Valid partial sale",
        "সঙ্গত আংশিক বিক্রয়",
        "25",
        [],
        {"completed": "60"},
    ),
    (
        "pending",
        "Pending transfer alone",
        "শুধু অপেক্ষমাণ হস্তান্তর",
        "20",
        [],
        {"pending": "10"},
    ),
    (
        "cancelled",
        "Cancelled transfer excluded",
        "বাতিল হস্তান্তর বাদ",
        "20",
        [],
        {"cancelled": "95"},
    ),
    (
        "missing-history",
        "History incomplete",
        "অসম্পূর্ণ ইতিহাস",
        "20",
        ["MISSING_INFORMATION"],
        {"history": False},
    ),
    (
        "unreadable",
        "Unreadable dag",
        "অপাঠ্য দাগ",
        "20",
        ["MISSING_INFORMATION", "AMBIGUOUS_IDENTITY"],
        {"dag": None},
    ),
    ("bangla", "Bangla numeric input", "বাংলা অঙ্কে পরিমাণ", "২৫.৫০", [], {}),
    ("english", "English numeric input", "ইংরেজি অঙ্কে পরিমাণ", "25.50", [], {}),
    (
        "correction",
        "Correction exercise: 120 → 20",
        "সংশোধন অনুশীলন: ১২০ → ২০",
        "120",
        ["EXCESS_AREA"],
        {},
    ),
    (
        "survey",
        "Uncertain survey mapping",
        "অনিশ্চিত জরিপ সম্পর্ক",
        "20",
        ["AMBIGUOUS_IDENTITY"],
        {"survey": "DEMO-CS"},
    ),
    (
        "future",
        "Future transfer excluded",
        "পরবর্তী তারিখের হস্তান্তর বাদ",
        "20",
        [],
        {"future": "95"},
    ),
    (
        "exact",
        "Exact decimal remainder",
        "সঠিক দশমিক অবশিষ্ট",
        "0.2",
        [],
        {"holding": "0.3", "completed": "0.1"},
    ),
    (
        "joint",
        "Unsupported joint interest",
        "অসমর্থিত যৌথ স্বত্ব",
        "20",
        ["AMBIGUOUS_IDENTITY"],
        {"ambiguous": True},
    ),
    (
        "missing-mutation",
        "Mutation not supplied",
        "নামজারি সরবরাহ করা হয়নি",
        "20",
        ["MISSING_INFORMATION"],
        {"mutation": False},
    ),
    (
        "conflict-missing",
        "Conflict and missing history",
        "অমিল ও অসম্পূর্ণ ইতিহাস",
        "110",
        ["EXCESS_AREA", "MISSING_INFORMATION"],
        {"history": False},
    ),
    (
        "mutation-party",
        "Mutation holder mismatch",
        "নামজারিতে স্বত্বধারীর অমিল",
        "20",
        ["SELLER_MISMATCH"],
        {"mutation_party": "DEMO-PARTY-B"},
    ),
    (
        "explicit-overlap",
        "Referenced overlapping interest",
        "একই স্বত্বের উল্লিখিত সংঘাত",
        "20",
        ["OVERLAPPING_TRANSFER"],
        {"pending": "10", "overlap": True},
    ),
]


def scenarios():
    result = []
    for key, en, bn, area, expected, opt in SPECS:
        f = dict(
            seller_id=opt.get("seller", "DEMO-PARTY-A"),
            holding_id="DEMO-HOLDING",
            mouza_id=opt.get("mouza", "loc-birulia"),
            survey=opt.get("survey", "DEMO-RS"),
            dag=opt.get("dag", "DEMO-DAG-17"),
            area=area,
            date="2026-09-01",
            unit="decimal",
        )
        h = dict(
            holding_id="DEMO-HOLDING",
            mouza_id=f["mouza_id"],
            survey="DEMO-RS",
            dag="DEMO-DAG-17",
            party_id="DEMO-PARTY-A",
            area=opt.get("holding", "100"),
            history_complete=opt.get("history", True),
            ambiguous=opt.get("ambiguous", False),
        )
        ts = []
        for kind in ("completed", "pending", "cancelled", "future"):
            if kind in opt:
                ts.append(
                    dict(
                        id="DEMO-" + kind,
                        holding_id="DEMO-HOLDING",
                        document_id="DEMO-RECORDS",
                        area=opt[kind],
                        date="2026-10-01" if kind == "future" else "2026-05-01",
                        status="completed" if kind == "future" else kind,
                        overlap_reference=opt.get("overlap", False),
                    )
                )
        m = (
            dict(
                party_id=opt.get("mutation_party", "DEMO-PARTY-A"),
                area=opt.get("mutation_area", h["area"]),
            )
            if opt.get("mutation", True)
            else None
        )
        result.append(
            dict(
                id=key,
                title={"en": en, "bn": bn},
                fields=f,
                holding=h,
                transfers=ts,
                mutation=m,
                expected=expected,
            )
        )
    return copy.deepcopy(result)
