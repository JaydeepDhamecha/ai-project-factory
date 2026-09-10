# {{PROJECT_NAME}} — Assumptions and Open Questions

> Append-only. Every agent adds here; nobody deletes. Resolved items are marked
> resolved, not removed.

## Assumptions

```
ASM-NNN   <the assumption>
  Area:        product | requirements | architecture | data | api | design | security | ops
  Because:     why this was assumed (what the sources did not say)
  Impact:      what depends on it
  Risk:        what breaks if it is wrong
  Reversible:  YES | NO | COSTLY
  Made by:     <agent>   Date: <ISO>
  Status:      OPEN | CONFIRMED | CORRECTED
```

| Id | Assumption | Area | Risk | Reversible | Status |
|---|---|---|---|---|---|

## Open questions

Things a safe default could not resolve. No major business functionality is
invented to fill these.

```
Q-NNN     <the question>
  Blocks:      <what cannot proceed, or what is at risk>
  Why unknown: <what the sources say / do not say>
  Options:     <the plausible answers>
  Interim:     <what was built in the meantime, if anything>
  Status:      OPEN | ANSWERED
  Answer:      <once given, with the date>
```

| Id | Question | Blocks | Status |
|---|---|---|---|

## Deviations from source material

Where the implementation deliberately differs from a supplied reference.

| # | Reference | Deviation | Reason | Approved by |
|---|---|---|---|---|
