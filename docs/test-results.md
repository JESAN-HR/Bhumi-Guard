# Actual validation results — 18 October 2026

Environment: Windows, Python 3.12.14, Node 24.19.0, installed Chrome 155; SQLite development database. These results are local and synthetic.

| Check | Observed result |
|---|---|
| Alembic initial upgrade | Passed against SQLite; application seeded successfully |
| Backend pytest | 49 passed, 0 failed in 6.65 s |
| TypeScript `tsc -b` | Passed |
| Vite production build | Passed, 63 transformed modules; final Vite phase 1.57 s |
| Frozen pnpm install | Passed with existing lockfile; esbuild postinstall succeeded |
| Chrome Playwright | 6 passed, 0 failed in 15.5 s; welcome/login, English/Bangla workflows, geography, delayed login/API failure/mobile and upload/manual/print tests |
| Synthetic rule evaluation | 22/22 exact expected-code matches; 1.547 ms measured for one local loop |
| Reference import | 556 rows added to existing six; 64 districts, 495 upazilas, 3 mouzas; existing cases retained |
| Import tests | Duplicate/invalid/unverified inputs rejected; idempotence, identity preservation and filtered location API tested |
| PDF samples | 3 generated, rendered by Poppler and visually inspected |
| API authorization | Tested unauthenticated, cross-reviewer case/document denial and CSRF rejection |
| Correction/history | Tested preserved original extraction, stale previous analysis, obsolete-decision rejection and persisted fresh decision |
| Missing API credentials | Tested backend and browser; upload persists and manual entry remains available |
| PostgreSQL/Compose execution | NOT RUN â€” Docker/PostgreSQL executables unavailable |
| Live model extraction | NOT RUN â€” no API credentials supplied; no paid requests made |

The Python test client emits one Starlette deprecation warning recommending `httpx2`; tests still pass with the installed compatible httpx client. Poppler emits missing optional Symbol/ArialUnicode font warnings; rendered samples were visually inspected and their text/watermarks are legible.

Browser tests assert language changes preserve unsaved Bangla numeric input, conflict â†’ correction â†’ fresh clear outcome, stale-state notice, supporting source visibility, decision persistence after page reload, audit history, API-failure field retention, no horizontal overflow at 390 px, fictional PDF preview, failed live extraction with manual fallback, insufficient-information findings and both language sections in print media.

Initial browser failures were test-selector ambiguity (two New review buttons), a select-label locator mismatch, and an expected audit count of seven where six actions occurred. Tests were corrected to target the intended control and assert the actual six-event workflow. No passing results are inferred from those failed attempts.

Screenshots and Playwright JSON are generated under ignored `frontend/test-results/`. Rule evaluation details are tracked in `docs/rule-evaluation.json`. Browser tests intentionally add fictional cases; dashboard counts are queried from the database, not reset to fabricated fixed values.

## Acceptance assessment

Welcome update: verified Bangla-first notice, language switching, displayed local credentials, acknowledgment leading to a successful login, tab-local persistence and reopening the notice on mobile. The desktop glass page screenshot was visually inspected. An initial browser failure exposed a preexisting mobile CSS rule hiding header actions; it was fixed and the final suite passed. Backend tests verify account ID preservation, password hashing, old-session revocation and suppression of credential disclosure outside local mode or after a password change.

Expansion validation on 18 October: all 64 district options and Chattogram's 15 imported upazilas were checked in Chrome. Missing mouzas display an explicit explanation in both languages; creation stays disabled without a mouza and changing language retains selections. The coverage screenshot was visually inspected. The reference importer added 556 rows to the existing six without resetting accounts or cases.

The new browser test initially had two selector errors (login arrow text and select label matching), which were corrected. A subsequent run exposed a real login race: navigation could become available before reference loading finished, then a delayed dashboard transition overwrote New review. The UI now finishes loading before publishing the authenticated state; a delayed catalog response is included in regression coverage. Final results above are from the successful rerun. The build required approved access after a sandbox ancestor-directory read denial.

National mouza completeness remains unmet: only three verified mouzas are imported. The 495-upazila snapshot has a documented discrepancy with a newer portal header saying 500. Import validation and counts do not resolve that reference gap.

The local seeded vertical slice, persistence, bilingual UI, verified limited geography, fictional labeling, correct conflict/clear/incomplete behavior, evidence links, stale-analysis enforcement, saved decisions, credential-free operation, and browser exercise have been demonstrated.

The full requested acceptance is **not yet claimed**: PostgreSQL/Compose has not been executed here. Live extraction is an optional unverified integration. Manual uploads do not yet have a UI for importing independent structured holdings/history; they honestly report missing records. Pre-analysis information requests for unreadable identifiers are not implemented. See `limitations.md` for exact next steps.

Synthetic rule agreement and elapsed time are not evidence of nationwide detection accuracy, real-world fraud recall, or model extraction performance. The evaluator was not a load test or independent held-out benchmark.
