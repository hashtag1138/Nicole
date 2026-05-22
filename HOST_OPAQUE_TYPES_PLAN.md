# Host Opaque Types Plan

## 1. Plan maintenance rule

This file is the authoritative workflow/status plan for the Nicole host opaque types spec update.

Maintenance rules:

- update this file before or together with any phase transition
- preserve the accepted design decisions unless an explicit design-decision prompt changes them
- append a short entry to the change log for each material plan/status update
- keep workflow phase names and ordering stable
- do not treat this file as normative language spec text
- if the baseline commit/tag changes, update the baseline section first

---

## 2. Goal

Plan the full specification workflow for introducing **host opaque types** into Nicole without introducing a general user-defined type system.

This plan covers:

- pre-patch audit discipline
- spec patch sequencing
- post-patch audit discipline
- commit/tag/push order
- expected affected spec files
- residual design gaps to monitor

This plan does not itself patch the specification.

---

## 3. Baseline

Repository:

```text
/data/data/com.termux/files/home/Sources/nicole/nicole_language_docs_seed
```

Expected baseline:

```text
HEAD: 08706edd315e64c22b47e69b4121a0f0f04e7a9f
tag: v0.1.0-modules-freeze
```

Current workflow target:

```text
Host opaque types RFC/spec patch workflow
```

---

## 4. Source of truth

Normative source of truth:

- `SYNTAXE.md`
- `SEMANTIQUE.md`
- `HOST_ABI.md`

Derived/supporting documents expected to be updated in this workflow:

- `INVALID_EXAMPLES.md`
- `EXAMPLES.md`
- `README.md`

If any derived document diverges from the normative spec files, the normative spec files win.

---

## 5. Accepted design decisions

- Feature name: `host opaque type`
- Declared by host ABI only
- Nicole source cannot declare opaque types
- Names live under `host.*`
- Nested names allowed, e.g. `host.io.FileHandle`
- Nominal typing
- Allowed in signatures, locals, stack values, quotations, `List<T>`, `Result<T,E>`, `Map<K,T>` where `K ∈ {Int,String,Bool}`
- Host opaque types may appear as map values only
- Forbidden as `Map` keys
- Forbidden generic equality
- Not constructible in Nicole
- No field access
- No source-level opaque type syntax
- No external type syntax
- No ownership system
- No destructors
- No nullable handles
- Closed-handle state is host-contract state
- Aliases deferred to a later RFC

---

## 6. Explicit non-goals

- patching the implementation
- introducing a user-defined type system
- introducing source declarations such as `opaque type`, `external type`, or `extern type`
- introducing type aliases in this workflow
- introducing ownership, move semantics, or borrow rules
- introducing nullable handles
- introducing destructors or automatic finalization guarantees
- introducing generic equality or ordering for opaque values
- allowing opaque values as `Map` keys
- introducing callback or quotation ABI extensions
- defining a serialization protocol

Alias discussion remains deferred and should stay absent from the first spec patch except for an explicit defer note if needed.

---

## 7. Phase table

| Phase | Name | Status | Primary outcome |
|---|---|---|---|
| 0 | Preliminary spec audit | complete | initial spec-only audit completed |
| 1 | Plan creation | in-progress | this plan file created and validated |
| 2 | Pre-patch audit | pending | exact patch-ready audit against current spec text |
| 3 | Spec patch | pending | normative spec files updated |
| 4 | Post-patch audit | pending | patch reviewed for consistency/completeness |
| 5 | Commit spec patch | pending | spec patch committed |
| 6 | Final audit | pending | repository re-audited after commit |
| 7 | Final plan/status commit | pending | this plan/status file updated and committed |
| 8 | Tag and push | pending | final verification, tag, and push |

Required workflow exactly:

```text
Phase 0 — Preliminary spec audit
Status: complete

Phase 1 — Plan creation
Status: in-progress

Phase 2 — Pre-patch audit
Status: pending

Phase 3 — Spec patch
Status: pending

Phase 4 — Post-patch audit
Status: pending

Phase 5 — Commit spec patch
Status: pending

Phase 6 — Final audit
Status: pending

Phase 7 — Final plan/status commit
Status: pending

Phase 8 — Tag and push
Status: pending
```

---

## 8. Detailed phases

### Phase 0 — Preliminary spec audit

Status:

```text
complete
```

Purpose:

- confirm host opaque types are broadly coherent with the Nicole specification direction
- identify current conflicts and deferred clauses
- confirm accepted design assumptions for planning

Exit criteria:

- audit complete
- planning can proceed without reopening the accepted design decisions

### Phase 1 — Plan creation

Status:

```text
in-progress
```

Purpose:

- create this workflow/status file
- record accepted design decisions, non-goals, phase order, and audit discipline

Exit criteria:

- `HOST_OPAQUE_TYPES_PLAN.md` exists
- only this file is modified
- baseline and validation commands are recorded

### Phase 2 — Pre-patch audit

Status:

```text
pending
```

Purpose:

- perform a fresh spec-only audit immediately before drafting the patch
- verify no relevant spec text changed since planning
- identify exact target sections and wording boundaries

Required checks:

- current baseline still matches expected commit/tag or is intentionally updated in this plan
- worktree clean before patching
- accepted design decisions still hold
- alias discussion remains deferred

Exit criteria:

- patch-ready audit notes exist in the prompt/session
- no untracked design drift remains

### Phase 3 — Spec patch

Status:

```text
pending
```

Purpose:

- patch only the specification documents

Expected normative work:

- define host-qualified opaque type naming in `SYNTAXE.md`
- integrate host opaque values into type/semantic rules
- update ABI rules in `HOST_ABI.md`
- add required invalid and valid examples
- refresh `README.md`

Patch grouping rule:

- group tightly coupled normative changes into the same patch
- do not split naming/type admission from equality exclusion
- do not split ABI admission from export ABI wording updates

Exit criteria:

- patch applied to the planned spec files
- no unrelated file changes

### Phase 4 — Post-patch audit

Status:

```text
pending
```

Purpose:

- audit the patched spec before any commit

Required review focus:

- naming consistency for `host.*` opaque types
- coherence between `SYNTAXE.md`, `SEMANTIQUE.md`, and `HOST_ABI.md`
- equality exclusion present and correctly scoped
- `Map` key restriction preserved
- aliases still absent
- examples consistent with the normative text

Exit criteria:

- audit confirms the patch is coherent
- any required corrections applied before commit

### Phase 5 — Commit spec patch

Status:

```text
pending
```

Purpose:

- create the spec patch commit only after successful post-patch audit

Commit discipline:

- commit only after audit passes
- do not tag yet
- do not push yet

Exit criteria:

- spec patch committed

### Phase 6 — Final audit

Status:

```text
pending
```

Purpose:

- re-audit the repository after the spec patch commit
- verify committed state matches intended outcome

Required checks:

- clean worktree after commit
- expected files changed and nothing else
- wording still coherent after commit boundary

Exit criteria:

- final audit passed

### Phase 7 — Final plan/status commit

Status:

```text
pending
```

Purpose:

- update this plan file with final statuses and any residual gaps
- commit the final plan/status update only after the final audit

Required updates:

- mark completed phases
- record residual gaps that remain intentionally deferred
- append final change log entry

Exit criteria:

- plan/status commit created

### Phase 8 — Tag and push

Status:

```text
pending
```

Purpose:

- perform final validation
- tag only after clean verification
- push only after tag verification

Required discipline:

- clean worktree before tag
- tag only after final validation
- verify tag placement
- push only after tag verification

Exit criteria:

- tag created and verified
- push completed

---

## 8A. Expected spec file impact

### `SYNTAXE.md`

- expected change:
  - explicit admission of host opaque type names under `host.*`
  - explicit admission of nested names such as `host.io.FileHandle`
  - type-surface integration for host opaque types
  - generic equality exclusion for host opaque types
  - preserve map key restriction (`Int`, `String`, `Bool`) while allowing host opaque types as map values
- risk:
  - high
- phase where modified:
  - Phase 3

### `SEMANTIQUE.md`

- expected change:
  - semantic behavior of opaque values in locals, stack values, quotations, and containers
  - clarification that closed-handle state is host-contract state, not type-state
- risk:
  - medium
- phase where modified:
  - Phase 3

### `HOST_ABI.md`

- expected change:
  - declaration model for host opaque types
  - ABI-valid value family update
  - recursive container compatibility including `Map<K,T>` values where `K` stays a valid v1 key type
  - export ABI wording update
  - lifetime/close responsibility wording
- risk:
  - high
- phase where modified:
  - Phase 3

### `INVALID_EXAMPLES.md`

- expected change:
  - invalid examples for constructor attempts, field access, generic equality, opaque map keys, and forbidden source syntaxes
- risk:
  - low
- phase where modified:
  - Phase 3

### `EXAMPLES.md`

- expected change:
  - valid examples for host opaque values in signatures, containers, results, and quotations
- risk:
  - low
- phase where modified:
  - Phase 3

### `README.md`

- expected change:
  - high-level project summary update to reflect host opaque type support in the specification
- risk:
  - low
- phase where modified:
  - Phase 3

---

## 8B. Audit and patch discipline

This workflow requires the following order:

- audit before patch
- patch before audit
- audit before commit
- commit before final audit
- final audit before final plan/status commit
- clean worktree before tag
- tag only after final validation
- push only after tag verification

Operational interpretation:

- Phase 2 must complete before Phase 3
- Phase 4 must complete before Phase 5
- Phase 6 must complete before Phase 7
- Phase 8 must not begin unless the worktree is clean

---

## 9. Validation commands

Baseline and worktree validation:

```bash
git status --short
git rev-parse HEAD
git diff --stat
```

Content sanity scan:

```bash
grep -RIn "host opaque\|host.io.FileHandle\|opaque type\|external type\|extern type" SYNTAXE.md SEMANTIQUE.md HOST_ABI.md INVALID_EXAMPLES.md EXAMPLES.md README.md || true
```

Workflow note:

- no implementation tests are required for this plan because the workflow is spec-only

---

## 10. Residual gaps

These are known residual gaps to monitor during later phases:

- exact wording for excluding host opaque types from generic equality
- exact wording for exported Nicole words using declared host opaque types
- whether debug rendering should be explicitly marked implementation-defined
- whether repeated `close` behavior should remain fully host-defined
- ensuring alias discussion remains deferred and absent from the first patch
- ensuring no wording drifts into ownership, destructors, or nullable-handle semantics
- ensuring map wording remains consistent: host opaque types may appear as map values for any valid existing key type (`K ∈ {Int,String,Bool}`), never as map keys

These gaps are not blockers for Phase 1 plan creation.

---

## 11. Change log

- 2026-05-22: created initial `HOST_OPAQUE_TYPES_PLAN.md`; recorded baseline, accepted design decisions, workflow phases, expected file impact, validation commands, and audit discipline
- 2026-05-22: corrected host opaque map-value decision: host opaque types may appear as map values for any existing valid key type `K ∈ {Int,String,Bool}`; host opaque types remain forbidden as map keys
