# Output contract

## 01-evidence-inventory.md

Include one row per result:

| ID | Setup | Comparison | Metric | Exact result | Uncertainty/repeats | Source | Boundary | Confidence |
|---|---|---|---|---|---|---|---|---|

Never round away a result that affects interpretation. Mark missing repetition or uncertainty explicitly.

## 02-claim-evidence-map.md

| Claim ID | Proposed claim | Evidence IDs | Strength | Allowed wording | Forbidden wording | Boundary | Status |
|---|---|---|---|---|---|---|---|

Status must be one of:

- `supported`
- `supported-with-boundary`
- `inference`
- `unsupported-remove`
- `fatal-gap`

## 03-argument-map.md

Record:

```text
Observed phenomenon:
Bounded research gap:
Research question:
Method delta:
Central claim:
Evidence chain:
Alternative explanation:
Boundary:
Contribution statement:
Main figure sequence:
```

The bounded gap must be answerable by the current evidence. Avoid “no work solves X” unless verified and necessary.

## 04-experiment-decisions.md

| Proposed experiment | Exact abstract claim | Can claim be narrowed? | Adverse-result consequence | Class | Blocking? | Decision |
|---|---|---|---|---|---|---|

Do not create a separate mandatory-experiment wishlist.

## 05-story-lock.md

Use:

```text
Story status: FROZEN | BLOCKED | DRAFT
Freeze date:
Evidence cutoff:
Paper type:
Target audience/venue:

One-sentence argument:
In [task/setting], we show [bounded advance] using [approach], supported by [evidence], under [boundary].

Central claims:
Main figures/tables:
Allowed claims:
Forbidden claim expansion:
Unresolved A-class gaps:
Non-blocking B-class boundaries:
Deferred C-class extensions:

Unlock conditions:
Handoff order:
```

## Quality checks

Before setting `FROZEN`, verify:

- every central claim appears in the map;
- every central claim links to existing evidence;
- no credible unresolved validity contradiction affects the evidence dependency chain;
- every number is traceable;
- no B/C item appears as blocking;
- no novelty claim appears without verification;
- figure order tells the same story as the argument map;
- the one-sentence argument contains a boundary;
- the next action is manuscript drafting, not open-ended experiment design.
