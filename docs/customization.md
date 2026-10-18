# Student guide: understand, run and change BhumiGuard

## What a hackathon is

A hackathon is a time-limited event where a team builds and demonstrates a solution to a specified problem. The organizer's rules determine the deadline, permitted tools, team size and judging criteria. A credible demonstration explains the user's problem, shows a working end-to-end flow, supplies evidence of testing, and states limitations. A large feature list is less useful than a workflow the team can explain and reliably demonstrate.

For this project, explain: **an officer compares fictional supplied land records, corrects extraction, inspects deterministic findings, and records a review**. It does not prove criminal fraud or certify ownership. Ask organizers whether a changed problem is still within P3 before reshaping the submission.

## How the code works

1. `frontend/src/main.tsx` renders the dashboard, new review, document fields, findings and history. Its `api()` helper calls `/api/...` and attaches the session's CSRF token. React state preserves fields while the language changes.
2. `frontend/src/i18n.ts` holds the two interface dictionaries. Geographic names are already stored in both languages. Documents and user notes remain original.
3. `backend/app/main.py` defines FastAPI routes, authentication, authorization and input boundaries. Every case/document request checks the reviewer. `/docs` describes accepted JSON and response schemas.
4. `backend/app/schemas.py` validates typed requests; `services.py` coordinates relational records, corrections, analysis versions, decisions and audit events. Changing fields invalidates an old analysis; decisions must use a current analysis.
5. `backend/app/rules.py` is the independent checking engine. It receives supplied record context, uses `Decimal`, and returns stable finding codes and bilingual templates. It does not call an AI or update ownership.
6. `backend/app/models.py` maps Python objects to database tables. `db.py` selects PostgreSQL from `DATABASE_URL` or the explicit local SQLite fallback. Alembic owns schema upgrades; do not edit a live database manually to make the UI work.
7. `backend/app/extraction.py` is the optional provider boundary. Only the explicit extraction action sends a fictional document. Responses require schema validation and human confirmation before checks run.
8. `backend/app/fixtures.py` creates synthetic scenarios; `seed.py` inserts them idempotently. `geography.py` independently validates and imports geographic references. Geographic coverage does not create any real holdings or transaction history.

Read in this order: README → `docs/rules.md` → `rules.py` → one case in `fixtures.py` → `services.py` → corresponding FastAPI route → frontend action. Follow the `correction` scenario to see why a first conflict can become a clean result after a documented correction and fresh analysis.

## Run and edit

Follow the README's setup commands first. On this existing Windows workspace:

```powershell
cd 'C:\Users\jesan\OneDrive\Desktop\Bumi Guard'
.\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

For frontend hot reload, open a second terminal, enter `frontend`, run `pnpm dev`, then visit http://127.0.0.1:5173. Node/pnpm must be on PATH; `docs/environment.md` lists the bundled paths for this machine. Port 8000 serves the last **built** frontend; after editing run `pnpm build` to update that view. Browser refresh alone does not compile source files.

The local password is in ignored `runtime/local-account.txt`. For a fresh installation, the seed command prompts for your own password. `.env` is read by Docker Compose; direct Python commands use shell environment variables. Keep the same `DATABASE_URL` for migrations, importing, seeding and serving. Do not reset to fix a login or missing-location issue: reset deletes saved cases.

## Where to customize

| Requested change | Edit | Verify |
|---|---|---|
| Wording, Bangla/English labels | `frontend/src/i18n.ts` | Both languages, no missing keys |
| Colors, spacing, responsive layout | `frontend/src/style.css` | Keyboard focus, desktop and mobile |
| New synthetic demonstration | `backend/app/fixtures.py` | Add expected codes and run evaluator; seed exports JSON |
| New verified locations | `data/locations/locations.json`, then validated importer | Parent hierarchy, bilingual names, provenance, no invented codes |
| New inconsistency rule | `backend/app/rules.py` | Stable code, bilingual template, independent positive/negative tests |
| Different extraction provider | `backend/app/extraction.py` | Same validated output contract, explicit opt-in, failure fallback |
| New stored field/entity | `models.py`, `schemas.py`, service and a **new** Alembic revision | Upgrade existing data; validation and API tests |
| New review action | Service transition and route, then UI/dictionaries | Authorization, stale version rejection and history |

These are existing extension boundaries, not a claim of automatic adaptation to every new problem. There is no generic plugin framework. The React view still needs component extraction as it grows.

## If judges change the problem

Write a short acceptance example first: “Given these supplied records, when this reviewer does X, the system shows Y with evidence Z.” Identify what can be reused (login, uploads, confirmation, versioning, bilingual UI, evidence/history) and what needs a new domain model or rules. A change from excess area to missing-document review can reuse much of the flow; a problem about valuation or cadastral geometry needs different data and checks.

For example, to add a missing-required-document check: specify the required document types for that problem, add structured document-type data and validation, introduce a unique rule code plus both language templates, include present/missing/unreadable synthetic cases, then expose the finding through the existing analysis UI. Do not infer document type from a filename or silently make AI output a legal decision.

Make one change at a time on a Git branch. Preserve existing rule meanings and old analysis runs; use new codes/revisions for changed semantics. Run pytest, the synthetic evaluator, frontend build and browser workflow. Update dataset documentation, limitations and the demo script. For two participants, one can explain records/rules/tests and the other UI/extraction/workflow, but both should rehearse the complete case.

## Troubleshooting

- **Only old locations appear:** run the reference importer with `--apply` against the database used by the server, then refresh. Editing JSON alone does not update an existing database.
- **Empty mouza dropdown:** that upazila has no imported verified mouzas. Use Dhaka → Savar/Dhamrai for the current demo or add sourced references. Never substitute a union/village list.
- **UI changes not visible:** rebuild the frontend or use port 5173 for Vite hot reload.
- **Port already in use:** stop the previous project server in its terminal with Ctrl+C, then restart.
- **API unavailable:** confirm port 8000 is running and Vite's proxy points there. Manual entry does not require an AI key.
- **Can't analyze/decide:** resolve and confirm required fields; after editing, run a fresh analysis before recording a decision.
- **Different counts after tests:** browser tests intentionally create fictional cases. Dashboard counts come from the database.
