# HOST_ABI Migration Plan

## Scope

This document plans the future migration of `HOST_ABI.md` only.

This plan is limited to host-ABI model migration preparation for the frozen host ABI refactor.

This plan does not:

- rewrite normative ABI text yet
- rewrite `SYNTAXE.md` yet
- rewrite `SEMANTIQUE.md` yet
- define implementation strategy
- discuss NicolePy internals
- discuss runtime storage or execution internals
- define parser or AST details
- modify any other specification file

This document is planning/tracking text only.

## Current HOST_ABI model

Current `HOST_ABI.md` areas relevant to this migration:

- introductory model and principles
  - describes two directions: `export` from program to host, and direct callable `host.*` from host to program
  - treats host word effects as ABI metadata attached to direct `host.*`
- `# 2. export`
  - already aligned in large part with the current `SYNTAXE.md` and `SEMANTIQUE.md` export model
  - mostly concerns canonical host-visible names and export uniqueness
- `# 3. host.*`
  - treats `host.*` as the callable program-facing host surface
  - uses external contract entries such as `host.log` and `host.timezone`
  - assumes direct call semantics from Nicole source
- `# 4. Obligations de typage`
  - requires host contract declarations for names, signatures, availability, and effects
  - frames contract knowledge as external to Nicole source
  - includes “required” versus “optional” host words in the external contract
- `# 5. Obligations de contrat`
  - treats the ABI boundary as satisfaction of externally declared host bindings
- `# 6. Erreurs d’intégration`
  - frames integration failure around missing or mismatched external host bindings
- `# 7. Valeurs franchissant l’ABI`
  - defines the allowed ABI value set, including opaque host types
  - this area is mostly orthogonal to the host-surface refactor
- `# 8. Différences de niveau d’erreur`
  - includes runtime error wording tied to direct `host.*` presence/absence
- `# 9. Frontière de vérification et d’exécution`
  - treats the host contract as applied to an already verified program
  - does not yet model source-visible host ABI declarations

## Target source-visible ABI model

Frozen target assumptions taken from:

- `HOST_ABI_REFACTOR_PLAN.md`
- committed `SYNTAXE.md`
- committed `SEMANTIQUE.md`

Target ABI model:

- direct callable `host.*` is removed from the active language model
- `module @host` becomes the reserved source-visible declaration surface for required host capabilities
- `require` inside `module @host` declares:
  - capability path
  - stack signature
  - explicit ABI effect
  - importable symbol
- application modules consume host capabilities only through imports from the consolidated `@host` contract
- the runtime remains trusted
- the runtime must satisfy the declared source-visible ABI contract
- `@host` is fragmentable across files
- all `@host` fragments contribute to one deterministic consolidated host contract
- identical duplicate `require` declarations are allowed
- divergent duplicate `require` declarations are compile-time errors
- explicit `pure` and `dirty` are required in host ABI declarations
- opaque host types under `host.*` remain valid ABI/type vocabulary
- builtins remain out of scope

## Direct conflicts

- Conflict: direct host call surface
  - current rule: `host.*` is the program-facing callable host surface
  - target rule: host capability consumption happens via imports from `@host`
  - migration implication: every ABI section that treats direct `host.*` as the active call surface must be rewritten
  - severity: BLOCKER

- Conflict: external-only contract model
  - current rule: host contract entries are conceptually external to Nicole source
  - target rule: required host capabilities are declared directly in Nicole source through `module @host`
  - migration implication: ABI declaration structure must be rewritten around source-visible requirements
  - severity: BLOCKER

- Conflict: availability model
  - current rule: external contract distinguishes required versus optional host words while direct source calls imply requirement
  - target rule: source-visible `require` declarations define the host ABI surface the runtime must satisfy
  - migration implication: old optional/direct-call framing must be reconsidered and narrowed around the new declared contract
  - severity: MAJOR

- Conflict: effect metadata location
  - current rule: effect metadata belongs to direct `host.*` entries in the external contract
  - target rule: effect metadata is declared in source `require` entries and validated against runtime satisfaction
  - migration implication: effect sections must be rewritten around declared ABI requirements
  - severity: BLOCKER

- Conflict: fragmentation model
  - current rule: no source `@host` fragment consolidation exists
  - target rule: fragmentable `@host` contributes to a single deterministic host contract
  - migration implication: ABI document must define consolidated contract behavior
  - severity: BLOCKER

- Conflict: examples
  - current rule: examples use direct `msg host.log`
  - target rule: examples must show `module @host`, `require`, and explicit imports
  - migration implication: concept and example blocks need coordinated rewrite
  - severity: MAJOR

## `module @host`

Current ABI model:

- `@host` is not the declaration surface
- ABI names live in conceptual external contract entries

Target ABI role:

- `module @host` is the source-visible declaration module for required host capabilities
- `@host` is reserved
- `@host` is not a normal user module
- `@host` contributes ABI declarations only

ABI rewrite needs:

- define `@host` as the ABI declaration locus
- explain its relationship to the rest of the program
- keep detailed module semantics in `SEMANTIQUE.md`
- keep syntax shape in `SYNTAXE.md`
- use `HOST_ABI.md` to explain what the declarations mean at the ABI boundary

## `require`

Current ABI model:

- no `require` declaration exists in the ABI document
- contract entries are described in external pseudo-structured form

Target ABI role:

- `require` is the ABI declaration unit
- each `require` is the normative source-visible statement of one required host capability

ABI rewrite needs:

- define the normative meaning of one `require`
- define that the capability path is relative to `@host`
- define that the signature is part of the required ABI contract
- define that the effect is mandatory and explicit
- define that the declaration creates an importable host capability symbol for Nicole source

## ABI contract structure

Current ABI model:

- describes host entries using conceptual external records such as:
  - name
  - signature
  - availability
  - effect

Target ABI contract structure:

- a consolidated source-visible `@host` contract made of `require` declarations
- each declaration carries:
  - path
  - signature
  - effect
- the runtime is responsible for satisfying that contract

ABI rewrite needs:

- move from external-entry presentation to source-visible declaration presentation
- retain conceptual contract vocabulary without prescribing storage, serialization, or wire format
- decide how to restate or narrow the old availability concept under the new required-declaration model

## Runtime satisfaction model

Current ABI model:

- host contract must provide words and signatures matching what the program expects
- missing bindings can be detected statically or at execution time depending on knowledge

Target ABI model:

- the runtime must satisfy the consolidated declared `@host` contract
- source declaration checks compatibility at the language-spec level
- implementation correctness is still trusted, not proved by the language

ABI rewrite needs:

- restate runtime obligation in terms of the consolidated declared contract
- keep the distinction between:
  - source-visible contract declaration
  - runtime satisfaction of that declared contract
- avoid introducing runtime mechanism details

## Trusted runtime boundary

Current ABI model:

- runtime and host integration remain conceptual
- contract failures can be static or runtime errors

Target ABI model:

- runtime implementations remain trusted
- source declaration and static checking do not prove runtime correctness
- runtime failure to satisfy a valid declared contract remains an integration/runtime contract problem

ABI rewrite needs:

- make the trust boundary explicit
- preserve the distinction between validation of declarations and trust in execution behavior
- avoid VM, session, or framework expansion

## Fragmentable `@host` consolidation

Current ABI model:

- no source consolidation model exists

Target ABI model:

- multiple `module @host` fragments are allowed
- all fragments contribute to one deterministic consolidated host contract
- file order must not affect meaning

ABI rewrite needs:

- define consolidation conceptually
- state that only `@host` participates in this special consolidation
- avoid implementation-pass or storage-algorithm details

## Duplicate identical declarations

Current ABI model:

- no duplicate `require` concept exists

Target ABI model:

- identical duplicate `require` declarations are allowed

ABI rewrite needs:

- define what “identical” means at the ABI-spec level:
  - same capability path
  - same signature
  - same effect
- define the contract consequence:
  - allowed as one consolidated requirement
- avoid turning this into implementation-specific merge mechanics

## Divergent declaration errors

Current ABI model:

- no divergent `require` concept exists

Target ABI model:

- divergent declarations for the same capability path are compile-time errors

ABI rewrite needs:

- define divergence at the ABI-spec level
- describe the outcome as contract invalidity / compile-time rejection
- keep exact diagnostic wording open unless already frozen elsewhere

## Explicit `pure` / `dirty`

Current ABI model:

- effect metadata is mandatory in conceptual host entries
- `pure` and `dirty` are ABI properties of direct host words

Target ABI model:

- every `require` must declare explicit `pure` or `dirty`
- `pure` remains ABI-only source syntax
- `dirty` remains the general user-word effect annotation elsewhere, but in `HOST_ABI.md` it is part of the host contract declaration

ABI rewrite needs:

- move effect declaration examples from external contract entries into `require`
- preserve mandatory explicit effect declaration
- keep the boundary clear between ABI effects and ordinary Nicole word annotations

## Opaque host types

Current ABI model:

- opaque host types live under `host.*`
- they are named, nominal, and externally declared
- they can cross the ABI under existing value-boundary constraints

Target ABI model:

- opaque host type vocabulary under `host.*` remains valid
- host capability declarations may expose those types through source-visible `require` signatures

ABI rewrite needs:

- preserve opaque type rules unless they depend specifically on direct callable `host.*`
- update examples so opaque types appear in `require` signatures rather than external direct-host entries when appropriate

## Removal of direct callable `host.*`

Current ABI model:

- direct host words are the active program-facing interface
- optionality and examples are framed around direct calls

Target ABI model:

- direct callable `host.*` is removed from the active language model
- `host.*` remains ABI/type vocabulary, not the normal source call surface

ABI rewrite needs:

- replace direct-call prose with source-visible declaration + import-mediated usage references
- preserve `host.*` type vocabulary where still valid
- align examples with committed `SYNTAXE.md` and `SEMANTIQUE.md`

## Diagnostics and integration errors

Current ABI model:

- integration errors cover missing host words, mismatched signatures, and unsatisfied links
- static versus runtime detection depends on when the contract is known

Target ABI model:

- integration errors must also account for source-visible declaration inconsistencies
- divergent `require` declarations are compile-time errors
- runtime inability to satisfy a valid consolidated declared contract remains an integration/runtime-contract failure

ABI rewrite needs:

- separate:
  - invalid declared host contract
  - invalid source use relative to the declared contract
  - runtime failure to satisfy a valid declared contract
- keep `Result` distinct from the linkage/satisfaction mechanism

## Examples impacted

`HOST_ABI.md` examples and wording likely requiring migration:

- introductory bullets that say `host.*` is callable by the program
- external record examples like `host.log` / `host.timezone`
- `msg host.log` examples in export and host usage sections
- optional host-word wording tied to direct source calls
- any wording that describes host capability names as known only outside Nicole source

## Suggested rewrite ordering

1. Rewrite the document introduction and principles around the source-visible ABI model.
2. Keep `export` largely intact, performing only consistency updates where needed.
3. Replace the direct `host.*` callable section with `module @host` plus `require`.
4. Rewrite contract-structure wording around consolidated source-visible declarations.
5. Rewrite type-obligation sections so host capability declarations and opaque type declarations align with the new model.
6. Rewrite contract-obligation sections around runtime satisfaction of the declared consolidated contract.
7. Rewrite integration-error sections to distinguish declaration errors from runtime satisfaction failures.
8. Rewrite ABI value-boundary examples and host-facing examples.
9. Sweep terminology for old direct-host phrasing and optionality wording that no longer matches the frozen model.

Why this order minimizes inconsistency risk:

- the document’s top-level model must change before local rules can be interpreted correctly
- `export` can remain stable while the host-facing side is replaced
- diagnostics and runtime-trust wording depend on the declared-contract model being stated first
- examples should be updated after the normative contract structure is rewritten

## Risks

- mixed-model risk: leaving both direct callable `host.*` and source-visible `@host` declarations in the same ABI document would create contradictory authority
- scope-drift risk: too much semantic detail could leak from `SEMANTIQUE.md` into `HOST_ABI.md`
- implementation-drift risk: consolidation wording could accidentally turn into parser/pass/runtime algorithm detail
- optionality-drift risk: retaining the old “optional host word” framing without adapting it to the new declared-contract model could reintroduce direct-call assumptions
- type-drift risk: overcorrecting direct-call removal could accidentally damage the still-valid opaque host type vocabulary under `host.*`

## Open questions

Only unresolved ABI-level questions still within the frozen architecture:

- exact normative wording for duplicate-identical `require` handling in the consolidated contract
- exact normative wording for divergent `require` declaration errors
- whether the old “optional” availability concept should be retained as conceptual metadata in `HOST_ABI.md` or removed from the active v1 host-capability model because direct callable optional host words no longer exist
- exact wording for the boundary between source-declared ABI compatibility and trusted runtime satisfaction

## Recommendation

CONTINUE_SPEC_INVESTIGATION

Reason:

- the target ABI model is frozen strongly enough to plan the rewrite
- the impacted `HOST_ABI.md` regions are now identifiable and file-oriented
- a few wording decisions remain, especially around availability metadata and duplicate-handling formulation, before issuing a safe normative rewrite prompt
