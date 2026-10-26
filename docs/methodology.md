# Assessment methodology

## Target and company evidence

The unit of assessment is the full text of one ACN point for an essential entity. The processed English catalogue retains requirement IDs, measure descriptions, sheet names and row numbers. The English workbook is the assessment criterion. The original Italian workbook and literal Italian reference phrases remain unchanged for source alignment; application prose, teaching prompts and assessment rationales are in English. The `essenziale` profile value is an original source identifier meaning “essential entity”.

Each request includes the target text, its normative dependencies, target-linked questions with **only their selected answers**, the fictional company profile and all 20 dated `AR-*` company records. Records are not selected according to a desired verdict. Specific facts and later clarifications must be read alongside general statements. Missing information does not automatically establish the absence of a control.

The questionnaire's unselected options appear only in the separate offline matching exercise. Selected values, labels, question text and conditional visibility are checked for consistency.

## Directed dependencies

The graph contains 72 nodes and 106 edges: 71 question/source links and 35 dependency edges. Academy acceptance is an editorial decision, not a legal audit; source review statuses are retained.

| Relation | Meaning |
| --- | --- |
| `REQUIRES_CONTEXT_INTERNAL` | A point references another point in the same measure. |
| `REQUIRES_CONTEXT_EXTERNAL` | A point references another ACN measure. |
| `HAS_POINT` | A referenced measure contains a point. It does not imply a direct target dependency. |

Traversal follows the recorded source-to-target direction, including transitive references. Nodes are deduplicated while all reference paths and relation types remain available. Cycles are recorded and stopped. A path through an external measure remains external even if a later step is internal. Dependencies explain the target; they are not separately assessed. Reached references to documents outside the catalogue remain explicitly unresolved.

Only questions linked to the target supply selected answers. Questions are not indiscriminately added from every dependency.

## ENISA guidance

Candidate guidance follows `ACN ← question → ENISA section`. The first step traverses a question-to-ACN edge in reverse. An explicit per-target editorial passage selection is then applied. A shared question is a retrieval route, not proof of passage relevance, legal equivalence or company compliance. An empty selection for a target is deliberate.

The package contains 28 verified ENISA excerpts. Each offered passage retains its ID, section, title, text, physical PDF page, printed page, PDF hash and matching paths. Passages are deduplicated. Normalized substring checks against the included PDF establish text identity, not interpretive sufficiency. Consult the full page when context or qualifications matter.

Physical PDF pages are numbered from 1, including the cover; printed labels are one lower in this document. The supplied index is for navigation. Heading node `0023` has an inconsistent source interval; verified excerpt pages, rather than that interval, locate the quotations. Heading node IDs and substantive clause IDs remain distinct.

ENISA is interpretive guidance. Company evidence comes from selected answers and `AR-*` records. The validator keeps those citation categories separate.

## Prompts and source integrity

`assessment.txt` and `matching.txt` preserve the English teaching templates presented in the demonstration. Every placeholder must have exactly one supplied value; missing or unexpected substitutions fail. The assessment replaces the illustrative output shape with the actual per-target JSON Schema.

A short execution prefix limits the model to supplied material and instructs it not to follow instructions embedded in source data. The rendered template and exact prefixed input are saved separately in new runs. No saved judgments, expected status labels, teacher rubric or target distribution is loaded into the context. Internal source-origin paths and hashes in the processed data are provenance, not runtime dependencies on another checkout.

All required inputs are under `src/nis2_academy/resources/`. `integrity.json` detects accidental source changes. It is not protection against someone who can also rewrite the integrity file. The 27-target boundary prevents claiming reviewed dependency/matching coverage for the remaining 89 catalogue points.

## Output and review

The schema follows the teaching demonstration: `requirement_id`, `status`, `reason`, typed `source_ids`, and `missing_information`. Status is one of `Satisfied`, `Partially satisfied`, `Not satisfied`, `Not determinable`.

Validation checks exact fields, target identity, allowed status, nonblank rationale, reference membership and type, duplicate references, missing-information entries for `Not determinable`, and at least one company-evidence reference for a determinate judgment. Duplicate JSON keys, NaN, Markdown fences and surrounding text are rejected.

These checks cannot establish whether a citation supports a claim, whether all relevant facts were weighed or whether the verdict is correct. Human review must examine the full target, evidence, contradictions and rationale. The included results are preserved assessments for that review; tests use synthetic responses to check program behavior rather than treating their statuses as ground truth.
