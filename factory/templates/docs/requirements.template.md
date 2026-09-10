# {{PROJECT_NAME}} — Requirements

> Owner: `project-requirements` · Ids are stable and never reused.

## Format

```
REQ-NNN   <one-line statement>
  Objective:    why this exists
  Actors:       who performs / is affected
  Inputs:       data in
  Outputs:      data / effect out
  Permissions:  who may do this
  Rules:        business rules that apply
  Validation:   field-level rules
  Errors:       what can go wrong, and what the user sees
  States:       loading / empty / error / success behaviour
  Source:       references/<file> p.N §X  |  description  |  DERIVED  |  ASSUMED
  Confidence:   EXPLICIT | DERIVED | ASSUMED | UNKNOWN
  Feature:      f<NN>-<slug>
  Criteria:     AC-NNN-1, AC-NNN-2
```

## Functional requirements

### {{FEATURE_AREA}}

REQ-001

## Non-functional requirements

| Id | Category | Requirement | Target | Source | Confidence |
|---|---|---|---|---|---|

## Traceability summary

| REQ | Feature | Criteria | Test | Status |
|---|---|---|---|---|

Every requirement appears in exactly one feature. Every functional requirement
has at least one acceptance criterion.
