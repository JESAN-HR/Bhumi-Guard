import hashlib, json
from decimal import Decimal
from sqlalchemy import select
from .models import *
from .db import ROOT
from .fixtures import scenarios
from .rules import analyze, number

WATERMARK = "DEMO — FICTIONAL DATA — NOT AN OFFICIAL DOCUMENT"


def serialize(obj):
    result = {}
    for c in obj.__table__.columns:
        v = getattr(obj, c.name)
        if isinstance(v, datetime):
            v = v.replace(tzinfo=timezone.utc).isoformat()
        if isinstance(v, Decimal):
            v = str(v)
        result[c.name] = v
    return result


def audit(db, case, user, event, details=None):
    db.add(
        AuditEvent(
            case_id=case.id, actor_id=user.id, event=event, details=details or {}
        )
    )


def create_document(db, case, label, lines):
    # Simple synthetic exhibit, deliberately not an official deed replica.
    import html, textwrap

    docid = uid()
    path = ROOT / "runtime" / f"{docid}.svg"
    texts = [
        WATERMARK,
        "BHUMIGUARD / SYNTHETIC EXHIBIT",
        label,
        "No official identifiers. All persons and transactions are fictional.",
    ] + [part for line in lines for part in textwrap.wrap(line, 72)]
    svg = '<svg xmlns="http://www.w3.org/2000/svg" width="800" height="1120" viewBox="0 0 800 1120"><rect width="800" height="1120" fill="#fffdf6"/><rect x="30" y="25" width="740" height="65" fill="#e2efed"/>'
    for n, t in enumerate(texts):
        svg += f'<text x="48" y="{62+n*30}" font-family="sans-serif" font-size="{14 if n==0 else 16}" fill="#163b48">{html.escape(str(t))}</text>'
    svg += '<text x="48" y="1070" font-family="sans-serif" font-size="13">DEMO — FICTIONAL DATA — NOT AN OFFICIAL DOCUMENT</text></svg>'
    path.write_text(svg, encoding="utf-8")
    d = Document(
        id=docid,
        case_id=case.id,
        label=label,
        path=str(path),
        media_type="image/svg+xml",
        sha256=hashlib.sha256(svg.encode()).hexdigest(),
        evidence={"page": 1, "text": texts},
    )
    db.add(d)
    db.flush()
    return d


def new_case(db, user, scenario_id, mouza_id):
    spec = next((s for s in scenarios() if s["id"] == scenario_id), None)
    if scenario_id and not spec:
        raise ValueError("scenario_not_found")
    fields = (
        spec["fields"]
        if spec
        else dict(
            seller_id=None,
            holding_id=None,
            mouza_id=mouza_id,
            survey=None,
            dag=None,
            area=None,
            date=None,
            unit="decimal",
        )
    )
    fields["mouza_id"] = mouza_id
    case = ReviewCase(
        owner_id=user.id,
        scenario_id=scenario_id,
        title=(
            spec["title"]
            if spec
            else {"en": "Manual document review", "bn": "ম্যানুয়াল নথি পর্যালোচনা"}
        ),
        mouza_id=mouza_id,
        fields=fields,
    )
    db.add(case)
    db.flush()
    if spec:
        proposal = create_document(
            db, case, "DEMO PROPOSED TRANSFER", [f"{k}: {v}" for k, v in fields.items()]
        )
        h = spec["holding"]
        h["mouza_id"] = mouza_id
        records = create_document(
            db,
            case,
            "DEMO HOLDING / MUTATION / HISTORY",
            [f"{k}: {v}" for k, v in h.items()]
            + ["mutation: " + str(spec["mutation"])]
            + [
                f"{t['id']} {t['date']} {t['status']} area={t['area']} overlap={t['overlap_reference']}"
                for t in spec["transfers"]
            ],
        )
        p = Parcel(mouza_id=mouza_id, survey=h["survey"], dag=h["dag"])
        db.add(p)
        db.flush()
        holding = Holding(
            case_id=case.id,
            parcel_id=p.id,
            party_id=h["party_id"],
            document_id=records.id,
            record_ref="DEMO-HOLDING",
            area=number(h["area"]),
            source_value=h["area"],
            history_complete=h["history_complete"],
            ambiguous=h["ambiguous"],
        )
        db.add(holding)
        db.flush()
        for t in spec["transfers"]:
            db.add(
                Transfer(
                    holding_id=holding.id,
                    document_id=records.id,
                    area=number(t["area"]),
                    date=t["date"],
                    status=t["status"],
                    overlap_reference=t["overlap_reference"],
                )
            )
        if spec["mutation"]:
            db.add(
                Mutation(
                    holding_id=holding.id,
                    document_id=records.id,
                    party_id=spec["mutation"]["party_id"],
                    area=number(spec["mutation"]["area"]),
                )
            )
        db.add(
            ExtractionRun(
                case_id=case.id,
                document_id=proposal.id,
                provider="seeded_fixture",
                result={
                    "fields": fields,
                    "evidence": {"page": 1, "document_id": proposal.id},
                },
            )
        )
    else:
        db.add(
            ExtractionRun(
                case_id=case.id, provider="manual_entry", result={"fields": fields}
            )
        )
    audit(db, case, user, "created")
    db.commit()
    return case


def record_context(db, case):
    documents = [
        d.id for d in db.scalars(select(Document).where(Document.case_id == case.id))
    ]
    h = db.scalar(select(Holding).where(Holding.case_id == case.id))
    if not h:
        return None, [], None, documents
    p = db.get(Parcel, h.parcel_id)
    holding = dict(
        holding_id=h.record_ref,
        mouza_id=p.mouza_id,
        survey=p.survey,
        dag=p.dag,
        party_id=h.party_id,
        area=str(h.area),
        history_complete=h.history_complete,
        ambiguous=h.ambiguous,
    )
    transfers = [
        serialize(t) | {"holding_id": h.record_ref}
        for t in db.scalars(
            select(Transfer).where(Transfer.holding_id == h.id).order_by(Transfer.date)
        )
    ]
    mutation = db.scalar(select(Mutation).where(Mutation.holding_id == h.id))
    refs = [h.document_id] + ([mutation.document_id] if mutation else [])
    refs += documents
    return (
        holding,
        transfers,
        serialize(mutation) if mutation else None,
        list(dict.fromkeys(refs)),
    )


def run_analysis(db, case, user):
    h, ts, m, refs = record_context(db, case)
    outcome, findings = analyze(case.fields, h, ts, m, refs)
    run = AnalysisRun(
        case_id=case.id,
        version=case.version,
        outcome=outcome,
        snapshot={
            "fields": case.fields,
            "holding": h,
            "transfers": ts,
            "mutation": m,
            "rule_version": "1.0",
        },
    )
    db.add(run)
    db.flush()
    for f in findings:
        db.add(Finding(analysis_id=run.id, **f))
    case.status = "analyzed"
    audit(db, case, user, "analyzed", {"analysis_id": run.id, "version": case.version})
    db.commit()
    return run


def detail(db, case):
    result = serialize(case)
    result["documents"] = [
        {k: v for k, v in serialize(d).items() if k != "path"}
        for d in db.scalars(select(Document).where(Document.case_id == case.id))
    ]
    for key, model in [
        ("extractions", ExtractionRun),
        ("corrections", Correction),
        ("decisions", Decision),
        ("audit", AuditEvent),
    ]:
        result[key] = [
            serialize(x)
            for x in db.scalars(
                select(model).where(model.case_id == case.id).order_by(model.created_at)
            )
        ]
    result["analyses"] = []
    for r in db.scalars(
        select(AnalysisRun)
        .where(AnalysisRun.case_id == case.id)
        .order_by(AnalysisRun.created_at)
    ):
        result["analyses"].append(
            serialize(r)
            | {
                "stale": r.version != case.version,
                "findings": [
                    serialize(f)
                    for f in db.scalars(
                        select(Finding).where(Finding.analysis_id == r.id)
                    )
                ],
            }
        )
    h, ts, m, _ = record_context(db, case)
    result.update(holding=h, transfers=ts, mutation=m)
    return result
