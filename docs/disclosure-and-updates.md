# AI/tool disclosure

Codex generated and edited application code, translations, tests, documentation and synthetic data. Shell tools ran dependency installation, migrations, seeding, pytest, TypeScript/Vite builds and Playwright. Browser screenshots were inspected for desktop/Bangla/mobile rendering. ReportLab generated three fictional PDFs; Poppler rendered them for visual verification.

Prettier and Black formatted the source for readability. They are development tools, not runtime AI services. A repeat seed run preserved the database case count (37 before and after).

A bounded research subagent manually checked public authoritative geography references and wrote the provenance dataset. Web research also checked official Vite, FastAPI and OpenAI API documentation. No government website was scraped or bulk-downloaded. No real personal identifiers or real ownership records were used.

The Sites skill supplied local implementation/preview guidance. The PDF skill supplied document rendering/verification guidance. OpenAI Docs guidance informed the optional extraction adapter. No hosting connector, public deployment, blockchain, custom training, vector store or ornamental agents are part of the application.

The application's seeded extraction results are fixtures, clearly labeled. The optional model adapter has not been invoked with a live credential. Findings and explanations are deterministic; no generative output changes rule outcomes. Bangla translations were authored during implementation and should receive participant/domain-language review before submission.

# Update log

## 2026-10-18 — Beginner local setup guides

- Added separate Ubuntu and Windows guides with prerequisite installation, fresh-source transfer, SQLite setup, demo-login configuration, build/run steps, daily restart, backup and troubleshooting.
- Distinguished first-time internet requirements from offline operation, and fresh synthetic seeding from migrating existing review data with absolute document paths.
- Linked both guides prominently from README. Checked commands against existing scripts and official installer documentation; no Ubuntu execution or fresh-machine installation is claimed.

## 2026-10-18 — Glass welcome notice

- Added a bilingual glass-style welcome page before login, once per tab, with acknowledgment and a reopen action.
- Added editable team/contest/creator metadata and validated GitHub links. The team supplied DIU Jex Stone, MD Habibur Rahman Jesan (Jesan-hr), and MD. Touhidul Islam Raha (raha-66); names are preserved as supplied in both interfaces.
- Renamed the existing local reviewer to the requested demo account, preserving case ownership and revoking old sessions. Public demo credentials are served from ignored local configuration only; production mode suppresses them.
- Added tests for the welcome/login flow, responsive layout, account identity preservation, session revocation, production suppression and stale credential suppression.

## 2026-10-18 — Reference expansion and student handover

- Expanded to 64 districts and 495 upazilas from manually curated official directory references, retaining three verified mouzas and existing location IDs.
- Documented snapshot count disagreement, duplicate Shaistaganj handling and Jiyanagar renaming notice. No nationwide mouza completeness claim.
- Added transactional reference import/dry-run/report, hierarchy/provenance checks and identity-collision protection; existing cases retained.
- Replaced fixed UI counts/district labels; added bilingual missing-mouza notices and prevented empty-location submissions. Added optional parent/kind API filters.
- Wrote dataset card and student run/code/customization guide, including hackathon preparation and changed-problem workflow.
- Added import regression tests and a bilingual browser coverage test. Updated actual results in `test-results.md`.
- Fixed a login/loading navigation race exposed by browser tests; added delayed-reference response coverage. Final result: 48 backend tests and 5 browser tests pass.

## 2026-10-17 — Initial local vertical slice

- Inspected an empty Windows workspace; located bundled Python/Node/Git runtimes.
- Built relational storage, migrations, verified geography import and 22 fictional labeled scenarios.
- Implemented Decimal checking engine, confirmation/version integrity, reviewer authentication and owner authorization.
- Connected bilingual dashboard, viewer, corrections, findings, evidence, decisions/history and print view.
- Added controlled uploads, strict-schema optional vision adapter and tested missing-key manual fallback.
- Generated and visually reviewed three watermarked sample PDFs.
- Ran backend and Chrome browser tests; corrected ambiguous test selectors and audit-event expected count.
- Added Docker/PostgreSQL setup and documented the host's unverified Docker/PostgreSQL and live-provider integrations.

See `test-results.md` for exact current measured results. No fabricated commits, deployments or benchmarks are recorded.
