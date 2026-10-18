"""Pure deterministic checks. Decimal strings at the boundary; no identity inference."""

from decimal import Decimal, InvalidOperation
from datetime import date

DIGITS = str.maketrans("০১২৩৪৫৬৭৮৯", "0123456789")


def number(value):
    try:
        result = Decimal(str(value).translate(DIGITS).strip())
        if (
            not result.is_finite()
            or result < 0
            or result > Decimal("999999999")
            or result.as_tuple().exponent < -6
        ):
            raise ValueError("invalid_number")
        return result
    except (InvalidOperation, TypeError):
        raise ValueError("invalid_number")


TEMPLATES = {
    "EXCESS_AREA": (
        "Proposed area exceeds the documented remaining holding.",
        "প্রস্তাবিত জমি নথিভুক্ত অবশিষ্ট স্বত্বের চেয়ে বেশি।",
        "Reconcile completed transfers and the holding area.",
        "সম্পন্ন হস্তান্তর ও স্বত্বের পরিমাণ মিলিয়ে দেখুন।",
    ),
    "OVERLAPPING_TRANSFER": (
        "Supplied records indicate potentially overlapping commitments for this seller interest.",
        "সরবরাহকৃত নথিতে একই বিক্রেতার স্বত্বে সম্ভাব্য পরস্পরবিরোধী হস্তান্তর রয়েছে।",
        "Inspect the referenced transfer and identify the affected interest.",
        "উল্লিখিত হস্তান্তর ও সংশ্লিষ্ট স্বত্ব পরীক্ষা করুন।",
    ),
    "SELLER_MISMATCH": (
        "Explicit party references disagree across supplied records.",
        "সরবরাহকৃত নথিতে পক্ষের রেফারেন্সে অমিল রয়েছে।",
        "Obtain evidence linking the seller to this holding; names alone are insufficient.",
        "এই স্বত্বের সঙ্গে বিক্রেতার সম্পর্কের প্রমাণ সংগ্রহ করুন; শুধু নাম যথেষ্ট নয়।",
    ),
    "AREA_MISMATCH": (
        "Holding and mutation area fields disagree.",
        "স্বত্ব ও নামজারি নথির জমির পরিমাণে অমিল রয়েছে।",
        "Reconcile the supplied record areas.",
        "সরবরাহকৃত নথির পরিমাণ যাচাই করুন।",
    ),
    "MISSING_INFORMATION": (
        "Critical identifiers, records or complete relevant history are missing.",
        "গুরুত্বপূর্ণ পরিচিতি, নথি অথবা প্রাসঙ্গিক পূর্ণ ইতিহাস অনুপস্থিত।",
        "Request the listed missing evidence before relying on the result.",
        "ফলাফলের ওপর নির্ভর করার আগে অনুপস্থিত প্রমাণ সংগ্রহ করুন।",
    ),
    "AMBIGUOUS_IDENTITY": (
        "Parcel/survey mapping or ownership structure requires manual review.",
        "দাগ/জরিপের সম্পর্ক অথবা মালিকানার কাঠামো ম্যানুয়াল পর্যালোচনা প্রয়োজন।",
        "Verify mouza, survey and seller interest; do not equate survey records automatically.",
        "মৌজা, জরিপ ও বিক্রেতার স্বত্ব যাচাই করুন; ভিন্ন জরিপ স্বয়ংক্রিয়ভাবে এক করবেন না।",
    ),
}


def analyze(fields, holding, transfers, mutation, sources):
    findings = []

    def add(code, values, refs=None):
        en, bn, ae, ab = TEMPLATES[code]
        findings.append(
            dict(
                code=code,
                priority=(
                    "information"
                    if code in ("MISSING_INFORMATION", "AMBIGUOUS_IDENTITY")
                    else "conflict"
                ),
                values=values,
                sources=refs if refs is not None else sources,
                explanation={"en": en, "bn": bn},
                action={"en": ae, "bn": ab},
                assumptions={
                    "en": "Only supplied records are checked. No legal ownership determination.",
                    "bn": "শুধু সরবরাহকৃত নথি যাচাই করা হয়েছে। আইনগত মালিকানা নির্ধারণ করা হয়নি।",
                },
            )
        )

    missing = [
        key
        for key in ("seller_id", "dag", "survey", "area", "date", "holding_id")
        if fields.get(key) in (None, "")
    ]
    if not holding:
        add(
            "MISSING_INFORMATION",
            {"missing": missing + ["holding", "mutation", "history"]},
        )
        return "insufficient", findings
    if not holding["history_complete"]:
        missing.append("history")
    if not mutation:
        missing.append("mutation")
    if missing:
        add("MISSING_INFORMATION", {"missing": missing})
    identity_matches = all(
        fields.get(k) == holding[k] for k in ("holding_id", "mouza_id", "survey", "dag")
    )
    if not identity_matches or holding.get("ambiguous"):
        add(
            "AMBIGUOUS_IDENTITY",
            {
                "proposed": {
                    k: fields.get(k)
                    for k in ("holding_id", "mouza_id", "survey", "dag")
                },
                "record": {
                    k: holding[k] for k in ("holding_id", "mouza_id", "survey", "dag")
                },
            },
        )
    if fields.get("seller_id") and (
        fields["seller_id"] != holding["party_id"]
        or mutation
        and mutation["party_id"] != holding["party_id"]
    ):
        add(
            "SELLER_MISMATCH",
            {
                "seller": fields["seller_id"],
                "holder": holding["party_id"],
                "mutation_holder": mutation["party_id"] if mutation else None,
            },
        )
    if mutation and number(mutation["area"]) != number(holding["area"]):
        add(
            "AREA_MISMATCH",
            {"holding_area": holding["area"], "mutation_area": mutation["area"]},
        )
    if (
        fields.get("area")
        and fields.get("date")
        and identity_matches
        and not holding.get("ambiguous")
    ):
        proposal_date = date.fromisoformat(fields["date"])
        relevant = [
            t
            for t in transfers
            if t["holding_id"] == holding["holding_id"]
            and t["id"] != fields.get("transfer_id")
            and date.fromisoformat(t["date"]) <= proposal_date
        ]
        completed = [t for t in relevant if t["status"] == "completed"]
        remaining = number(holding["area"]) - sum(
            (number(t["area"]) for t in completed), Decimal(0)
        )
        if number(fields["area"]) > remaining:
            add(
                "EXCESS_AREA",
                {
                    "proposed_area": str(number(fields["area"])),
                    "remaining_area": str(remaining),
                    "original_area": holding["area"],
                    "completed_area": str(number(holding["area"]) - remaining),
                },
            )
        pending = [t for t in relevant if t["status"] == "pending"]
        overlap = [
            t
            for t in relevant
            if t["status"] != "cancelled" and t.get("overlap_reference")
        ]
        overcommit = (
            number(fields["area"])
            + sum((number(t["area"]) for t in pending), Decimal(0))
            > remaining
        )
        if overlap or pending and overcommit:
            add(
                "OVERLAPPING_TRANSFER",
                {
                    "transfer_ids": [t["id"] for t in (overlap or pending)],
                    "pending_area": str(
                        sum((number(t["area"]) for t in pending), Decimal(0))
                    ),
                    "remaining_area": str(remaining),
                },
                list(
                    dict.fromkeys(
                        sources + [t["document_id"] for t in (overlap or pending)]
                    )
                ),
            )
    outcome = (
        "conflict"
        if any(f["priority"] == "conflict" for f in findings)
        else "insufficient" if findings else "clear"
    )
    return outcome, findings
