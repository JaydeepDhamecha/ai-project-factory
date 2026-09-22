# Task packets

A per-feature agent used to open five or six whole documents to implement one
slice, and then the next agent opened the same five or six, and then the next
feature started and all of them did it again.

`.project/state/features.json` carries `requirements: ["REQ-012", …]` — **ids**.
An id is not information. To act on it the agent must read all of
`docs/requirements.md`, which is why every per-feature dispatch paid for the
whole corpus to answer a question about one slice.

A **task packet** resolves those ids once, at plan time, into one bounded file.

---

## 1. Why this band

Measured on a completed reference run of 798 journal events
(`factory/rules/scale-rules.md` §5):

| Band | Share of events |
|---|---|
| Phases 05–10, the per-feature loop incl. fix → retest | **81%** |
| Phases 00–04, the framing phases | 3.3% |

Phases 05–10 repeat **per feature, per platform, and again per fix cycle**. That
multiplier is what makes their reading cost dominate, and it is the only place
in the factory where cutting input tokens compounds.

This is deliberately **not** applied to 00–04. Those phases *are* the reading;
a packet there would be a summary of a document that does not exist yet.

---

## 2. The rule

> A packet is **derived, never authoritative**. Where a packet disagrees with
> the document it cites, **the document wins** —
> `factory/rules/source-of-truth.md` is unchanged by this file.

Four constraints follow, and none is optional:

1. **Resolved, not referenced.** Requirement and acceptance-criterion *text*
   travels in the packet. An id alone recreates the problem.
2. **Citations travel too.** Each requirement keeps the reference-file citation
   it was extracted with. A packet without citations is an unsourced summary,
   and an agent that builds from one cannot be audited.
3. **`notIncluded` is mandatory.** The packet states what it deliberately omits,
   so an agent knows when to open the full document rather than assuming the
   packet is complete. **This field is what makes a packet honest rather than
   lossy.**
4. **Provenance is recorded.** `generatedFrom` carries the path and SHA-256 of
   every document the packet was resolved from. When a document changes, packets
   resolved from the old hash are **stale** and must be regenerated before use.

Schema: `factory/schemas/task-packet.schema.json`.

---

## 3. Who writes them, who reads them

**Written by `planner`**, at the end of `02-plan`, immediately after
`features.json` — one `.project/tasks/<featureId>.json` per feature. The planner
has just read the whole document set to produce the plan, so resolving the
packets costs one extra pass over material already in context.

**Regenerated** whenever a document in `generatedFrom` changes — in practice
after a bug-fix that amends a requirement or the contract. A stale packet is a
defect, not a nuisance: it is how an agent implements a requirement that was
corrected two phases ago.

**Read by** the per-feature agents in 05–10: `backend`, `web`, `mobile`,
`integration`, `qa`, `playwright`, `bug-fixer`.

The reading contract for those agents is:

```
1. .project/tasks/<featureId>.json      ← start here, always
2. the full document                     ← only when the packet's `notIncluded`
                                           says the answer is not in the packet,
                                           or the packet is stale
```

Opening the full document is **never wrong** — it is the source of truth. It is
simply no longer the default, and an agent that opens one records why in its
handoff, so the packets that are failing to carry their weight are visible
rather than inferred.

---

## 4. What this does not change

- **No gate is affected.** Gates cite documents, and every document still
  exists, is still generated, and is still authoritative.
- **No evidence requirement is relaxed.** A packet is an input, never evidence.
- **No requirement is dropped.** A requirement missing from a packet is a
  planner defect that `workflow-validator` catches by set comparison against
  `features.json`.
- **Nothing is summarised away.** Requirement text is copied, not paraphrased.
  Paraphrasing a requirement into a packet is the failure this file exists to
  prevent, not the technique it recommends.

---

## 5. Validation

`workflow-validator` checks, whenever `.project/tasks/` exists:

| Check | Fails when |
|---|---|
| Coverage | A feature in `features.json` has no packet |
| Set equality | A packet's requirement ids ≠ that feature's ids in `features.json` |
| Resolution | A requirement in a packet has an empty `text` |
| Citation | A requirement in a packet has no `citation` |
| Honesty | `notIncluded` is missing or empty |
| Freshness | A `generatedFrom` hash does not match the document on disk |

A failing packet is a `BLOCKED` input, never a warning to work around.
