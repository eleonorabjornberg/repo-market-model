# The pivot

**This folder is the only place the pivot is documented.** Anything elsewhere links here.

On 30 September 2026 the project re-based its methodology. Every published record had read its inputs 4–5 business days
before the day it forecast, and the benchmark was handicapped the same way, so the records were re-scored under an
as-of information rule. This folder holds the finding behind that, the research records written since, and the page a
session starts from.

The current direction is not in this folder. It is the top block of the "Directive queue" issue (#46): the primary goal
H5 (the SOFR − IORB spread distribution in bp), the secondary goal H9, the research plan H1–H10, and the scoring
protocol #640. The September plan and directive briefs are in `docs/archive/`.

| File | What it is |
|---|---|
| [`next-session.md`](next-session.md) | **Start here.** Reading order, state with check commands |
| [`lag-assessment.md`](lag-assessment.md) | The finding: root cause, measured impact, how far it reaches, the fix, alternatives rejected |
| [`literature.md`](literature.md) | Similar work and borrowable methods, with links |
| [`scouting/`](scouting) | The scripts behind the assessment's numbers, with their recorded output |
| `*-result.md`, `studies/`, `evidence/` | Research records: what each study measured, when. They are records, not instructions, and a +5 bp "headline" in them is the project's aim at the time |

The rulings are in `docs/decisions/`: `information-set.md`, `workflow.md` and `publish-rule.md`. Superseded documents
are in `docs/archive/`, which is not binding.
