# Geographic reference provenance

Curated on **17–18 October 2026**. Imported scope: **64 districts, 495 upazilas from a dated directory snapshot, and three mouzas**. This is not a complete national mouza register. Upazilas without verified imported mouzas remain visible, with an explicit empty-state explanation; case creation requires a verified mouza.

## District and upazila expansion

- [Bangladesh National Portal district directory](https://bangladesh.gov.bd/views/district-list), retrieved 17 October 2026: all 64 district names, manually transcribed. Bangladesh has 64 districts; Dhaka is one district, not the parent of all 64.
- [National Portal district-grouped upazila directory](https://bangladesh.gov.bd/views/upazila-list/উপজেলাসমূহ/), retrieved 17 October 2026: cached May 2026 page with a 495-upazila header. Manual bilingual transcription is stored in `data/locations/upazilas-curated.txt`; `scripts/expand_upazilas.py` builds JSON without network access. The newer district page header says 500 upazilas. This mismatch is unresolved, so 495 imported entries are a dated snapshot, **not verified current nationwide completeness**. City thanas and unions are not added as upazilas.
- The directory lists Shaistaganj twice with spelling/domain variants. It is represented once under Habiganj, not counted as two places.
- [Official upazila portal notice, 12 March 2026](https://indurkani.pirojpur.gov.bd/pages/notices/69b2d2a70e394cfb3829fcd7), retrieved 18 October 2026: its indexed official text names Pirojpur district and the renaming of Indurkani to Jiyanagar, supporting the directory's Jiyanagar entry. Direct retrieval failed; the indexed notice text was read, not its attachment. The app imports one Jiyanagar node. It does not assert survey equivalence or create a second Indurkani identity.

Remaining national reference gap: a complete dated official upazila register resolving the 495/500 discrepancy, plus a permitted district→upazila→mouza register with explicit mouza status. No organizer dataset was supplied. The official settlement dropdown did not establish a complete export. No village/union list is substituted, and missing rows are not invented. A national mouza acceptance criterion remains unmet.

## Verified demo mouzas

| District | Upazila | Mouza | Evidence |
|---|---|---|---|
| ঢাকা / Dhaka | সাভার / Savar | বিরুলিয়া / Birulia | 2014 Gazette, printed p. 1485; PDF p. 11 |
| ঢাকা / Dhaka | সাভার / Savar | বড় কাকর / Bara Kakar | Same Gazette and page |
| ঢাকা / Dhaka | ধামরাই / Dhamrai | উত্তর পাড়াগাঁও / Uttar Paragao | 2016 Gazette, printed pp. 1482–1483; PDF pp. 10–11 |

## References and verification method

1. [Bangladesh Gazette, 14 August 2014, Part VI](https://www.dpp.gov.bd/upload_file/gazettes/11383_63985.pdf), published by the Department of Printing and Publications. The schedule on printed page 1485 explicitly identifies Dhaka district, Savar upazila and the two mouzas. Verification status: **verified against authoritative published text**.
2. [Bangladesh Gazette, 1 December 2016, Part VI](https://www.dpp.gov.bd/upload_file/gazettes/19418_85459.pdf), same publisher. Schedules on printed pages 1482–1483 identify Uttar Paragao as a mouza in Dhamrai thana, Dhaka district. Verification status: **verified against authoritative published text**.
3. [Dhamrai Upazila official portal, At a glance](https://dhamrai.dhaka.gov.bd/pages/static-pages/6995d1c235ce18e1c07a9d49) identifies Dhamrai as an upazila. [Kulla Union official portal, At a glance](https://kullaup.dhaka.gov.bd/pages/static-pages/6995bef435ce18e1c07a01f6) explicitly records district Dhaka and upazila Dhamrai. These establish the current administrative labels alongside the historical Gazette's thana terminology.

Names and relationships were manually curated from these targeted public references; no government site was scraped or bulk downloaded. The PDF text uses legacy Bangla font encoding. Search-result OCR was checked against the PDF's extracted body: search snippets misread some numbers. The web PDF screenshot endpoint failed with a cache miss, so this verification is text-based, not a claimed visual page review. The source pages remain linked for organizer review.

English mouza names are explicitly stored transliterations of the verified Bangla names, not claimed official English spellings. No LLM translation runs at application runtime. Internal `loc-*` identifiers are application IDs, never government codes.

**Official codes and JL numbers are intentionally null.** In particular, the 2016 source prints differing JL values in separate Uttar Paragao schedules. The application does not reconcile or import them. Historical geographic evidence does not establish survey equivalence, present boundaries, ownership, or current official identifiers. No parcel boundary or real land record was imported; only geographic names and provenance were retained.

## Extension/import contract

`data/locations/locations.json` separates `sources` and `locations`. Every location has an internal ID, kind, explicit bilingual names, parent ID, verification status, source IDs, and null official identifiers. `backend/app/geography.py` validates hierarchy, bilingual names, source URLs/dates/status, duplicate IDs and existing identity collisions. Include ancestors in the input. Only manually verified rows may be enabled; the schema check itself is not independent geographic verification.

Run `python -m backend.app.geography data/locations/locations.json` for a dry run, then add `--apply` to persist reviewed additions; `--report runtime/geography-import.json` saves counts, missing-parent coverage, input hash and applied status. All rows are validated before insertion and commit is transactional. Existing IDs/names/parents and saved cases are preserved. The importer does not overwrite existing provenance or accept official/JL codes; use a reviewed migration for corrections. `GET /api/locations` supports optional `kind` and `parent_id` filters for future larger catalogs.

The minimum demonstration name/hierarchy scope is supported by the references above. Remaining reference work before real operational use: organizer confirmation of the curated current hierarchy, authoritative survey-specific JL/code mapping, and independently reviewed official English spellings if required. No nationwide coverage or current cadastral validation is claimed.
