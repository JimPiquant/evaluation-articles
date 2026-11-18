---
name: evaluation-article-review
description: Review an evaluation article or its draft changes for audience fit, decision usefulness, technical grounding, and consistency with its plan. Use for editorial feedback or a pre-publication content review.
---

# Review an evaluation article

Review only by default. Do not edit the article, change its status, or regenerate
deliverables unless asked.

1. Find the article and its audience in `series.json`. Read the article, its
   adjacent plan, and any requested diff. For a revision, note what improved
   and what useful guidance or caveats were lost. Check the slide source if the
   revision changes a claim the slides repeat.
2. Check that the article helps its audience make a decision: what to choose,
   when and why, what evidence to use, and what tradeoffs affect the choice.
   Look for an observable outcome in examples, clear definitions before use,
   and links to deeper coverage rather than repeated explanations.
3. Keep evaluation purpose (capability or regression), grading method (code,
   model, or human), application architecture, evaluation level (turn or
   conversation), and product catalog categories separate. A rubric defines
   criteria; a reference provides evidence. Neither alone identifies who or
   what assigns the score.
4. Use `references/grounding.md` and `references/sources.json` to verify material
   claims against their sources. Distinguish product behavior, source
   recommendations, and editorial advice. Flag overgeneralized cost or payoff
   claims, unsupported one-to-one mappings, and wording that turns a
   recommendation into a requirement. Check that reader-facing citations use
   linked source titles or section titles, not internal IDs. Say when a claim
   could not be verified.
5. Prioritize review findings by reader impact. For each material finding,
   give the location, explain why it matters, and suggest a concrete fix.
   Separate factual or source issues from style preferences, and mention
   strengths worth preserving.
