# Dataset card

This project uses **geographic reference data and synthetic test fixtures**. It has no model-training dataset and no collection of real ownership records.

| Dataset | Type and purpose | Size / coverage | Limits |
|---|---|---|---|
| `data/locations/locations.json` | Manually curated public geographic names, hierarchy and provenance; populates location selectors | 64 districts, 495 upazilas from a dated directory, 3 Gazette-supported mouzas | Not a complete national mouza register; snapshot discrepancies remain |
| `data/locations/upazilas-curated.txt` | Readable manual transcription used by `scripts/expand_upazilas.py` | District-grouped bilingual upazila names; Jiyanagar added separately with notice provenance | English names are human transliterations; not certified government spellings |
| `backend/app/fixtures.py` → `data/scenarios/cases.json` | Synthetic labeled rule scenarios, created for repeatable demos and regression testing | 22 scenarios | Expected codes are authored with the implementation, not an independent real-world benchmark |
| `sample-documents/` | Watermarked fictional PDF exhibits for upload/viewer demonstrations | 3 samples | Not official forms, OCR ground truth or real deeds |
| `runtime/` (ignored) | Local database, generated source exhibits and user-uploaded fictional documents | Changes with use | Not distributed as a public dataset; includes local account information |

We use real geography to make the Bangladesh context understandable, and synthetic land records to avoid exposing personal information or suggesting that a real person committed fraud. Controlled scenarios let students test edge cases without obtaining confidential deeds. This choice limits external validity: passing the fixtures does not establish nationwide fraud-detection accuracy.

## Labels and creation

`fixtures.py` is the source of truth for synthetic cases. The seed exports its JSON representation, creates source documents and stores relational holdings, parcels, transfers and mutation records. Scenario labels are expected **finding codes**. Cases cover valid transfers, excess area, pending/cancelled/completed history, overlapping seller interests, mismatching fields, incomplete history, unreadable identifiers, digit normalization, corrections and uncertain survey identity. `scripts/evaluate.py` compares actual and expected code sets and records results in `docs/rule-evaluation.json`.

All parties, deeds, dag/khatians, interests, areas, dates and histories are invented and marked DEMO. Repeated dag values can occur across mouzas and surveys; they are not global identifiers. Real geographic names do not make any linked fictional ownership data real.

## Provenance and maintenance

Each location has an internal ID, type, parent, explicit English/Bangla names, verification status and source references. Each source records URL, retrieval date, title and verification evidence. No JL or official codes are populated. See `geography.md` for references, source conflicts and exact remaining gaps. No government website crawler or bulk download is used.

New imports must include ancestor rows and source provenance. Run the importer dry first, review its report, then apply. Duplicate IDs, unsupported parent relationships, unverified rows and silent changes to existing identities are rejected. Existing cases keep their IDs. Existing provenance is retained by the append-only importer; correcting an existing record or its provenance requires a reviewed migration rather than silently rewriting historical data.

Before accepting a future external dataset, check permission/licensing, publisher, date, geography level, missing districts, duplicate names/IDs, name changes, survey context and whether each purported mouza really is a mouza. Keep unverified candidates outside selectable data. Public accessibility alone does not establish unrestricted reuse rights; obtain organizer/domain review before broader redistribution or operational use.

## Evaluation separation

Rule evaluation uses structured fictional fields and expected codes. Browser tests assess workflow/persistence/languages. Neither measures extraction accuracy. Live vision extraction has not been benchmarked and no live paid call was made. A future extraction benchmark needs separate fictional documents, independently labeled fields, and field-level accuracy/latency reporting.
