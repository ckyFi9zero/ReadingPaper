---
name: lock-paper-story
description: Freeze a minimal, defensible manuscript story from experiments, figures, tables, drafts, and author notes that already exist. Use when a researcher believes the evidence is sufficient to start writing but keeps cycling through research gaps, insights, reviewer-style objections, or expanding experiment requests; when Codex must extract bounded claims and insights, build a claim-evidence map, classify missing evidence as fatal/scope-limiting/optional, decide whether any experiment truly blocks submission, lock the story, or reopen a previously frozen story only for explicit reasons. Do not use for open-ended ideation, literature discovery, formal peer review, prose polishing, or designing an ideal future research program.
---

# Lock Paper Story

Turn completed work into the smallest coherent paper that the evidence can support. Optimize for a defensible submission, not an idealized exhaustive study.

## Governing stance

- Treat existing results as the design boundary unless the user explicitly authorizes new experiments.
- Prefer narrowing or deleting a claim over requesting more evidence.
- Distinguish manuscript sufficiency from scientific completeness. A paper may be bounded and publishable without resolving every limitation.
- Derive the story from evidence. Do not invent a grand research gap and then require the experiments to catch up.
- Do not invoke reviewer simulation before the story is frozen.
- Do not describe scope limitations or future extensions as blockers.
- Allow at most three candidate stories. Converge; do not brainstorm indefinitely.

Read [references/decision-rules.md](references/decision-rules.md) before classifying gaps or recommending experiments. Read [references/output-contract.md](references/output-contract.md) before writing artifacts. Read [references/lidar-robotics-lens.md](references/lidar-robotics-lens.md) only for LiDAR, point-cloud, adverse-weather, autonomous-driving, or robotics perception work.

## Source boundary

Inventory only material actually supplied or explicitly placed in scope:

- experiment logs and result tables;
- figures and captions;
- method notes and code/configuration evidence;
- existing abstracts, outlines, or drafts;
- user-stated observations, failed runs, constraints, and intended venue.

Label every item as `observed`, `author-interpretation`, `unverified`, or `missing`. Never convert an interpretation into a result. Do not conduct literature search unless the user separately asks for novelty verification. Until then, mark novelty as `not assessed`.

## Workflow

### 1. Establish the lock scope

Record:

- intended paper type and audience;
- evidence cutoff date;
- experiments included and excluded;
- resource/time constraints;
- whether new experiments are forbidden, discouraged, or allowed only for fatal gaps;
- target deliverable: story selection, freeze pack, or unlock audit.

Default to `new experiments allowed only for fatal gaps`.

### 2. Build the evidence inventory

Extract each stable result with:

```text
evidence ID | setup | comparison | metric | exact result | repetition/uncertainty | source | boundary
```

Include negative and null results when they constrain interpretation. Do not start from Introduction prose or broad field gaps.

### 3. Build candidate insights

Derive each insight using:

```text
stable observation
+ meaningful contrast
+ smallest design difference that may explain the contrast
+ explicit boundary
= candidate insight
```

Use `suggests` when the mechanism is not isolated. Use `shows` only for direct comparisons. Reject an insight that requires unseen evidence.

### 4. Generate no more than three candidate stories

For each candidate, state:

- central claim;
- concrete problem and bounded gap;
- evidence chain;
- main figures/tables;
- claim boundary;
- strongest counterargument;
- unresolved A-class gaps only;
- novelty status: `not assessed`, `partially checked`, or `verified`.

Rank candidates by evidence coverage, coherence, distinctiveness, and writing cost. Do not rank by how ambitious they sound.

### 5. Select the minimum publishable story

Choose the candidate that:

1. uses the strongest existing evidence;
2. needs the fewest causal or universal assumptions;
3. forms a complete problem–approach–evidence–boundary chain;
4. can be expressed in 3–5 main figures or tables;
5. has no unresolved fatal validity problem.

Present the selected story and one-sentence argument to the user for confirmation before freezing when the framing is genuinely ambiguous. Do not ask for confirmation merely because optional improvements exist.

### 6. Classify every gap and experiment request

Apply the A/B/C rules in [references/decision-rules.md](references/decision-rules.md).

For every suggested experiment, answer all four questions:

1. Which exact abstract-level claim does it support?
2. Can narrowing or deleting that claim resolve the issue?
3. Would an adverse result invalidate the central story?
4. Is it A fatal, B scope-limiting, or C optional?

An experiment may block writing only when it is A-class, supports the central claim, and cannot be replaced by honest claim narrowing. Otherwise record it as non-blocking.

Do not use claim narrowing to bypass the validity of the evidence itself. If a credible unresolved issue may invalidate the labels, split, metric, statistical unit, or data provenance supporting every version of the central claim, keep it A-class and request the smallest audit or correction. An A-class resolution may be a code/configuration check or recalculation; do not automatically call it a new experiment.

### 7. Create the freeze pack

Copy [assets/story-lock-template.md](assets/story-lock-template.md) into a user-approved output directory, or default to `<project>/story-lock/`. Produce:

```text
01-evidence-inventory.md
02-claim-evidence-map.md
03-argument-map.md
04-experiment-decisions.md
05-story-lock.md
```

Follow [references/output-contract.md](references/output-contract.md). Keep the pack concise enough that the user can audit it in one sitting.

### 8. Freeze or stop

Set `Story status: FROZEN` when:

- one central claim is expressible in one sentence;
- every central claim has direct evidence;
- the labels, splits, metrics, and provenance underlying that evidence have no credible unresolved validity contradiction;
- no A-class gap remains unresolved;
- every B-class gap has a boundary statement;
- C-class work is explicitly non-blocking;
- the planned main figures/tables form a complete results sequence.

If an A-class gap remains, set `Story status: BLOCKED`, identify exactly one minimal resolution path, and stop. Do not append a wishlist.

When frozen, hand off to manuscript drafting. Recommend Results first, then Methods, Discussion, Introduction, Conclusion, and Abstract/title last. Use `$nature-writing` when available.

## Unlock protocol

Do not reopen a frozen story because a more ambitious narrative appears possible. Reopen only for:

- discovered data leakage, calculation error, or irreproducibility;
- new evidence that contradicts the central claim;
- a material target-venue change;
- co-author rejection of the central framing;
- explicit user authorization to expand scope.

Record the trigger, affected claim, required change, and whether the previous version remains recoverable. Preserve the old freeze pack.

## Prohibited behaviors

- Do not translate every limitation into an experiment.
- Do not require cross-dataset, cross-sensor, downstream-task, statistical, ablation, qualitative, or real-world experiments by category alone.
- Do not use `first`, `novel`, `unprecedented`, or `state of the art` without dedicated verification.
- Do not hide a fatal flaw by polishing prose.
- Do not continue revising after freeze conditions are met.
- Do not generate full manuscript prose during the lock run unless the user explicitly requests the subsequent handoff.

## Completion report

Return:

1. story status;
2. one-sentence central argument;
3. selected evidence chain;
4. unresolved A-class gaps, or `none`;
5. non-blocking B/C items;
6. freeze-pack paths;
7. exactly one next action.
