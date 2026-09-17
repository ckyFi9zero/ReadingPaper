# Decision rules

## Claim test

A usable manuscript claim must state:

```text
system or task + intervention/design + observed effect + conditions + boundary
```

Prefer the strongest claim fully supported by existing evidence, not the most ambitious plausible claim.

## Gap classes

### A — Fatal validity gap

The central claim cannot remain in the abstract if the issue is unresolved.

Typical cases:

- data leakage or invalid split;
- incorrect metric or analysis;
- no credible comparator for a comparative central claim;
- claimed component contribution with no isolating evidence;
- result not reproducible within the available record;
- unfair comparison caused by undisclosed extra data, labels, or compute;
- the only evidence does not measure the claimed outcome.

Resolution order:

1. correct the analysis;
2. narrow the claim;
3. delete the claim;
4. run the smallest decisive experiment only if steps 2–3 would destroy the central story.

### Evidence-dependency propagation

Trace every central claim through its evidence dependencies:

```text
claim -> reported result -> metric -> labels/ground truth -> split/statistical unit -> raw source
```

If a credible unresolved contradiction at one dependency could invalidate all evidence for the bounded central claim, classify it as A. Do not downgrade it to B by narrowing domain, sensor, dataset, or wording. Resolve it with the smallest audit first, such as inspecting label code, reconstructing a split, recalculating a metric, or checking raw rows. This is evidence validation, not scope-expanding experimentation.

Distinguish:

- `credible validity contradiction`: a specific conflict in formulas, code, logs, splits, counts, or metrics that could reverse evidence meaning -> A until audited;
- `unverified implementation detail`: merely absent from the supplied record, with no concrete contradiction -> boundary or missing input, not automatically A;
- `broader generalization missing`: evidence remains valid inside its domain -> B.

### B — Scope-limiting gap

The paper can proceed, but the conclusion must name its boundary.

Typical cases:

- one dataset, sensor, site, weather type, or population;
- no cross-domain or cross-device test;
- no real-world or downstream-task evaluation;
- limited uncertainty analysis when the observed effect remains clear;
- incomplete mechanism isolation when the paper claims empirical effectiveness rather than mechanism proof.

Required response: add a boundary statement. Do not mark the experiment mandatory.

### C — Optional enhancement

The work may improve presentation, breadth, or future impact but does not decide the central claim.

Typical cases:

- more backbones, datasets, visualizations, or parameter sweeps;
- multimodal, temporal, or deployment extensions;
- broader weather coverage;
- additional case studies after the main effect is established.

Required response: record under future work or omit. Never block writing.

## Experiment admission gate

Admit a new experiment to the blocking list only when all conditions are true:

```text
A-class
AND supports an abstract-level central claim
AND honest claim narrowing cannot resolve it
AND the experiment has a decisive outcome criterion
```

Reject vague requests such as “more validation”, “more baselines”, or “better generalization”. Require one hypothesis, one comparison, one metric, and a falsifying result.

## Story sufficiency test

A story is sufficient when:

- the problem is concrete;
- the gap is the missing relation answered by the work, not the absence of an entire field solution;
- the method introduces a specific delta;
- evidence directly tests the delta or bounded overall effect;
- the conclusion states where the result stops;
- limitations do not contradict the central claim.

Scientific completeness is not required.

## Stop rules

Stop exploring when any condition holds:

- one candidate dominates on evidence coverage and coherence;
- three candidates have been assessed;
- all remaining differences depend only on unsupported speculation;
- freeze conditions are satisfied;
- the same non-blocking experiment is proposed twice;
- two successive revisions do not change the central claim or evidence chain.
