# Deterministic checking rules — version 1.0

No rule establishes criminal fraud or legal title. Outcomes describe supplied evidence only.

| Code | Trigger | Priority |
|---|---|---|
| EXCESS_AREA | Proposed amount exceeds original holding area minus same-holding completed transfers on/before proposal date | Conflict |
| OVERLAPPING_TRANSFER | Same-interest supplied overlap reference, or proposed + pending commitments exceeds documented remainder | Conflict requiring review |
| SELLER_MISMATCH | Explicit seller/holder/mutation party IDs disagree | Conflict |
| AREA_MISMATCH | Supplied holding and mutation amounts disagree | Conflict |
| MISSING_INFORMATION | Critical fields, holding, mutation or declared complete relevant history missing | Information |
| AMBIGUOUS_IDENTITY | Holding/mouza/survey/dag mapping differs or unsupported ownership structure is marked ambiguous | Information / manual review |

Outcome precedence is conflict, then insufficient information, then no conflict found in supplied records. Conflict and missing-information findings coexist. Both languages use exactly the same codes and calculations; reviewed bilingual explanation/action templates are stored with findings.

Amounts use Decimal with at most six decimal places. Bangla digits are normalized only for calculation; the original entered text remains stored. Negative, non-finite, overlarge and excessive-precision inputs are rejected. Unit is explicitly decimal/shotok; no acre/bigha/katha conversion is guessed.

Identity includes mouza, survey, dag and holding interest. Different survey records are never automatically equated. A name is not an identity key. The synthetic holding record represents one identified seller interest, not necessarily the entire parcel. Unsupported joint interests, inheritance, subdivision or uncertain mapping must be marked ambiguous and require manual review.

Completed transfers reduce the correct holding's amount only when dated on/before the proposal. Future, cancelled, other-holding and explicitly identified proposed transfers are excluded. Pending transfers do not reduce completed balance. A pending transfer alone is not a conflict; overcommitment or a supplied overlap reference is needed. This is a numerical/explicit-reference check, not geometric parcel-overlap detection.

Unknown relevant history always emits missing information. A known excess can still be reported alongside that warning; no clean result is emitted. Record-area conflicts compare fixtures documented as the same holding scope, not different historical extents. Source links point to the actual per-case synthetic exhibits used in analysis.

## Dataset

22 hand-authored cases cover valid/excess/overlap, mutation area and holder discrepancies, same dag in another mouza, partial sale, pending/cancelled/future transfers, incomplete history, unreadable dag, Bangla/English amounts, correction, cross-survey uncertainty, exact 0.3−0.1 arithmetic, unsupported joint ownership, missing mutation and mixed conflict/missing evidence.

Expected codes are stored in `data/scenarios/cases.json`. Engine-only labeled evaluation includes unreadable fields; the HTTP workflow correctly refuses to run those unresolved fields until human correction. Thus rule evaluation and workflow confirmation tests assess distinct layers.

Fixtures are deliberately small and not independent real-world validation. Synthetic agreement is not nationwide accuracy, extraction accuracy, recall on real fraud, or evidence of legal validity.
