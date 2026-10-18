# Architecture and data model

One browser application, one Python service, one database. The browser never receives an API key. It requests JSON over same-origin `/api`; the production Vite build is served by FastAPI. Development Vite proxies that prefix to the Python service. PostgreSQL is the Compose database; SQLite is the locally tested fallback.

## Follow the code

1. `fixtures.py`: 22 readable fictional scenarios and expected rule codes.
2. `seed.py`: validate/import the separate geography dataset, create fictional parties, create a hashed local reviewer account, seed each scenario once per reviewer.
3. `models.py`: relational storage with explicit foreign keys, NUMERIC(18,6), JSON snapshots and UTC timestamps.
4. `schemas.py`: bounded input fields, dates, decimal/shotok unit and Bangla/English digit handling.
5. `rules.py`: pure deterministic checks; no database, model or HTTP access.
6. `services.py`: build a case's supplied-record context, preserve snapshots/findings, create watermarked evidence, serialize history.
7. `main.py`: authentication, authorization, validation, transitions and routes.
8. `extraction.py`: replaceable provider interface and optional OpenAI vision implementation.
9. `frontend/src/i18n.ts`: parallel Bangla/English dictionaries; proper geographic names come from stored data.
10. `frontend/src/main.tsx`: dashboard → document confirmation → analysis → decision/history. Language changes do not recreate form state.

## Relational entities

`locations` self-reference parents and retain provenance. `parties` contain synthetic labels. `parcels` specify mouza + survey + dag. `holdings` link one explicit party interest to a parcel and source document. `transfers` and `mutation_records` link to that holding and their source documents. Each demo case has its own supplied record set; records are not a master government register.

`review_cases` belong to a reviewer. `source_documents`, `extraction_runs`, `field_corrections`, `analysis_runs`, `review_decisions` and `audit_events` belong to a case. `findings` belong to an analysis. `users` and `sessions` implement local reviewer authentication.

Original area text and source unit are retained; calculation values are Python Decimal and PostgreSQL NUMERIC. Only decimal/shotok is supported. SQLite's NUMERIC storage is a development limitation and should not be treated as proof of PostgreSQL decimal persistence. The original extraction is immutable through application APIs; edits append corrections. Analysis stores a record snapshot and rule version 1.0. Previous results are retained.

## Workflow integrity

Saving fields increments the case version, records before/after values, and optionally confirms all six critical fields. Empty seller/holding/dag/survey/area/date cannot be confirmed. Analysis requires confirmation. New uploads and live extraction increment the version and remove confirmation. A decision must reference the newest analysis for the current version and include an explanation. PostgreSQL mutations acquire a case row lock; edits also require the caller's expected version. A review decision updates workflow status only, never ownership.

Unreadable cases must have critical fields resolved from evidence before analysis or decision; the prototype does not record a pre-analysis information request. This is an explicit current limitation.

## API map

| Route | Purpose |
|---|---|
| POST `/api/login`, GET `/api/me`, POST `/api/logout` | Local session lifecycle |
| GET `/api/locations`, `/api/scenarios` | Supported geography and fictional launchers |
| GET/POST `/api/cases` | Reviewer-owned queue / create a scenario or manual review |
| GET `/api/cases/{id}` | Case, documents, record context, extraction/correction/analysis/decision/audit history |
| PUT `/api/cases/{id}/fields` | `{fields, confirmed, version}`; original numeric text retained |
| POST `/api/cases/{id}/documents` | Multipart `file` and `fictional=true` |
| GET `/api/documents/{id}` | Authorized original document bytes |
| POST `/api/documents/{id}/extract` | Explicit third-party extraction initiation |
| POST `/api/cases/{id}/analyze` | Confirmation-gated deterministic analysis |
| GET `/api/cases/{id}/findings` | Latest run and its findings/staleness |
| POST `/api/cases/{id}/decisions` | `{analysis_id, action, notes}`; action `reviewed` or `more_information` |
| GET `/api/cases/{id}/history` | Preserved runs, corrections, decisions and audit |

Errors return a stable `detail` code translated by the UI. The generated OpenAPI document specifies request schemas; case responses are aggregate JSON objects documented above. Runtime interactive docs are at `/docs`. No deletion or audit-rewrite endpoints are exposed.

## Security boundary

Argon2 hashes passwords. Session cookies contain random secrets; only SHA-256 token hashes are stored. Sessions expire after eight hours, are HttpOnly and SameSite Strict. CSRF tokens are required for authenticated mutations; browser Origin is checked against an explicit list. Cookie Secure is configurable and false only for local HTTP. No permissive CORS middleware is installed. All case/document/extraction routes enforce reviewer ownership; unauthorized objects return 404.

Uploads use server-generated filenames, validated MIME/content, image pixel limits, PDF page limits and a controlled authenticated route. SVG uploads are rejected; only application-generated escaped SVG is served. Duplicate files are not classified as fraud. Document responses have nosniff and sandbox CSP headers. Production would need malware scanning, reverse-proxy request limits, TLS, login throttling and operational security review. The prototype is loopback-bound.

Audit events are append-only **through application APIs**, not tamper-proof against database or filesystem administrators. Local generated credentials live in an ignored file for the user's development convenience, not in committed code. Avoid using the sample `.env` placeholders as real credentials.

## Extraction

Only `/extract` invokes the provider. Uploading does not. The provider gets the selected fictional file, not other cases or histories. A strict JSON schema and a second Pydantic check reject unexpected or invalid fields. Evidence page/text is retained in the extraction run when provided. Human confirmation is always required. No model confidence is displayed or used by rules.

Timeout 45 seconds, zero retries, output cap 1,800 tokens; 10 MB, 10 PDF pages, 20M image pixels. Document instructions are explicitly untrusted; the API call supplies no tools. Location remains the user's selected internal ID. No name-based party resolution or automatic history synthesis occurs. API errors return a translated manual-fallback message and an audit event. Live accuracy/latency remain unmeasured.

References consulted: [FastAPI security](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/), [Vite setup](https://vite.dev/guide/), [OpenAI file inputs](https://developers.openai.com/api/docs/guides/file-inputs), [OpenAI structured outputs](https://developers.openai.com/api/docs/guides/structured-outputs).
