# Page templates

The registry is MECE by a page's primary communication job. A page chooses exactly one template. A visualization is an optional fill inside an evidence page, not another page type.

## Structure

| Id | Use when | Required content | Avoid |
|---|---|---|---|
| `cover` | Opening the artifact | title, subtitle or scope, brand mark | evidence, dense metadata |
| `toc` | Showing the reader's route | ordered sections and short labels | mini summaries for every page |
| `chapter` | Starting a major narrative section | section title and one orienting sentence | charts or detailed evidence |
| `readme` | Explaining scope, method, definitions, or confidence | reading rules and limitations | hiding caveats in fine print |

## Message

| Id | Use when | Required content | Avoid |
|---|---|---|---|
| `statement` | Landing one claim, quotation, question, or principle | one message and optional support | several parallel claims |
| `verdict` | Recording a decision, recommendation, or falsification result | decision, rationale, next action | neutral description without a choice |

## Evidence

| Id | Use when | Required content | Avoid |
|---|---|---|---|
| `kpi` | Comparing 3-6 headline measures | value, label, unit, period or denominator | unrelated vanity metrics |
| `roster` | Showing a named list, ranking, or accountable set | rows, stable columns, explicit total when additive | more rows than fit; paginate |
| `chart` | Answering one quantitative question visually | visualization id, data, source, takeaway | charts chosen before the question |
| `chart-table` | Pairing a figure with executable detail | chart plus no more than 8 supporting rows | repeating every chart value in the table |

## Synthesis

| Id | Use when | Required content | Avoid |
|---|---|---|---|
| `matrix` | Crossing two dimensions or showing a bounded state grid | axes, cell rule, legend, no more than 9 primary cells | using a matrix as decoration |
| `compare` | Contrasting options, profiles, stages, or before/after states | shared comparison criteria | unequal evidence or mismatched units |

## Shell mapping

The 12 templates fit four structural shells:

| Shell | Templates |
|---|---|
| `cover` | `cover` |
| `divider` | `chapter` |
| `body` | `toc`, `readme`, `statement`, `kpi`, `roster`, `matrix`, `compare`, `verdict` |
| `figure` | `chart`, `chart-table` |

Tables are content inside `body` or `figure`; they are not a fifth shell. Continuations retain the same template id and point to the original page with `overflow_of`.

## Classification order

1. Is the page navigation or orientation? Use a Structure template.
2. Is the page primarily one claim or decision? Use a Message template.
3. Is the page primarily source evidence? Use an Evidence template.
4. Is the page combining dimensions or options into a new view? Use a Synthesis template.

If two templates seem equally valid, split the page. It is doing two jobs.
