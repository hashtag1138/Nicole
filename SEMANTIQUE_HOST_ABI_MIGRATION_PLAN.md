# SEMANTIQUE Host ABI Migration Plan

## Scope

This document plans the future migration of `SEMANTIQUE.md` only.

This plan is limited to semantic-model migration preparation for the frozen host ABI refactor.

This plan does not:

- rewrite normative semantic text yet
- rewrite `HOST_ABI.md` yet
- rewrite `SYNTAXE.md` yet
- define implementation strategy
- discuss NicolePy internals
- modify any other specification file

This document is planning/tracking text only.

## Current semantic model summary

Current `SEMANTIQUE.md` areas relevant to this migration:

- `## Formes réservées et builtins`
  - treats `host.*` as part of the visible reserved builtin namespace
  - includes `host.*` in the visible resolution space
- `# 3. Résolution des appels`
  - assumes external user calls use `@module.word` with matching imports
  - assumes imports exist only at top-level
  - assumes import aliases are visible at compilation-unit scope after textual inclusion
  - forbids a user module named `@host`
  - includes `host.*` in the normal resolution order as callable reserved names
- `## Effets pure / dirty en v1`
  - states that only `host.*` bindings introduce impurity directly
  - treats host effect sourcing as attached to direct `host.*` bindings
- `# 8. Frontière compile-time / runtime`
  - treats missing host words as runtime-contract violations at the host boundary
  - still frames host lookup in terms of direct `host.*` calls
- `# 9. Contrat hôte`
  - presents two directions: `export` and direct callable `host.*`
  - treats `host.*` as the host-facing semantic lookup surface
  - models host-word availability, effect sourcing, and opaque-type circulation through that direct-call model
- `# 6. Quotations et call`
  - includes dirty propagation rules that are correct in shape, but currently inherit host impurity through direct `host.*`
- `# 15. Types v1` in `SYNTAXE.md`, plus matching semantic wording
  - still use `host.*` for opaque host type names; this remains relevant and is not being removed by S2

## Target semantic model summary

Frozen target semantic assumptions taken from:

- `HOST_ABI_REFACTOR_PLAN.md`
- `SYNTAXE_HOST_ABI_MIGRATION_PLAN.md`
- updated `SYNTAXE.md`

Target semantic model:

- direct callable `host.*` is removed from the language model
- `@host` is a reserved ABI declaration module, not a normal user module
- `require` declarations in `module @host` define source-visible host capabilities
- application modules access host capabilities only through explicit imports from `@host`
- imports are module-local
- aliases are module-local
- qualified aliases are valid local alias names
- host capability lookup is driven by imported `@host` declarations rather than ambient global host names
- every host capability has an explicit ABI effect classification
- `pure` in this workflow is ABI-declaration-only source syntax, not a general word modifier
- `@host` is fragmentable across files
- `@host` fragment merge is deterministic
- identical duplicate `require` declarations are allowed
- divergent duplicate `require` declarations for the same capability path are compile-time errors
- builtins `list.*`, `map.*`, and `result.*` remain unchanged
- host opaque types under `host.*` remain part of the ABI surface

## Direct semantic conflicts

- Conflict: direct host lookup model
  - current rule: direct `host.*` calls are normal callable names in semantic resolution
  - target rule: host capabilities are callable only after explicit import from `@host`
  - migration implication: call-resolution and host-lookup sections must stop treating `host.*` as ambient callable names
  - severity: BLOCKER

- Conflict: import visibility model
  - current rule: imports are top-level declarations and aliases propagate at compilation-unit scope
  - target rule: imports and aliases are module-local
  - migration implication: semantic visibility, collision, and lookup rules must be rewritten together
  - severity: BLOCKER

- Conflict: reserved module treatment
  - current rule: user modules cannot be `@host`, and all module names are unique
  - target rule: reserved `module @host` is legal and uniquely fragmentable
  - migration implication: semantic module collection and symbol-table wording must carve out the `@host` exception
  - severity: BLOCKER

- Conflict: effect sourcing
  - current rule: impurity enters the program directly through `host.*` bindings
  - target rule: impurity enters through imported host capabilities declared by `require`
  - migration implication: effect propagation text must be reworded around imported capability bindings rather than ambient host names
  - severity: BLOCKER

- Conflict: host contract visibility
  - current rule: host contract knowledge is primarily external to Nicole source
  - target rule: host capability declarations are source-visible in `module @host`
  - migration implication: semantic contract-validation wording must acknowledge source-visible ABI declarations
  - severity: BLOCKER

- Conflict: diagnostics boundary
  - current rule: missing `host.*` is described as a host-boundary failure from direct calls
  - target rule: capability declaration, import visibility, and merged `@host` compatibility must be part of the static semantic model
  - migration implication: diagnostics sections must distinguish source-level declaration errors from runtime satisfaction failures
  - severity: MAJOR

- Conflict: examples and host-facing prose
  - current rule: semantic examples use direct `host.log`
  - target rule: examples must show `module @host`, `require`, and explicit module-local imports
  - migration implication: example blocks and explanatory prose require coordinated rewrite
  - severity: MAJOR

## Name resolution changes

Current semantic resolution order in `SEMANTIQUE.md` assumes:

- locals
- same-module short names
- visible import aliases
- explicit `@module.word`
- reserved namespaces including callable `host.*`

Target semantic resolution needs to become:

- locals in the current frame
- words defined in the current module via short name
- module-local imported aliases, including qualified aliases
- explicit imported external references allowed by the module-local import surface
- language builtins and reserved non-host namespaces

Required semantic rewrite points:

- remove direct callable `host.*` from the normal ambient resolution order
- define how imported host capabilities participate in visible-name resolution
- keep `@module.word` as the explicit external user-module reference form
- distinguish imported host capability aliases from explicit module references
- preserve visible-name uniqueness under the new imported host model

## Module-local import semantics

Current semantic model:

- imports are top-level declarations
- aliases become visible across the importing compilation unit
- textual inclusion does not create a distinct alias scope

Target semantic model:

- imports belong to the containing module only
- import visibility does not escape that module
- host capability imports follow the same visibility model
- import ordering before word definitions is already syntax-level; S2 must define the semantic consequences of that local scope

Semantic rewrite needs:

- replace compilation-unit alias scope with module-contained import scope
- restate collision rules in module-local terms
- make clear that import declarations are compilation-time declarations with no stack effect
- avoid redefining `include` semantics beyond what is required to remove stale global-alias wording

## Alias visibility semantics

Current semantic model:

- aliases are simple names
- aliases are visible after textual inclusion in the compilation unit
- aliases participate in visible-name collisions globally

Target semantic model:

- aliases may be simple or qualified
- aliases are visible only in the module that declares them
- qualified aliases remain alias names, not module references
- aliases cannot start with `@`
- aliases cannot occupy reserved roots such as `host`

Semantic rewrite needs:

- explicitly distinguish qualified alias names from `@module.word`
- define collision behavior for dotted alias names in module-local scope
- ensure alias-based lookup and explicit-module lookup do not collapse into one semantic category

## `@host` reserved module semantics

Current semantic model:

- `@host` is forbidden as a user module name
- all module names are unique in the compilation unit

Target semantic model:

- `@host` is reserved and legal
- `@host` is not a normal user module
- `@host` contributes declarations only
- only `@host` may appear in multiple fragments

Semantic rewrite needs:

- define semantic collection of `@host` fragments before ordinary module-body validation
- preserve normal uniqueness rules for every other module
- state that normal user-module semantics do not apply wholesale to `@host`
- defer detailed ABI merge algorithm wording to `HOST_ABI.md` where possible while still defining the semantic preconditions that `SEMANTIQUE.md` depends on

## `require` semantic role

Current semantic model:

- no `require` declaration exists
- host capability semantics begin at direct call sites to `host.*`

Target semantic role of `require`:

- declares a required host capability in source
- contributes the capability name, stack signature, and effect classification
- defines what may later be imported from `@host`

Semantic rewrite needs:

- define `require` as a declaration that contributes symbols to the host capability namespace
- define that capability availability is checked against the consolidated `@host` contract, not discovered ad hoc from direct call syntax
- define that `require` participates in static compatibility checking before ordinary host-capability use is validated

## Fragmentable `@host` merge semantics

Current semantic model:

- no fragmentable host declaration module exists

Target semantic model:

- multiple `module @host` fragments are allowed
- semantic result is one deterministic consolidated host ABI contract
- identical duplicates are allowed
- divergent duplicates are rejected

Semantic rewrite needs:

- define conceptual pre-resolution merge or consolidation step for `@host`
- define that file order does not affect merged meaning
- define the semantic consequence of duplicate identical declarations
- define the semantic consequence of duplicate divergent declarations
- avoid over-specifying storage, runtime layout, or implementation mechanics

## Host capability lookup

Current semantic model:

- direct `host.*` names resolve as known host words
- signatures and effects are attached to those direct names

Target semantic model:

- host capability use is legal only through imported symbols sourced from `@host`
- the resolved symbol ultimately points back to a declared capability path in the consolidated host contract
- source-visible imports expose the dependency path explicitly in Nicole code

Semantic rewrite needs:

- replace direct-call lookup with import-mediated host-capability lookup
- define the relationship between:
  - declared capability path in `@host`
  - imported symbol in an application module
  - local alias used at call sites
- preserve opaque-type terminology under `host.*` for type names where applicable

## Effect sourcing changes

Current semantic model:

- only direct `host.*` bindings introduce impurity directly
- host effect metadata is attached to ambient host words

Target semantic model:

- impurity enters via imported host capabilities whose effects were declared in `require`
- `pure` and `dirty` for host capabilities come from ABI declarations, not from local user-word annotations
- user-word effect propagation rules remain structurally the same after the new source of host effects is substituted

Semantic rewrite needs:

- rewrite the “only host bindings introduce impurity directly” wording around imported declared capabilities
- preserve the existing transitive propagation model for user words and quotations
- keep `dirty` as the only general user-word effect annotation
- explicitly state that `pure` in this workflow does not become a general source annotation for Nicole words

## Removal of direct `host.*`

Current semantic model still treats:

- direct `host.*` calls as valid
- missing direct host words as host-boundary failures
- effect propagation as entering through ambient host words

S2 rewrite needs to remove:

- direct callable `host.*` as an active semantic surface
- examples whose host usage depends on direct `host.log`
- any wording that implies a program can acquire host behavior without importing from `@host`

What remains valid after S2:

- `host.*` as opaque host type terminology
- ABI-facing terminology tied to host-defined opaque types

## Builtins unchanged

S2 must preserve the current semantic treatment of:

- `list.*`
- `map.*`
- `result.*`

This means:

- no builtin modularization
- no new builtin import model
- no change to collection semantics merely because host capability resolution changes

## Diagnostics implications

Semantic diagnostics likely needing new or revised treatment:

- use of a host capability without a corresponding module-local import
- import of a host capability not declared in consolidated `@host`
- duplicate divergent `require` declarations for one capability path
- duplicate identical `require` declarations, depending on final chosen diagnostic posture
- host capability effect mismatch between declaration and use expectations
- illegal assumption that direct `host.*` remains callable
- ambiguity or collision involving qualified aliases in module-local scope
- host contract unsatisfied by the runtime after source-level ABI declaration has been validated

Diagnostic boundary to preserve:

- source-declaration and visibility failures are compile-time semantic errors
- runtime inability to satisfy an already-declared host contract remains a runtime-contract error

## Examples and wording impacted

`SEMANTIQUE.md` areas likely requiring example or prose migration:

- `## Formes réservées et builtins`
- `# 3. Résolution des appels`
- `## Effets pure / dirty en v1`
- `# 8. Frontière compile-time / runtime`
- `# 9. Contrat hôte`
- any example block using `host.log`
- any wording that says imports are top-level
- any wording that says alias scope follows the whole compilation unit
- any wording that forbids `@host`
- any wording that says host-word signatures are only externally known rather than source-visible

## Suggested rewrite ordering

1. Update the semantic statement of the active host model.
2. Rewrite call resolution and visible-name lookup around module-local imports and imported host capabilities.
3. Rewrite alias visibility and collision semantics in module-local terms.
4. Introduce the reserved semantic role of `module @host` and the `@host` fragmentability exception.
5. Introduce the semantic role of `require` declarations and the consolidated host contract.
6. Rewrite host capability lookup from ambient direct names to import-mediated capability bindings.
7. Rewrite effect sourcing for host capabilities while preserving existing user-word propagation structure.
8. Rewrite compile-time versus runtime host-contract diagnostics.
9. Replace direct-host examples and stale explanatory wording.
10. Run a terminology and consistency sweep for old-model host wording.

Why this order minimizes inconsistency risk:

- resolution and visibility are upstream of effect propagation
- host contract semantics depend on the imported-symbol model being defined first
- diagnostics wording is easier to rewrite once declaration, lookup, and effect sources are settled
- example migration should come after the governing semantic rules are restated

## Risks

- mixed-model risk: leaving both direct `host.*` lookup and imported host capability lookup in the same semantic chapter would create contradictory authority
- scope drift risk: partial replacement of alias rules could leave compilation-unit and module-local visibility both implied
- fragmentability drift risk: wording about repeated `module @host` could accidentally broaden to ordinary user modules
- effect drift risk: rewriting host impurity sourcing imprecisely could look like a change to the general `dirty` system rather than a host-model refactor
- diagnostics drift risk: compile-time declaration errors and runtime host-satisfaction failures could be conflated
- type-surface drift risk: removing too much `host.*` wording could accidentally damage the still-valid opaque host type model

## Open questions

Only unresolved semantic questions that remain within the frozen architecture:

- exact semantic staging of `@host` consolidation relative to ordinary module-body validation
- exact wording for duplicate-identical `require` declarations: silent coalescing versus explicit non-fatal duplicate reporting
- exact wording for the boundary between compile-time ABI compatibility checking and runtime contract-satisfaction failure
- exact semantic wording needed to relate an imported alias such as `console.log` to its underlying declared capability path without making the alias sound like a module reference

## Recommendation

CONTINUE_SPEC_INVESTIGATION

Reason:

- the architecture is already frozen strongly enough for S2 planning
- the semantic rewrite scope is now identifiable and file-oriented
- a few wording and staging questions remain before a safe normative rewrite prompt should be issued
