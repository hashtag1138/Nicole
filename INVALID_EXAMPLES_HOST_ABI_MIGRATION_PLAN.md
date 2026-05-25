# INVALID_EXAMPLES Host ABI Migration Plan

## Scope

This document plans the future migration of `INVALID_EXAMPLES.md` only.

This plan is limited to invalid-example migration preparation after the committed host ABI refactor in:

- `SYNTAXE.md`
- `SEMANTIQUE.md`
- `HOST_ABI.md`
- `EXAMPLES.md`

This plan does not:

- rewrite `INVALID_EXAMPLES.md` yet
- rewrite normative syntax, semantics, ABI, or valid examples
- define implementation strategy
- discuss NicolePy internals
- modify any other specification file

This document is planning/tracking text only.

## Current invalid-example model summary

Current `INVALID_EXAMPLES.md` mixes three different host-related surfaces:

- invalid cases tied to the old direct callable `host.*` model
- legacy import / alias invalid cases written against pre-S1 visibility rules
- opaque host type invalid cases that still remain broadly valid under the new ABI model

Current areas most affected by the host ABI migration:

- `## 0bis. Résolution et imports (Phase 3)`
  - still contains an invalid `module @host` example that is now obsolete
  - still phrases alias/import invalidity with pre-S1 assumptions in a few places
- `## 3. Branches incompatibles`
  - `Garde conditionnelle dirty interdite` still uses direct `host.log`
- `## 7. host.*`
  - built around the old direct-call and external-only host model
- `## 10. Pureté et effet dirty invalides`
  - still uses direct `host.log` as the impurity source
- legacy syntax-invalid host declarations near the end of the file
  - `extern host.log`
  - `extern type host.io.FileHandle`

Host-neutral invalid sections likely unaffected:

- top-level user-definition rejection
- non-host typing errors
- return mismatches
- non-host `if` / `case` incompatibilities
- quotation arity/type errors unrelated to host ABI
- collection builtin errors unrelated to host ABI
- subword privacy errors
- non-host reserved-word violations

## Invalid examples still using old direct callable `host.*`

Old-model invalid examples currently present:

- `## 3. Branches incompatibles`
  - `Garde conditionnelle dirty interdite`
- `## 7. host.*`
  - `Appel d’un mot hôte non déclaré`
  - `Définition directe d’un mot host.*`
  - `Binding hôte supposé optionnel utilisé comme Result`
  - quotation-through-host examples using `host.run-later`
- `## 10. Pureté et effet dirty invalides`
  - `Annotation dirty manquante sur appel hôte dirty`
  - `Mot pur appelant un mot Nicole dirty`
  - `Export pur appelant du code dirty`
  - `Construction de DirtyQuote dans une frame pure`
- syntax-invalid legacy forms
  - `extern host.log`

Migration implication:

- these examples cannot remain as active invalid examples in their current form because they rely on a valid-language surface that no longer exists
- they must either disappear or be rewritten around `module @host`, `require`, and imported host capabilities

## Invalid old-model examples that must disappear

The following categories should be removed from the active invalid corpus rather than patched in place:

- invalid examples whose sole premise is “direct callable `host.*` exists but fails in some old way”
- invalid examples that rely on old external host-contract record formatting as if it were still the active user-facing surface
- `module @host` invalidity examples based on the old rule that `@host` was forbidden

Concrete removal targets:

- `module @host` under `## 0bis. Résolution et imports (Phase 3)`
- old direct-host section title `## 7. host.*`
- examples that treat missing direct host words as the primary invalid surface instead of invalid imported capability use

Replacement rule:

- replace these with invalid cases that demonstrate the new ABI model’s explicit declaration/import rules

## New invalid examples required by the new ABI model

S5 needs new invalid examples for the committed host model.

Required categories:

- direct source use of `host.*` after S1/S2/S3
- `require` outside `module @host`
- invalid content inside `module @host`
  - imports
  - exports
  - word definitions
  - executable logic
  - constants
  - variables
- missing explicit ABI effect on `require`
- illegal use of `pure` outside ABI declaration surface
- duplicate divergent `@host` declarations for the same capability path
- duplicate identical `@host` declarations if the file chooses to mention that they are allowed, not rejected
- host capability import from `@host` without matching declaration
- invalid module-local import placement for host capability imports
- invalid qualified alias forms
- reserved-root alias collisions for host capability imports

## Invalid examples affected by module-local imports

Current import-invalid examples needing review:

- `Import wildcard interdit`
- `Collision d’alias d’import`
- `Import sans alias n’expose pas le nom court`
- `Référence externe qualifiée sans import`
- `Cycle d’import interdit`

S5 impact:

- several current import-invalid examples are structurally obsolete because they are written with top-level imports, and top-level imports are no longer a valid source surface after S1
- these cases must not be described as mere wording cleanup; when their underlying purpose remains valid, they need new module-local scaffolding
- the plan must distinguish three subgroups:
  - examples to replace with new module-local invalid scaffolding
  - examples where top-level import is now itself the invalid condition
  - examples outside import placement that remain unchanged

Examples to replace with new module-local invalid scaffolding:

- `Import wildcard interdit`
  - keep the wildcard-invalid purpose, but re-scaffold it inside a module-local import context
- `Collision d’alias d’import`
  - keep the alias-collision purpose, but re-scaffold both imports inside the same module where alias visibility is now defined
- `Import sans alias n’expose pas le nom court`
  - keep the short-name-visibility purpose, but re-scaffold it with the import placed inside the containing module
- `Cycle d’import interdit`
  - keep the cyclic-import purpose, but re-scaffold it without relying on now-obsolete top-level import placement

Examples where top-level import is now itself the invalid condition:

- any existing host-capability or user-module import example written at top level should either be removed or rewritten so the rejection target is explicitly “top-level import is forbidden”
- S5 should add at least one explicit invalid top-level import example under the new model

Examples unrelated to import placement that remain unchanged in principle:

- `Référence externe qualifiée sans import`
  - this remains useful once aligned with the committed import rules, because its invalidity is missing import visibility rather than legacy top-level placement

Additional new host-specific import-placement invalids still needed:

- top-level host capability import
- host capability import inside a word body
- import after a word definition in the same module

Recommended additions:

- invalid top-level `import @host.console.log as console.log`
- invalid in-body `import @host.console.log as console.log`
- invalid late import after a word definition

## Invalid examples affected by alias locality

Current alias invalids already present:

- `Collision d’alias d’import`
- `Alias sur racine réservée`

S5 impact:

- keep the existing collision and reserved-root invalids
- rewrite wording so alias visibility is clearly module-local rather than compilation-unit-global
- add host-ABI-specific alias-locality cases where useful:
  - alias used outside the module that imported it
  - second module assuming visibility of `console.log` alias declared elsewhere

## Invalid examples affected by qualified aliases

Qualified aliases are now valid, so S5 must distinguish:

- examples that used to be invalid but are no longer invalid
- new invalid forms of qualified aliases

Required invalid categories:

- alias beginning with `@`
- alias occupying reserved root `host`
- malformed dotted alias
- treating a qualified alias as if it were a module reference category rather than a local alias name

Recommended examples:

- `import @host.console.log as @console.log`
- `import @host.console.log as host`
- `import @host.console.log as host.log`

## Invalid examples involving `module @host`

Current obsolete case:

- `Module sur racine réservée` using `module @host`

This case must be removed from the active invalid set because `module @host` is now reserved and valid.

S5 needs replacement `@host` invalids such as:

- nested `module @host`
- `module @host` with ordinary word definition
- `module @host` with `export`
- `module @host` with `import`
- `module @host` with executable logic

These examples should be phrased as violations of the reserved ABI-only role of `@host`, not as generic reserved-root occupancy errors.

## Invalid examples involving `require`

No dedicated `require` invalid corpus exists yet.

Required new invalid categories:

- `require` outside `module @host`
- `require` missing effect
- `require` using illegal non-ABI placement
- `require` attempting a non-canonical or malformed capability path where the syntax/spec requires a relative capability path
- `require` attempting to treat `pure` as a general modifier elsewhere

The purpose here is to make the new ABI declaration surface rejectable in explicit, source-visible ways.

## Duplicate/divergent `@host` declarations

S5 must introduce invalid examples for divergent duplicates.

Required divergent categories:

- same capability path, different signature
- same capability path, same signature, different effect

Optional mention:

- identical duplicates are allowed under the frozen architecture and therefore should not appear as invalid examples

Recommended framing:

- keep the example file-oriented or fragment-oriented
- make clear that the error is about one consolidated `@host` contract with incompatible declarations

## ABI effect declaration failures

Current effect-invalid cases in `## 10. Pureté et effet dirty invalides` remain useful in principle, but their host source must be updated.

Existing cases to rewrite, not remove:

- missing `dirty` annotation because of host capability use
- pure frame calling dirty code transitively
- pure export calling dirty code
- pure frame constructing or calling dirty quotations sourced from host capability use

Additional new ABI-surface invalids:

- `require console.log { msg:String -- }` with no explicit effect
- any illustrative misuse of `pure` as an ordinary word modifier if not already covered elsewhere

## Examples intentionally unchanged

These invalid categories should remain unchanged except for minimal wording cleanup if needed:

- non-host typing errors
- non-host return mismatch errors
- non-host `if` / `case` branch incompatibilities
- collection builtin invalids unrelated to host ABI
- subword privacy and no-capture invalids
- `?` propagation invalids unrelated to host ABI
- reserved builtin redefinition invalids for `list.*`, `map.*`, `result.*`

Reason:

- they remain valid under the committed host ABI model
- changing them would expand S5 beyond host-ABI alignment

## Diagnostics categories impacted

S5 must help illustrate the new diagnostic families now implied by the committed spec:

- direct `host.*` use is no longer valid source surface
- invalid `require` placement
- invalid `@host` body content
- missing ABI effect declaration
- invalid host capability import visibility or placement
- invalid qualified alias form
- divergent duplicate `@host` declarations
- undeclared imported host capability use
- dirty propagation sourced from imported host capabilities rather than direct host calls

The invalid corpus should not try to freeze final diagnostic wording, but it should make the rejected category unmistakable.

## Suggested rewrite ordering

1. Remove obsolete invalids tied to forbidden `module @host`.
2. Replace the old direct-host invalid section with a new host-ABI invalid section centered on `@host`, `require`, and imported capabilities.
3. Add invalid `require` placement and missing-effect cases.
4. Add invalid `@host` body-content cases.
5. Add divergent duplicate `@host` fragment cases.
6. Update import and alias invalids for module-local visibility and qualified alias rules.
7. Rewrite host-dependent dirty invalids to source impurity from imported capabilities.
8. Sweep the file for residual direct-call `host.*` assumptions, keeping only opaque-type vocabulary where valid.
9. Run a final consistency pass against committed `SYNTAXE.md`, `SEMANTIQUE.md`, `HOST_ABI.md`, and `EXAMPLES.md`.

Why this order is safer:

- obsolete invalids must disappear before new `@host` invalids are introduced
- the new ABI declaration surface should be established before downstream dirty/import diagnostics are rewritten
- dirty invalids depend on the new host capability model already being visible in the file
- host-neutral invalids can remain untouched unless residual wording drift is found

## Risks

- mixed-model risk:
  - leaving old direct `host.*` invalids beside new `@host` invalids would create contradictory rejection guidance
- over-removal risk:
  - deleting host-sensitive invalids without adding the new ABI-surface invalids would weaken the rejection corpus
- scope-creep risk:
  - broad editorial cleanup could accidentally rewrite stable non-host invalids
- alias-confusion risk:
  - failing to distinguish valid qualified aliases from invalid qualified-alias forms could reintroduce ambiguity
- diagnostics-drift risk:
  - examples might imply stronger or narrower diagnostics wording than the normative docs currently guarantee
- opaque-type drift risk:
  - overcorrecting `host.*` removal could accidentally erase still-valid invalid cases about opaque host types

## Recommendation

CONTINUE_SPEC_INVESTIGATION

Reason:

- the obsolete invalid host-model cases are now clearly separable from the new required ABI-surface invalids
- the normative host model is already committed
- the next step is a bounded invalid-example rewrite, but it should be prompted with tight category boundaries so unchanged invalids stay untouched
