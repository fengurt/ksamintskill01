# Measure cost per accepted change

Read when the user requests optimization or comparison, rather than adding bookkeeping to every small edit.

## Evidence to collect

For each representative task and workflow record model IDs, reasoning settings, all calls including repairs, input/output tokens and available cache categories, tool charges, elapsed time, first-delivery acceptance, regressions, and user correction minutes. Include unsuccessful tasks. Record missing fields as unknown. Do not sum a parent's aggregate usage with the same children's usage a second time.

Calculate monetary cost using current provider-specific billing categories. Reasoning tokens may already be included in billed output: inspect usage semantics before summing. Cached inputs remain tokens even when cheaper. API dollars are not a conversion formula for subscription credits or allowances.

Compare total workflow spending across attempted tasks divided by the number accepted under the same criteria. If none are accepted, the ratio is undefined; report failures and spending. Track quality and human effort alongside this ratio so low cost does not hide a worse outcome.

## Pilot design

Start with a small set of representative real changes, covering simple edits, routine features, and difficult defects. Compare a capable single agent with a capable lead plus bounded cheaper workers. Test a cheap coordinator only when the plan and task types are sufficiently stable.

Use isolated copies with the same starting revision, requirements, tools, acceptance checks, and budget. Do not expose the previous arm's solution to the next. Repeat close comparisons and report sample size and uncertainty; a small pilot is operational evidence, not proof of universal superiority. Do not run all variants on every production task.

Move responsibility to a cheaper model only after it meets the user's acceptance target without unacceptable repair or correction costs. If results deteriorate, restore the lead for that task class. Broad native model routing remains instruction-driven unless an external controller enforces these rules.

This measurement procedure is a proposed engineering method. OpenAI's [model-selection guidance](https://developers.openai.com/api/docs/guides/model-selection) recommends establishing accuracy before optimizing cost; its [subagent guidance](https://learn.chatgpt.com/docs/agent-configuration/subagents) warns that delegation adds token usage. Neither establishes that one fixed model hierarchy is optimal across providers.
