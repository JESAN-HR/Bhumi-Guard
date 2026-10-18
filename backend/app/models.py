from datetime import datetime, timezone
from uuid import uuid4
from decimal import Decimal
from sqlalchemy import (
    String,
    ForeignKey,
    Numeric,
    JSON,
    DateTime,
    Boolean,
    Integer,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column
from .db import Base


def uid():
    return str(uuid4())


def now():
    return datetime.now(timezone.utc)


class Identity:
    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=uid)


class User(Identity, Base):
    __tablename__ = "users"
    username: Mapped[str] = mapped_column(String(80), unique=True)
    password_hash: Mapped[str] = mapped_column(Text)


class LoginSession(Identity, Base):
    __tablename__ = "sessions"
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    token_hash: Mapped[str] = mapped_column(String(64), unique=True)
    csrf: Mapped[str] = mapped_column(String(80))
    expires: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class Location(Identity, Base):
    __tablename__ = "locations"
    parent_id: Mapped[str | None] = mapped_column(
        ForeignKey("locations.id"), nullable=True
    )
    kind: Mapped[str] = mapped_column(String(20))
    name_en: Mapped[str] = mapped_column(String(120))
    name_bn: Mapped[str] = mapped_column(String(120))
    provenance: Mapped[dict] = mapped_column(JSON)


class Party(Identity, Base):
    __tablename__ = "parties"
    label_en: Mapped[str] = mapped_column(String(120))
    label_bn: Mapped[str] = mapped_column(String(120))


class Parcel(Identity, Base):
    __tablename__ = "parcels"
    mouza_id: Mapped[str] = mapped_column(ForeignKey("locations.id"))
    survey: Mapped[str] = mapped_column(String(80))
    dag: Mapped[str] = mapped_column(String(80))


class ReviewCase(Identity, Base):
    __tablename__ = "review_cases"
    owner_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    scenario_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    title: Mapped[dict] = mapped_column(JSON)
    mouza_id: Mapped[str] = mapped_column(ForeignKey("locations.id"))
    fields: Mapped[dict] = mapped_column(JSON)
    confirmed: Mapped[bool] = mapped_column(Boolean, default=False)
    version: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[str] = mapped_column(String(30), default="draft")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Document(Identity, Base):
    __tablename__ = "source_documents"
    case_id: Mapped[str] = mapped_column(ForeignKey("review_cases.id"))
    label: Mapped[str] = mapped_column(String(120))
    path: Mapped[str] = mapped_column(Text)
    media_type: Mapped[str] = mapped_column(String(60))
    sha256: Mapped[str] = mapped_column(String(64))
    evidence: Mapped[dict] = mapped_column(JSON)


class Holding(Identity, Base):
    __tablename__ = "holdings"
    case_id: Mapped[str] = mapped_column(ForeignKey("review_cases.id"))
    parcel_id: Mapped[str] = mapped_column(ForeignKey("parcels.id"))
    party_id: Mapped[str] = mapped_column(ForeignKey("parties.id"))
    document_id: Mapped[str] = mapped_column(ForeignKey("source_documents.id"))
    record_ref: Mapped[str] = mapped_column(String(80))
    area: Mapped[Decimal] = mapped_column(Numeric(18, 6))
    source_value: Mapped[str] = mapped_column(String(80))
    source_unit: Mapped[str] = mapped_column(String(30), default="decimal")
    history_complete: Mapped[bool] = mapped_column(Boolean)
    ambiguous: Mapped[bool] = mapped_column(Boolean, default=False)


class Transfer(Identity, Base):
    __tablename__ = "transfers"
    holding_id: Mapped[str] = mapped_column(ForeignKey("holdings.id"))
    document_id: Mapped[str] = mapped_column(ForeignKey("source_documents.id"))
    area: Mapped[Decimal] = mapped_column(Numeric(18, 6))
    date: Mapped[str] = mapped_column(String(10))
    status: Mapped[str] = mapped_column(String(20))
    overlap_reference: Mapped[bool] = mapped_column(Boolean, default=False)


class Mutation(Identity, Base):
    __tablename__ = "mutation_records"
    holding_id: Mapped[str] = mapped_column(ForeignKey("holdings.id"))
    document_id: Mapped[str] = mapped_column(ForeignKey("source_documents.id"))
    party_id: Mapped[str] = mapped_column(ForeignKey("parties.id"))
    area: Mapped[Decimal] = mapped_column(Numeric(18, 6))


class ExtractionRun(Identity, Base):
    __tablename__ = "extraction_runs"
    case_id: Mapped[str] = mapped_column(ForeignKey("review_cases.id"))
    document_id: Mapped[str | None] = mapped_column(
        ForeignKey("source_documents.id"), nullable=True
    )
    provider: Mapped[str] = mapped_column(String(50))
    result: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Correction(Identity, Base):
    __tablename__ = "field_corrections"
    case_id: Mapped[str] = mapped_column(ForeignKey("review_cases.id"))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    before: Mapped[dict] = mapped_column(JSON)
    after: Mapped[dict] = mapped_column(JSON)
    version: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class AnalysisRun(Identity, Base):
    __tablename__ = "analysis_runs"
    case_id: Mapped[str] = mapped_column(ForeignKey("review_cases.id"))
    version: Mapped[int] = mapped_column(Integer)
    outcome: Mapped[str] = mapped_column(String(40))
    snapshot: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Finding(Identity, Base):
    __tablename__ = "findings"
    analysis_id: Mapped[str] = mapped_column(ForeignKey("analysis_runs.id"))
    code: Mapped[str] = mapped_column(String(40))
    priority: Mapped[str] = mapped_column(String(20))
    values: Mapped[dict] = mapped_column(JSON)
    sources: Mapped[list] = mapped_column(JSON)
    explanation: Mapped[dict] = mapped_column(JSON)
    action: Mapped[dict] = mapped_column(JSON)
    assumptions: Mapped[dict] = mapped_column(JSON)


class Decision(Identity, Base):
    __tablename__ = "review_decisions"
    case_id: Mapped[str] = mapped_column(ForeignKey("review_cases.id"))
    analysis_id: Mapped[str] = mapped_column(ForeignKey("analysis_runs.id"))
    reviewer_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    action: Mapped[str] = mapped_column(String(30))
    notes: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class AuditEvent(Identity, Base):
    __tablename__ = "audit_events"
    case_id: Mapped[str] = mapped_column(ForeignKey("review_cases.id"))
    actor_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    event: Mapped[str] = mapped_column(String(40))
    details: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
