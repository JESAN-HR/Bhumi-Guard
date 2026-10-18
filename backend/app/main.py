import hashlib, secrets, os, io
from datetime import timedelta
from pathlib import Path
from fastapi import (
    FastAPI,
    Depends,
    HTTPException,
    Request,
    Response,
    UploadFile,
    File,
    Form,
)
from fastapi.responses import FileResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy import select
from argon2 import PasswordHasher
from argon2.exceptions import VerificationError
from .db import Session, ROOT
from .models import *
from .schemas import Login, NewCase, Edit, ReviewDecision
from .services import detail, new_case, run_analysis, audit, serialize
from .fixtures import scenarios
from .extraction import OpenAIProvider
from .showcase import welcome

app = FastAPI(title="BhumiGuard demo API", version="0.1.0")


def db_session():
    with Session() as db:
        yield db


def error(code, status=400):
    raise HTTPException(status, code)


@app.exception_handler(RequestValidationError)
async def validation_error(request, exc):
    return JSONResponse(status_code=422, content={"detail": "validation_error"})


@app.middleware("http")
async def security(request, call_next):
    if request.method not in ("GET", "HEAD", "OPTIONS"):
        origin = request.headers.get("origin")
        allowed = os.getenv(
            "ALLOWED_ORIGINS",
            "http://127.0.0.1:5173,http://localhost:5173,http://127.0.0.1:8000,http://localhost:8000",
        ).split(",")
        if origin and origin not in allowed:
            return JSONResponse(status_code=403, content={"detail": "forbidden"})
        length = request.headers.get("content-length")
        if length and int(length) > 11 * 1024 * 1024:
            return JSONResponse(status_code=413, content={"detail": "file_too_large"})
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "same-origin"
    response.headers["Cache-Control"] = "no-store"
    return response


def current(request: Request, db=Depends(db_session)):
    token = request.cookies.get("bg_session", "")
    session = db.scalar(
        select(LoginSession).where(
            LoginSession.token_hash == hashlib.sha256(token.encode()).hexdigest()
        )
    )
    if not session or session.expires.replace(tzinfo=timezone.utc) < now():
        error("unauthorized", 401)
    if request.method not in ("GET", "HEAD") and not secrets.compare_digest(
        request.headers.get("x-csrf-token", ""), session.csrf
    ):
        error("forbidden", 403)
    return db.get(User, session.user_id), session


def owned(db, case_id, user, lock=False):
    query = select(ReviewCase).where(
        ReviewCase.id == case_id, ReviewCase.owner_id == user.id
    )
    if lock:
        query = query.with_for_update()
    case = db.scalar(query)
    if not case:
        error("not_found", 404)
    return case


@app.get("/api/health")
def health():
    return {"status": "ok", "demo": True}


@app.get("/api/welcome")
def welcome_info(db=Depends(db_session)):
    return welcome(db)


@app.post("/api/login")
def login(data: Login, response: Response, db=Depends(db_session)):
    user = db.scalar(select(User).where(User.username == data.username))
    try:
        if not user:
            error("invalid_credentials", 401)
        PasswordHasher().verify(user.password_hash, data.password)
    except VerificationError:
        error("invalid_credentials", 401)
    token = secrets.token_urlsafe(32)
    csrf = secrets.token_urlsafe(32)
    db.add(
        LoginSession(
            user_id=user.id,
            token_hash=hashlib.sha256(token.encode()).hexdigest(),
            csrf=csrf,
            expires=now() + timedelta(hours=8),
        )
    )
    db.commit()
    response.set_cookie(
        "bg_session",
        token,
        httponly=True,
        samesite="strict",
        secure=os.getenv("COOKIE_SECURE", "false") == "true",
        max_age=28800,
        path="/",
    )
    return {"username": user.username, "csrf": csrf}


@app.get("/api/me")
def me(auth=Depends(current)):
    return {"username": auth[0].username, "csrf": auth[1].csrf}


@app.post("/api/logout")
def logout(response: Response, auth=Depends(current), db=Depends(db_session)):
    db.delete(auth[1])
    db.commit()
    response.delete_cookie("bg_session")
    return {"ok": True}


@app.get("/api/locations")
def locations(
    kind: str | None = None,
    parent_id: str | None = None,
    auth=Depends(current),
    db=Depends(db_session),
):
    query = select(Location)
    if kind is not None:
        if kind not in ("district", "upazila", "mouza"):
            raise HTTPException(422, "error")
        query = query.where(Location.kind == kind)
    if parent_id is not None:
        query = query.where(Location.parent_id == parent_id)
    return [serialize(l) for l in db.scalars(query)]


@app.get("/api/scenarios")
def demo_scenarios(auth=Depends(current)):
    return [
        {"id": s["id"], "title": s["title"], "mouza_id": s["fields"]["mouza_id"]}
        for s in scenarios()
    ]


@app.get("/api/cases")
def cases(auth=Depends(current), db=Depends(db_session)):
    rows = list(
        db.scalars(
            select(ReviewCase)
            .where(ReviewCase.owner_id == auth[0].id)
            .order_by(ReviewCase.created_at.desc())
        )
    )
    return [serialize(c) for c in rows]


@app.post("/api/cases")
def create(data: NewCase, auth=Depends(current), db=Depends(db_session)):
    if not data.fictional:
        error("fictional_required")
    loc = db.get(Location, data.mouza_id)
    if not loc or loc.kind != "mouza":
        error("invalid_location")
    try:
        case = new_case(db, auth[0], data.scenario_id, data.mouza_id)
    except ValueError as e:
        error(str(e))
    return detail(db, case)


@app.get("/api/cases/{case_id}")
def get_case(case_id: str, auth=Depends(current), db=Depends(db_session)):
    return detail(db, owned(db, case_id, auth[0]))


@app.get("/api/cases/{case_id}/history")
def case_history(case_id: str, auth=Depends(current), db=Depends(db_session)):
    data = detail(db, owned(db, case_id, auth[0]))
    return {
        k: data[k]
        for k in ("analyses", "decisions", "corrections", "extractions", "audit")
    }


@app.get("/api/cases/{case_id}/findings")
def case_findings(case_id: str, auth=Depends(current), db=Depends(db_session)):
    data = detail(db, owned(db, case_id, auth[0]))
    return data["analyses"][-1] if data["analyses"] else None


@app.put("/api/cases/{case_id}/fields")
def correct(case_id: str, data: Edit, auth=Depends(current), db=Depends(db_session)):
    case = owned(db, case_id, auth[0], True)
    if data.version != case.version:
        error("version_conflict", 409)
    fields = data.fields.model_dump()
    if fields["mouza_id"] != case.mouza_id:
        error("invalid_location")
    if data.confirmed and any(
        fields.get(k) in (None, "")
        for k in ("seller_id", "holding_id", "dag", "survey", "area", "date")
    ):
        error("critical_unresolved")
    db.add(
        Correction(
            case_id=case.id,
            user_id=auth[0].id,
            before=case.fields,
            after=fields,
            version=case.version + 1,
        )
    )
    case.fields = fields
    case.version += 1
    case.confirmed = data.confirmed
    case.status = "confirmed" if data.confirmed else "draft"
    audit(
        db,
        case,
        auth[0],
        "fields_corrected",
        {"version": case.version, "confirmed": case.confirmed},
    )
    db.commit()
    return detail(db, case)


@app.post("/api/cases/{case_id}/analyze")
def analyze_case(case_id: str, auth=Depends(current), db=Depends(db_session)):
    case = owned(db, case_id, auth[0], True)
    if not case.confirmed:
        error("critical_unresolved", 409)
    run_analysis(db, case, auth[0])
    return detail(db, case)


@app.post("/api/cases/{case_id}/decisions")
def decide(
    case_id: str, data: ReviewDecision, auth=Depends(current), db=Depends(db_session)
):
    case = owned(db, case_id, auth[0], True)
    latest = db.scalar(
        select(AnalysisRun)
        .where(AnalysisRun.case_id == case.id)
        .order_by(AnalysisRun.created_at.desc())
    )
    if (
        not case.confirmed
        or not latest
        or latest.id != data.analysis_id
        or latest.version != case.version
    ):
        error("stale_analysis", 409)
    if not data.notes.strip() or len(data.notes.strip()) < 5:
        error("validation_error")
    db.add(
        Decision(
            case_id=case.id,
            analysis_id=latest.id,
            reviewer_id=auth[0].id,
            action=data.action,
            notes=data.notes.strip(),
        )
    )
    case.status = data.action
    audit(
        db,
        case,
        auth[0],
        "decision_saved",
        {"analysis_id": latest.id, "action": data.action},
    )
    db.commit()
    return detail(db, case)


@app.post("/api/cases/{case_id}/documents")
async def upload(
    case_id: str,
    file: UploadFile = File(...),
    fictional: bool = Form(...),
    auth=Depends(current),
    db=Depends(db_session),
):
    case = owned(db, case_id, auth[0], True)
    if not fictional:
        error("fictional_required")
    data = await file.read(10 * 1024 * 1024 + 1)
    if len(data) > 10 * 1024 * 1024:
        error("file_too_large", 413)
    media = file.content_type
    if media not in ("application/pdf", "image/png", "image/jpeg"):
        error("invalid_file")
    try:
        if media == "application/pdf":
            from pypdf import PdfReader

            if not data.startswith(b"%PDF-"):
                raise ValueError()
            pdf = PdfReader(io.BytesIO(data))
            if pdf.is_encrypted or not 1 <= len(pdf.pages) <= 10:
                raise ValueError()
        else:
            from PIL import Image

            with Image.open(io.BytesIO(data)) as im:
                if im.format not in ("PNG", "JPEG") or im.width * im.height > 20000000:
                    raise ValueError()
                im.verify()
    except Exception:
        error("invalid_file")
    docid = uid()
    suffix = {"application/pdf": ".pdf", "image/png": ".png", "image/jpeg": ".jpg"}[
        media
    ]
    path = ROOT / "runtime" / (docid + suffix)
    path.write_bytes(data)
    db.add(
        Document(
            id=docid,
            case_id=case.id,
            label="DEMO UPLOAD",
            path=str(path),
            media_type=media,
            sha256=hashlib.sha256(data).hexdigest(),
            evidence={"fictional_attested": True},
        )
    )
    case.version += 1
    case.confirmed = False
    case.status = "draft"
    audit(db, case, auth[0], "document_uploaded", {"document_id": docid})
    db.commit()
    return detail(db, case)


@app.get("/api/documents/{doc_id}")
def document(doc_id: str, auth=Depends(current), db=Depends(db_session)):
    doc = db.get(Document, doc_id)
    if not doc:
        error("not_found", 404)
    owned(db, doc.case_id, auth[0])
    return FileResponse(
        doc.path,
        media_type=doc.media_type,
        headers={
            "Content-Security-Policy": "sandbox; default-src 'none'; style-src 'unsafe-inline'"
        },
    )


@app.post("/api/documents/{doc_id}/extract")
def extract(doc_id: str, auth=Depends(current), db=Depends(db_session)):
    doc = db.get(Document, doc_id)
    if not doc:
        error("not_found", 404)
    case = owned(db, doc.case_id, auth[0], True)
    if doc.media_type not in ("application/pdf", "image/png", "image/jpeg"):
        error("fixture_only")
    try:
        result = OpenAIProvider().extract(
            Path(doc.path).read_bytes(), doc.media_type, case.mouza_id
        )
    except Exception:
        audit(db, case, auth[0], "extraction_failed")
        db.commit()
        error("extraction_unavailable", 503)
    if result.fields.mouza_id != case.mouza_id:
        error("invalid_location")
    db.add(
        ExtractionRun(
            case_id=case.id,
            document_id=doc.id,
            provider="live_vision",
            result=result.model_dump(),
        )
    )
    case.fields = result.fields.model_dump()
    case.version += 1
    case.confirmed = False
    case.status = "draft"
    audit(db, case, auth[0], "extracted", {"document_id": doc.id})
    db.commit()
    return detail(db, case)


# A built frontend can be served by the same origin without Node at runtime.
if (ROOT / "frontend" / "dist").exists():
    from fastapi.staticfiles import StaticFiles

    app.mount(
        "/",
        StaticFiles(directory=ROOT / "frontend" / "dist", html=True),
        name="frontend",
    )
