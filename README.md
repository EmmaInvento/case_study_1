# Aurora Grid — NIS2 methodology design case

**FusionAI Academy · 23 October 2026 · Morning workshop**

Aurora Grid is a fictional electricity-grid operator. For this exercise, assume it is an Italian NIS2 essential entity. The company information describes the situation as of **9 October 2026**.

## Your consulting assignment

Propose an effective AI-assisted methodology for assessing Aurora Grid against the supplied ACN requirements. Explain how your approach would work, why it is suitable, and how the client could judge the reliability of its conclusions.

Your deliverable is a **methodology report**. No code, working application, installation or paid service is required. The technical approach, organisation of information, relationships between sources and design of any proposed outputs are your decisions. Explain and justify them in your report.

The method should address the supplied case as a whole. During the workshop, use a small example from the materials to make your reasoning concrete. You do not need to complete an assessment of all 116 requirement points or produce a full set of questionnaire mappings.

## Materials

| Material | What it contains |
| --- | --- |
| [Security questionnaire](inputs/security-questionnaire.md) · [JSON version](inputs/security-questionnaire.json) | Ten questions and their possible answers. This blank form contains no Aurora selections. |
| [Aurora Grid dossier](inputs/aurora-grid-dossier.md) · [JSON version](inputs/aurora-grid-dossier.json) | Aurora's selected answers and twenty dated company records. |
| [ACN requirements workbook](inputs/acn-essential-entity-requirements.xlsx) | An editorial English exercise translation of 116 numbered ACN requirement points. Open the `Security Measures` sheet. |
| [ENISA technical guidance](inputs/enisa-technical-guidance.pdf) | Technical guidance available to support your analysis. It is non-binding guidance, not company evidence. |

The Markdown and JSON versions contain the same case information in different formats. Use whichever is convenient. A document reader and a spreadsheet viewer are enough to take part; no software dependencies need to be installed.

Review the supplied materials and explain the role you assign to each in your proposal. The [input manifest](input-manifest.json) identifies the exact files by checksum. The workbook and PDF are the reference editions for this exercise.

Source attribution: [ACN — Modalità e specifiche di base](https://www.acn.gov.it/portale/nis/modalita-specifiche-base) and [ENISA — NIS2 Technical Implementation Guidance, June 2025](https://www.enisa.europa.eu/sites/default/files/2025-06/ENISA_Technical_implementation_guidance_on_cybersecurity_risk_management_measures_version_1.0.pdf). The exercise translation does not replace the official ACN text.

## What to hand in

Submit **one report per team**, with the team members' names. PDF is recommended; Markdown is also accepted. Aim for **4–6 pages**, excluding a short references section or optional appendix. This is a suggested length, not a reason to omit an important design decision.

Your report must explain:

1. **Objective and scope:** the client need, what your method would assess, and its assumptions.
2. **Proposed methodology:** the steps, responsibilities and design choices, including where AI would help and where human judgment is needed.
3. **A small worked illustration:** apply your proposed reasoning to a case example of your choice, using precise references to the supplied materials. Distinguish what you actually examined from what your proposed system would do.
4. **Reliability and limitations:** how you would evaluate the approach, what could fail, and how you would handle missing, conflicting or inconclusive information.
5. **Client handoff:** what the client would receive, what remains unresolved and which questions or further information you would request.

The [report template](SUBMISSION_TEMPLATE.md) gives prompts for these sections. You may adapt its structure. A diagram is welcome if it makes your approach easier to understand. The template organises your explanation; it does not prescribe a system architecture or an output schema.

Name the file `team-<name>-nis2-methodology.pdf` (or `.md`). Submit through the channel specified by the instructor during the session. Be ready to explain and defend your design in the debrief.

## How your proposal will be discussed

We will look for a clear, feasible method; justified use of the available materials; reasoning that can be checked; meaningful reliability checks; and an honest account of limitations. We assess the quality of your design and explanation, not the amount of code or the choice of a particular technology.

Any illustrative finding should identify the exact ACN measure and numbered point. These judgment meanings are shared vocabulary for the exercise:

| Judgment | Meaning |
| --- | --- |
| Satisfied | The available company information supports every material element of the point within its stated scope. |
| Partially satisfied | Some material elements are supported, while a material limit is shown. Explain both. |
| Not satisfied | Company information affirmatively shows that a material requirement is unmet. |
| Not determinable | Missing, narrow or unresolved information prevents a conclusion. |

A missing record alone does not prove noncompliance. Keep the scope and date of any company record in view. Cite source locations clearly enough for a reader to check your example: ACN code and point, questionnaire question, dossier record ID and date, or ENISA section and PDF page as applicable.

## Working arrangements

- You have three hours for the exercise; breaks are outside that clock.
- Ask the presenter, acting as the client contact, about unclear case information. Record unresolved assumptions and questions.
- You may use AI tools, but you remain responsible for the reasoning and references. Briefly disclose any assistance used.
- The afternoon session is an instructor-led debrief of a worked system. Your morning proposal is the basis for comparison and discussion.
