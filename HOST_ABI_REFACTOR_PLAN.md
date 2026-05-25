# Host ABI Specification Refactor Plan

## Status

Document status:

`stable`

Current global status:

`planned`

## Scope rule

This file is a specification tracking document only.

It records the frozen architecture decisions for the host ABI refactor and prepares the later spec migration workflow.

This file is not normative language spec text.

## Source of truth

Normative source of truth:

- `SYNTAXE.md`
- `SEMANTIQUE.md`
- `HOST_ABI.md`

Derived/supporting documents expected to be updated later in this workflow:

- `EXAMPLES.md`
- `INVALID_EXAMPLES.md`
- `README.md`
- `MODULE_REFACTOR_PLAN.md`

If this plan conflicts with the current normative specification, the normative specification remains the source of truth until the migration phases are executed.

## Context

Phase 9 was paused because the current host ABI model was no longer stable enough for direct spec patching.

The host examples exposed architecture limitations in the current specification model:

- direct global `host.*` access hides dependencies in the language surface
- global top-level import visibility does not fit explicit host capability wiring
- the current host contract model lives primarily outside Nicole source
- the existing examples made the architectural mismatch visible before a safe spec rewrite plan existed

This is a specification evolution task, not an implementation task.

Implementation work is paused until the specification is stabilized because:

- the host capability surface is changing at the language-model level
- name resolution and import visibility rules are changing
- host ABI effect sourcing is changing
- examples and invalid examples must be realigned after the normative model is rewritten

No implementation work should be used to drive these language decisions.

## Frozen architecture decisions

- Direct global host access is removed from the language model. Direct `host.*` calls are scheduled for later removal from the specification. Backward compatibility is not required.
- `@host` becomes a reserved ABI declaration module.
- `@host` is not a normal user module.
- `@host` exists to declare host ABI requirements and expose importable host capabilities.
- `require` becomes a new language declaration form.
- `require` is allowed only inside `module @host`.
- A `require` declares a capability path, a stack signature, an explicit effect classification, and an importable symbol.
- Host ABI becomes source-visible.
- Nicole source files declare required host capabilities directly.
- The runtime/interpreter must satisfy the declared ABI.
- Runtime implementations remain trusted.
- Application modules import host capabilities explicitly.
- Imports become module-local.
- Aliases become module-local.
- Qualified aliases are allowed.
- Simple aliases remain allowed.
- Explicit ABI effects are required.
- `pure` becomes explicitly expressible in host ABI declarations.
- `@host` is fragmentable across files.
- Multiple `module @host` fragments are allowed.
- The merged `@host` ABI contract must be deterministic.
- File order must not affect `@host` semantics.
- Identical duplicate `require` declarations are allowed.
- Divergent declarations for the same capability path are compile-time errors.
- Builtins remain out of scope for this workflow: `list.*`, `map.*`, `result.*`.
- This is a specification evolution task only. It is not a NicolePy implementation task, migration-compatibility task, runtime bug task, or parser bug task.

## Frozen S1 syntax-surface decisions

- Qualified aliases are valid in import declarations.
- Simple aliases remain valid.
- Qualified aliases are local alias names.
- Qualified aliases are not module references.
- Aliases cannot start with `@`.
- Aliases cannot occupy reserved roots such as `host`.
- Canonical `require` capability paths are relative to `@host`.
- `require @host.console.log` is not the canonical form.
- Capability paths use `.` separators.
- Capability paths remain concise and concaténative in style.
- Imports are legal only inside modules.
- Imports appear before word definitions.
- Top-level imports are removed from the target syntax model.
- Imports are not legal inside word bodies.
- `require` is legal only inside `module @host`.
- `require` appears directly in the `@host` body.
- `@host` contains ABI declarations only.
- `@host` cannot contain imports.
- `@host` cannot contain exports.
- `@host` cannot contain word definitions.
- `@host` cannot contain executable logic.
- `@host` cannot contain constants.
- `@host` cannot contain variables.
- `pure` is legal only in ABI declaration surface.
- `dirty` remains legal in existing syntax.
- Every `require` must declare an explicit ABI effect.
- This does not generalize `pure` as a general Nicole declaration modifier.
- Preferred canonical `require` syntax is compact single-line form.
- Expanded multiline `require` form is also valid.
- Compact and multiline `require` forms are equivalent.
- Compact `require` form is preferred in simple examples.
- Multiline `require` form remains allowed for readability.
- Multiple `module @host` fragments are allowed.
- The fragmentability exception applies only to `@host`.
- No other module becomes fragmentable.

## Explicit non-goals

- modularizing builtins in this workflow
- rewriting `list.*`, `map.*`, or `result.*`
- adding a runtime reflection system
- adding dynamic capability negotiation
- adding hidden capability injection
- doing NicolePy implementation work
- restoring or preserving backward compatibility for direct `host.*`
- defining a VM architecture
- defining a session model
- expanding the language into a framework-oriented capability system

## Architectural invariants

- explicit dependencies are preferred over implicit host access
- host capabilities must be visible in source
- no hidden runtime semantics should be introduced by the host ABI model
- static validation must stay deterministic
- runtime implementations remain trusted rather than proved by the language
- file order must not affect merged ABI meaning
- no VM creep should enter the specification through this workflow
- no session creep should enter the specification through this workflow
- no framework creep should enter the specification through this workflow
- no hidden capability injection is allowed
- the repository specification remains the only authority for language behavior

## Open questions

- exact wording and structure of merge diagnostics for divergent `@host` declarations
- exact wording and structure of duplicate-identical `@host` declaration handling
- exact normative formulation of deterministic `@host` fragment merge
- exact normative distinction between reserved `@host` behavior and normal user-module behavior

## Planned migration phases

### Phase S1 — Syntax refactor

- Goal: rewrite the syntax-level host model around `@host`, `require`, module-local imports, and qualified aliases.
- Files:
  - `SYNTAXE.md`
- Tasks:
  - add `require` as a reserved declaration form
  - legalize reserved `module @host`
  - record that `@host` is ABI-declaration-only and not a normal user module
  - define `require` placement inside `module @host`
  - define capability-path declaration shape
  - define canonical relative capability-path form under `@host`
  - define compact and multiline `require` forms
  - define module-local imports
  - define import ordering before word definitions
  - remove top-level import syntax from the active model
  - forbid imports inside word bodies
  - define qualified aliases
  - preserve simple aliases
  - constrain aliases so they cannot start with `@` or occupy reserved roots
  - remove direct `host.*` call support from the syntax model
  - restate reserved-root rules to account for reserved `@host`
  - state the fragmentable `@host` exception without generalizing module fragmentability
  - define explicit ABI effect presence in every `require`
  - constrain `pure` to ABI declaration surface only
- Explicit exclusions:
  - no builtin refactor
  - no implementation notes

### Phase S2 — Semantic model refactor

- Goal: replace the current direct-host semantic model with explicit imported host capabilities.
- Files:
  - `SEMANTIQUE.md`
- Tasks:
  - rewrite name resolution around module-local imports
  - rewrite host capability lookup around imported `@host` declarations
  - rewrite import visibility rules
  - rewrite alias visibility rules
  - rewrite effect sourcing for host capabilities
  - remove semantic wording that treats direct `host.*` calls as the active language model
- Explicit exclusions:
  - no runtime design expansion
  - no builtin semantic changes

### Phase S3 — Host ABI refactor

- Goal: move the host ABI model from external-only declaration toward source-visible declaration plus trusted runtime satisfaction.
- Files:
  - `HOST_ABI.md`
- Tasks:
  - define source-visible ABI declarations
  - define `require` contract structure
  - define explicit ABI effect declaration with `pure` and `dirty`
  - define `@host` fragment merge model
  - define deterministic merge constraints
  - define identical-duplicate acceptance
  - define divergent-duplicate rejection
  - rewrite compatibility validation wording around declared source ABI
  - keep runtime trust model explicit
- Explicit exclusions:
  - no dynamic negotiation model
  - no reflection model

### Phase S4 — Example migration

- Goal: realign valid examples with the new host ABI model.
- Files:
  - `EXAMPLES.md`
- Tasks:
  - rewrite host examples to use `module @host`
  - remove direct host access examples
  - add module-local import examples
  - add qualified alias examples
  - align effect examples with explicit imported host capabilities
- Explicit exclusions:
  - no new builtin examples outside existing scope

### Phase S5 — Invalid examples migration

- Goal: replace obsolete invalid cases and add invalid cases required by the new host ABI model.
- Files:
  - `INVALID_EXAMPLES.md`
- Tasks:
  - remove invalid `module @host` examples tied to the old model
  - remove invalid cases that assume direct `host.*` is still the active model
  - add invalid `require` placement cases
  - add invalid `@host` fragment divergence cases
  - add invalid module-local import locality cases
  - add invalid import ordering and placement cases
  - add invalid qualified alias cases
  - add invalid `@host` body-content cases
  - add invalid missing-ABI-effect cases
  - add invalid direct `host.*` usage cases under the new model
- Explicit exclusions:
  - no separate parallel invalid corpus

### Phase S6 — Repository consistency pass

- Goal: align overview and tracking documents with the migrated specification.
- Files:
  - `README.md`
  - `MODULE_REFACTOR_PLAN.md`
  - `HOST_ABI_REFACTOR_PLAN.md`
  - other overview documents if later needed
- Tasks:
  - remove stale overview wording about direct `host.*`
  - remove stale overview wording about top-level global import visibility
  - align repository-level summaries with module-local imports and source-visible host ABI
  - align tracking terminology with the migrated normative specification
- Explicit exclusions:
  - no new normative semantics outside the main spec files

### Phase S7 — Final specification audit

- Goal: verify repository-wide consistency after the migration patches are complete.
- Files:
  - repository-wide audit
- Tasks:
  - consistency audit
  - terminology audit
  - example/spec alignment audit
  - invalid-example/spec alignment audit
  - hidden legacy wording audit
  - confirm no stale direct `host.*` language remains in active normative text
  - confirm no stale global-import wording remains in active normative text

## File impact summary

- Normative files expected to change later:
  - `SYNTAXE.md`
  - `SEMANTIQUE.md`
  - `HOST_ABI.md`

- Derived/supporting files expected to change later:
  - `EXAMPLES.md`
  - `INVALID_EXAMPLES.md`
  - `README.md`
  - `MODULE_REFACTOR_PLAN.md`

## Notes

- This file freezes tracking and architecture recording only.
- No normative spec rewrite is performed by this file.
- No implementation work is implied by this file.
