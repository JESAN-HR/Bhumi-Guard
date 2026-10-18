# BhumiGuard / ভূমিগার্ড

LandTech 2026 · P3 — Catch Fraud & Double-Selling. A local, bilingual officer-review prototype that compares **supplied fictional records**, preserves evidence and corrections, and records review decisions. It does not certify ownership, determine criminal fraud, or approve registration/mutation.

**Demo data — location names are real; ownership and transaction records are entirely fictional.**

**ডেমো তথ্য — স্থানগুলোর নাম বাস্তব; মালিকানা ও লেনদেনের তথ্য সম্পূর্ণ কাল্পনিক।**

## First time running on your own laptop?

Use the guide for your operating system. Each starts with installing the tools, walks through a fresh local database and the `jesan / 12345` demo login, and includes daily start/stop instructions and troubleshooting.

- **[Ubuntu: complete beginner guide](docs/START-UBUNTU.md)** — Ubuntu 24.04 / Python 3.12, with exact Terminal commands.
- **[Windows: complete beginner guide](docs/START-WINDOWS.md)** — PowerShell, Python 3.12 and Node 24; includes the original development computer's path.

Both use SQLite for the local demo: no Docker, database server, hosting account or API key is needed. Installation requires internet; the installed seeded/manual workflow runs offline. Create a fresh environment on each OS. Do not copy Windows `.venv` or `node_modules` to Ubuntu. Moving saved databases between paths/OSes needs document-path migration; the guides explain this distinction.

## Current implementation

- React/TypeScript/Vite, Tailwind 4, i18next; Bangla by default, persistent language selection, locally bundled Noto Sans Bengali (OFL).
- FastAPI/Pydantic, SQLAlchemy relational models, Alembic migrations, PostgreSQL Compose configuration. SQLite is an explicit non-Docker development fallback, not a substitute claim of PostgreSQL validation.
- Authenticated, reviewer-owned cases; Argon2 password hashes; random, hashed server-side session tokens; HttpOnly/SameSite cookies; CSRF tokens and origin validation.
- Database-derived dashboard counts, search/status/mouza filters, cascading geography and 22 labeled synthetic scenarios.
- Source viewer, fictional PDF/image uploads, preserved extraction runs, editable fields, human confirmation, versioned analysis, evidence links, transaction timeline, decisions, audit events and bilingual print view.
- Six deterministic rule codes; Decimal arithmetic; incomplete evidence cannot result in a clean outcome. Corrections and new uploads invalidate previous analyses. Decisions never mutate holdings.
- Manual entry and explicitly labeled seeded fixtures work without an API key. The optional vision adapter is implemented but has **not** been tested against a live paid API.

**Validation status:** the local SQLite application runs and has been exercised in Chrome. Backend tests and browser tests pass; see [actual results](docs/test-results.md). Docker and PostgreSQL binaries were unavailable on the implementation host, so the Compose/PostgreSQL acceptance criterion remains **unverified**. This is not claimed as a fully accepted production or hackathon submission.

## Start here on this Windows workspace

The glass welcome notice appears once per browser tab before login. It shows the team/contest and intentionally public **local demo** credentials. Use **About this demo** to reopen it. This workspace's requested demo login is **jesan / 12345**; existing saved cases were preserved. These are public fictional-demo credentials, not production credentials.

Edit `data/showcase.json` to set the team, contest, creators and GitHub repository. Creators use `{"name":{"en":"Your name","bn":"আপনার নাম"},"github_url":"https://github.com/YOUR_HANDLE"}`. Empty creator details are honestly marked as pending. Only HTTPS `github.com` links become clickable. Content is fetched from the backend, so editing metadata does not require a frontend rebuild.

For another local installation, create a reviewer normally, then explicitly configure a displayed demo login:

```powershell
.\.venv\Scripts\python.exe -m scripts.configure_demo_login --previous reviewer --username jesan
# Enter the intended public demo password at the prompt.
```

This local-only command keeps the reviewer ID/cases, hashes the new password, revokes previous sessions, and saves intentionally public login details in ignored `runtime/showcase-login.json`. The welcome API does not expose credentials when `APP_ENV` is not `local`, or when they no longer match the account. Ordinary seed password requirements remain unchanged. Delete that local configuration file to stop displaying credentials. The notice acknowledgment is presentation state, not authentication or authorization.

The application is served at **http://127.0.0.1:8000** while the development process remains running. The current local demo login is also in ignored `runtime/local-account.txt`. The intentionally public demo login appears on the welcome notice; it is not added to case reports or bundled JavaScript. API keys and other secrets are never shown.

To restart using the existing environment:

```powershell
cd 'C:\Users\jesan\OneDrive\Desktop\Bumi Guard'
.\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

Or run `powershell -ExecutionPolicy Bypass -File scripts/start-local.ps1` after the initial setup. This script uses PATH Python or the available bundled runtime; it does not install system software.

## Reproducible Docker setup (PostgreSQL)

Requires Docker Engine/Desktop with Compose. Copy `.env.example` to `.env`; replace both password placeholders with your own values. Use a URL-safe alphanumeric database password because Compose embeds it in the connection URL. Do not reuse a real account password.

```sh
docker compose up --build
```

Open http://localhost:8000 and sign in with `DEMO_USERNAME` / `DEMO_PASSWORD` from `.env`. The container runs migrations and an idempotent seed before serving. PostgreSQL and documents have separate persistent named volumes. `docker compose down` retains them. Only loopback port 8000 is exposed; PostgreSQL is not published to the host.

Re-run migrations/seed explicitly:

```sh
docker compose exec app python -m alembic -c backend/alembic.ini upgrade head
docker compose exec app python -m backend.app.seed
```

## Fresh non-Docker setup

Requires Python 3.12+, Node 22.12+ (tested with Node 24), pnpm 11.25 and Chrome for browser tests. Python/Node are bundled on the current machine but are not on PATH. Use their full paths if necessary; see `docs/environment.md`.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend/requirements.lock
.\.venv\Scripts\python.exe -m alembic -c backend/alembic.ini upgrade head
.\.venv\Scripts\python.exe -m backend.app.seed --username reviewer
# Enter a new password of at least 12 characters at the hidden prompt.
cd frontend
pnpm install --frozen-lockfile
pnpm build
cd ..
.\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

On macOS/Linux replace `.venv\Scripts\python.exe` with `.venv/bin/python`. The default fallback database is `runtime/demo.db`; it persists across restarts. To use an existing local PostgreSQL database, set `DATABASE_URL=postgresql+psycopg://USER:PASSWORD@localhost:5432/DATABASE` **before** migration, seed and server commands. Shell environment variables are used by Python; `.env` is automatically read by Compose only.

For hot reload, run the backend with `--reload`, then `pnpm dev` in `frontend/`. Open http://127.0.0.1:5173; Vite proxies `/api` to port 8000. Avoid running two backend processes on the same port.

## Optional live extraction

Set server-side `OPENAI_API_KEY` and optionally `OPENAI_MODEL`, then restart the backend. Upload a fictional PDF/PNG/JPEG and explicitly click **Send document for live extraction**. This is the only action that sends a document to a third-party service. No call was made during implementation. Changing language, uploading, confirming fields or running rules does not call a model.

The adapter uses a strict JSON schema, validates with Pydantic, has a 45-second timeout, a 1,800-token output cap, and **zero automatic retries**. Files are limited to 10 MB; PDFs to 10 pages; images to 20 million pixels. Missing values stay unresolved. The model has no tools and cannot add land history or mutate holdings. Provider failures preserve the document and leave manual entry available. See [architecture and extraction limitations](docs/architecture.md).

## Tests

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m scripts.evaluate
# With the backend running and Chrome installed:
$env:DEMO_USERNAME = 'reviewer'
$env:DEMO_PASSWORD = 'your-local-password'
cd frontend
pnpm test:e2e
```

On this workspace, E2E tests can read the ignored generated `runtime/local-account.txt` instead of environment variables. Tests create additional fictional review cases; counts correctly reflect them. Backend tests use separate temporary databases. `frontend/test-results/` contains browser evidence and is ignored. Test runs do not use a live model.

## Data, samples and reset

- [Geographic provenance](docs/geography.md): **64 districts, 495 upazilas from a dated official directory, and 3 verified mouzas**. Upazila snapshot completeness is not guaranteed; nationwide mouzas are unavailable. Missing mouzas are explained in the UI. For complete demo cases use Dhaka → Savar → Birulia / Bara Kakar or Dhaka → Dhamrai → Uttar Paragao. No invented JL or official codes. English names are stored human transliterations.
- `data/locations/locations.json` is separate from `data/scenarios/cases.json`. The reference importer validates hierarchy and provenance, rejects unverified locations and protects existing IDs. It only adds reviewed entries; it does not scrape, guess or silently replace existing identities.
- `backend/app/fixtures.py` is the readable synthetic generator; its 22 labeled cases are exported to JSON by seeding. Every reference begins with DEMO or is an internal UUID.
- Three fictional PDF exhibits are in `sample-documents/`; regenerate with `python -m scripts.generate_samples`. Seeded case documents are simple watermarked SVG exhibits served only after authorization. No seals, official forms or parcel boundaries are used.
- Explicit destructive local reset: `python -m backend.app.seed --reset --confirm DELETE-FICTIONAL-DEMO`. Requires `APP_ENV=local`. This removes **all rows in the configured application database**, including reviewer accounts, and reseeds with the supplied username/password. Use only a dedicated demo database. Old document files are retained; automatic filesystem deletion is deliberately absent. No reset HTTP endpoint exists.

Update an **existing** database with the expanded reference data, without resetting accounts or cases:

```powershell
# Validate first; this rolls back and does not change the database.
.\.venv\Scripts\python.exe -m backend.app.geography data/locations/locations.json
# Apply the reviewed additions, preserving existing case references.
.\.venv\Scripts\python.exe -m backend.app.geography data/locations/locations.json --apply --report runtime/geography-import.json
```

Refresh the browser after import. On Docker use `docker compose exec app python -m backend.app.geography data/locations/locations.json --apply`. A fresh seed includes the expanded reference file automatically. Source provenance is bundled with the data; an import report does not prove nationwide completeness. Additional mouzas need an authoritative reference explicitly confirming mouza status and district/upazila parentage.

## Understand and customize the project

Start with the [student code, run and customization guide](docs/customization.md). It explains the request flow, where each feature lives, common startup problems, how two participants can prepare, what a hackathon is, and how to respond if judges give a new problem. The [dataset card](docs/dataset-card.md) explains what each dataset contains, why it is used, how labels are created, and what the results do **not** prove.

The reusable parts are authentication, upload/viewing, human confirmation, bilingual UI, evidence, versioning and history. Domain checks live separately in `backend/app/rules.py`, synthetic examples in `fixtures.py`, geographic import in `geography.py`, and the optional AI adapter in `extraction.py`. This keeps common changes localized; supporting an unrelated problem still requires explicit new data/rules and tests.

## Submission guide

- [Architecture, data model, security and API](docs/architecture.md)
- [Rule definitions and supported assumptions](docs/rules.md)
- [Actual tests and acceptance status](docs/test-results.md)
- [90-second demo script](docs/demo-script.md)
- [Known limitations and next priorities](docs/limitations.md)
- [AI/tool disclosure and update log](docs/disclosure-and-updates.md)
- Interactive API schemas: http://127.0.0.1:8000/docs; saved schema: `docs/openapi.json`.

Nothing has been publicly deployed. There is no blockchain, government-system integration, nationwide coverage or calibrated fraud probability.
