# SYNTAXE Host ABI Migration Plan

## Scope

This document plans the future migration of `SYNTAXE.md` only.

This plan is limited to syntax-surface migration preparation for the frozen host ABI refactor.

This plan does not:

- rewrite normative syntax yet
- rewrite semantic rules yet
- rewrite the runtime model yet
- modify any other specification file

This document is planning/tracking text only.

## Current syntax model summary

Current `SYNTAXE.md` areas relevant to this migration:

- `## Lexique minimal v1`
  - defines `.` as a structural separator and `@` as module-reference syntax
  - defines `qualified_name`, `module_ref`, and `module_qualified_name`
- `## Formes réservées v1`
  - reserves `module`, `end-module`, `import`, `include`, `dirty`
  - reserves namespace roots `host`, `list`, `map`, `result`
  - explicitly forbids a user module named `@host`
  - explicitly keeps `host.*` valid as reserved qualified builtin-style forms
- `# 2. Visibilité interne, export et contrats hôte`
  - all user words are inside `module @... end-module`
  - modules are top-level only and unique in the compilation unit
  - external user references use `@module.word`
  - local short-name access is allowed within the defining module
- `## Fondations grammaticales modules/imports/includes (Phases 1-3)`
  - import forms are top-level
  - aliases are visible at compilation-unit scope after textual inclusion
  - targeted imports support only simple aliases
  - wildcard imports do not exist
- `# 11. Mots fournis par l’hôte`
  - direct `host.*` words are legal source forms
  - direct `host.*` calls are treated as required host bindings
  - host words are described as outside source declarations
- `# 28. Exemple complet valide` and `# 29. Résumé de la syntaxe`
  - still show direct `host.*` usage in valid syntax examples
- `# Séparation future des documents`
  - still summarizes `HOST_ABI.md` as handling `host.*`, events, and exports under the current model

## Frozen target syntax model summary

Frozen target syntax assumptions taken from `HOST_ABI_REFACTOR_PLAN.md`:

- direct `host.*` access is removed from the language model
- `@host` becomes a reserved ABI declaration module
- `@host` is not a normal user module
- `require` becomes a language declaration form
- `require` is allowed only inside `module @host`
- host ABI becomes source-visible
- application modules import host capabilities explicitly
- imports become module-local
- aliases become module-local
- qualified aliases are allowed
- simple aliases remain allowed
- explicit ABI effects are required
- `pure` is explicitly expressible in host ABI declarations
- `@host` is fragmentable across files
- fragment merge must be deterministic
- identical duplicate declarations are allowed
- divergent duplicate declarations are compile-time errors
- builtins remain out of scope

## Frozen S1 syntax-surface decisions

- Qualified aliases are valid.
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
- Compact form is preferred in simple examples.
- Multiline form remains allowed for readability.
- Multiple `module @host` fragments are allowed.
- The fragmentability exception applies only to `@host`.
- No other module becomes fragmentable.

## Direct syntax conflicts

- Conflict: reserved module root
  - current rule: `@host` is forbidden as a user module name and `host` is a reserved root with `host.*` kept valid
  - target rule: `module @host` becomes a reserved legal declaration form
  - migration implication: reserved-root wording must distinguish forbidden user occupancy from reserved language-owned `@host`
  - severity: BLOCKER

- Conflict: missing declaration form
  - current rule: `require` is not part of reserved forms or declaration grammar
  - target rule: `require` becomes a first-class declaration form
  - migration implication: reserved-form tables and declaration grammar must be expanded
  - severity: BLOCKER

- Conflict: host access model
  - current rule: direct `host.*` words are valid source syntax
  - target rule: direct `host.*` access is removed
  - migration implication: all syntax wording that treats `host.*` as a callable source form must be replaced
  - severity: BLOCKER

- Conflict: import placement
  - current rule: imports exist only at top-level
  - target rule: imports are legal only inside modules, appear before word definitions, and are not legal inside word bodies
  - migration implication: import grammar and all placement wording must be rewritten together; partial wording would be contradictory
  - severity: BLOCKER

- Conflict: alias visibility
  - current rule: aliases are visible at compilation-unit scope after textual inclusion
  - target rule: aliases are module-local
  - migration implication: current alias-scope wording becomes wrong even before semantic elaboration
  - severity: BLOCKER

- Conflict: alias shape
  - current rule: import aliases are simple names such as `t` or `split`
  - target rule: qualified aliases such as `console.log` are allowed, remain local alias names, are not module references, cannot start with `@`, and cannot occupy reserved roots
  - migration implication: alias grammar must admit dotted alias targets explicitly and distinguish them from module-reference syntax
  - severity: BLOCKER

- Conflict: module uniqueness versus reserved fragmentability
  - current rule: module names are unique in the compilation unit
  - target rule: `@host` may appear in multiple fragments across files
  - migration implication: module grammar prose must carve out the reserved `@host` exception without reopening general user-module duplication
  - severity: BLOCKER

- Conflict: effect expressibility in ABI declarations
  - current rule: `dirty` is source-visible, but `pure` is not a source declaration keyword in syntax tables
  - target rule: every `require` must express `dirty` or `pure`, and `pure` is legal only in ABI declaration surface
  - migration implication: syntax text must define where `pure` is legal while explicitly preventing generalization to ordinary Nicole declaration modifiers
  - severity: MAJOR

- Conflict: `require` surface shape
  - current rule: there is no `require` declaration syntax at all
  - target rule: canonical form is `require console.log { msg:String -- } dirty`, with equivalent multiline form also valid
  - migration implication: declaration grammar and examples must be updated in a way that keeps both forms aligned and clearly equivalent
  - severity: BLOCKER

- Conflict: example surface
  - current rule: valid syntax examples still use direct `host.*`
  - target rule: examples must show `module @host`, `require`, and module-local imports
  - migration implication: syntax examples and summaries require coordinated replacement
  - severity: MAJOR

## Required grammar changes

- reserved keyword table
  - add `require`
  - account for `pure` in ABI declaration surface
- lexical forms
  - clarify capability-path and qualified-alias interaction with existing `qualified_name`
  - clarify that alias names cannot start with `@`
- module grammar
  - legalize reserved `module @host`
  - preserve top-level-only module placement
  - carve out fragmentable reserved `@host`
  - restrict `@host` to ABI declarations only
- import grammar
  - move imports from top-level-only wording to module-local wording
  - keep explicit imports only
  - require imports to appear before word definitions
  - forbid imports inside word bodies
- alias grammar
  - preserve simple aliases
  - add qualified aliases as legal syntax
  - constrain aliases so they cannot occupy reserved roots
- declaration grammar
  - introduce `require` as a declaration form distinct from word definitions and `export`
  - define compact and multiline `require` forms as equivalent
- reserved namespace rules
  - replace wording that keeps direct `host.*` callable
  - preserve builtin reservations for `list.*`, `map.*`, `result.*`
- capability path grammar
  - define the source shape used after `require`
  - state that canonical paths are relative to `@host`
- host capability reference grammar
  - define the imported reference surface replacing direct `host.*`
- example grammar blocks
  - rewrite canonical examples and invalid examples embedded in `SYNTAXE.md`

## Module-local import migration analysis

Current visibility model:

- imports are top-level declarations
- aliases become visible in the importing compilation unit
- textual inclusion does not create a separate alias scope
- external user references require matching imports

Target visibility model:

- imports live inside modules
- visibility is local to the containing module
- aliases are local to the containing module
- host capability imports follow the same module-local visibility surface
- imports appear before word definitions
- imports do not appear at top-level
- imports do not appear inside word bodies

Possible ambiguity points:

- whether current prose that says “in the compilation unit” is fully replaced or partially shadowed
- whether user-module imports and `@host` imports share exactly the same placement wording
- whether local short-name resolution and module-local imported aliases can be confused in examples if rewrite ordering is inconsistent

Interaction with includes/multi-file compilation:

- current syntax wording ties alias scope to textual inclusion
- target module-local import wording must avoid leaving old compilation-unit alias language in place
- `include` remains deferred, so S1 must avoid silently redefining include semantics while still removing stale global-import wording
- reserved `@host` fragmentability must not accidentally be described as normal module-local visibility sharing

Risks of mixed visibility wording:

- keeping both compilation-unit alias language and module-local alias language would make the syntax chapter internally contradictory
- keeping top-level import examples while declaring module-local imports would produce an immediate example/spec mismatch
- leaving any suggestion that imports may appear after word definitions would contradict the frozen ordering rule
- leaving any suggestion that imports may appear inside executable bodies would contradict the frozen placement rule
- leaving current `include` scope language untouched in the wrong place could imply cross-module alias leakage that the target model removes

## Qualified alias analysis

The frozen target requires dotted aliases to become legal syntax.

Syntax-planning implications:

- dotted aliases must become first-class source forms rather than incidental prose examples
- the alias surface must be distinguished from existing qualified references such as `@module.word`
- the rewrite must make it clear that a qualified alias is an alias name, not a module reference and not a direct host capability path
- alias grammar must also preserve existing simple alias forms
- alias grammar must make it explicit that aliases cannot start with `@`
- alias grammar must make it explicit that aliases cannot occupy reserved roots such as `host`

Ambiguity risks:

- `console.log` could be read either as a qualified alias or as an existing qualified name form
- `import @host.console.log as console.log` introduces two dotted sequences in one statement, so the grammar prose must clearly separate imported target from alias target
- current alias wording assumes aliases are roots like `t` or short names like `split`, so examples may mislead readers if not rewritten in lockstep

Interaction with existing qualified references:

- `@module.word` remains the explicit external user-module reference form
- qualified aliases must not be described as module references
- syntax prose must prevent confusion between:
  - imported target path
  - alias path
  - ordinary user qualified references

## `require` declaration analysis

Declaration shape to plan for:

- compact canonical form such as `require console.log { msg:String -- } dirty`
- equivalent multiline form with path, signature, and effect on separate lines
- capability path following `require`
- stack signature block
- explicit ABI effect marker on every declaration

Placement restrictions to plan for:

- legal only inside `module @host`
- legal only directly in the `@host` body
- not legal in normal user modules
- not legal at top-level outside any module
- not legal as a replacement for `export`
- not legal as a word definition
- not legal inside word bodies

Interaction with module bodies:

- `require` must be described as a module-body declaration form
- the syntax chapter must state that `module @host` contains ABI declarations only
- the syntax chapter must state that `module @host` cannot contain imports, exports, word definitions, executable logic, constants, or variables
- ordering expectations inside `module @host` must be written clearly enough to avoid ambiguity in later examples

Reserved-word implications:

- `require` must enter reserved-form tables
- current examples using identifiers containing `require` do not conflict, but the exact bare identifier must no longer be available as a user-defined word name
- `pure` needs syntax treatment limited to ABI declarations unless later normative text says otherwise

Formatting/style consistency with existing Nicole syntax:

- existing declaration forms use compact Nicole-style blocks such as `export : word` and `: word { ... }`
- `require` planning should preserve that document style rather than introducing implementation-flavored notation
- the future rewrite must keep `require` presented as Nicole source syntax, not external contract pseudo-notation
- compact single-line examples should be preferred in simple cases
- multiline examples remain valid for readability and must be presented as equivalent rather than as a different construct

## `@host` reserved module analysis

How it differs from user modules:

- it is reserved by the language
- it is legal despite current reserved-root prohibition
- it is not a normal user module
- it exists for ABI declaration rather than ordinary word definition
- it is fragmentable across files under frozen rules

Syntax restrictions that must be explicit:

- `module @host` is reserved and special
- normal user modules still cannot occupy reserved roots
- direct `host.*` callable syntax is removed even though host ABI remains source-visible
- the syntax chapter must state that `require` is the legal declaration form inside `@host`
- the syntax chapter must state what declarations are not legal inside `@host`
- the syntax chapter must state that `@host` does not contain executable logic

How fragmentability affects syntax wording:

- current syntax says module names are unique in the compilation unit
- S1 planning must add a narrowly scoped exception for reserved `@host`
- the wording must avoid accidentally generalizing fragmentable modules beyond `@host`
- syntax-level wording should state the permitted repeated `module @host` form without drifting into semantic merge algorithm detail

## Syntax diagnostics inventory

Future syntax-error classes likely required:

- `require` outside `module @host`
- illegal declaration inside `module @host`
- illegal import inside `module @host`
- illegal export inside `module @host`
- illegal word definition inside `module @host`
- illegal executable content inside `module @host`
- illegal direct `host.*` use under the new model
- invalid qualified alias form
- alias starting with `@`
- invalid alias occupying a reserved root
- invalid import placement outside the allowed module-local surface
- invalid top-level import
- import placed after word definitions
- import inside a word body
- illegal duplicate reserved-module wording for non-`@host` modules
- illegal user occupancy of `@host`
- illegal ABI effect declaration shape
- illegal missing ABI effect line in `require`
- non-canonical `require @host...` path form if explicitly rejected in examples or grammar notes
- mixed old/new host syntax in the same example block

Final wording is intentionally deferred.

## Examples requiring rewrite later

Exact `SYNTAXE.md` example categories likely requiring migration:

- module/import grammar examples in `Fondations grammaticales modules/imports/includes`
- any example or rule text that uses top-level imports
- any example showing only simple aliases without qualified-alias coverage
- any example implying aliases may start with `@` or occupy reserved roots
- the entire `Mots fournis par l’hôte` section
- invalid host example using direct `host.read-config`
- conceptual host contract example comments using direct `host.io.open-file`
- any example that treats `@host` like a normal user module
- visibility example block in `Syntaxe à ne pas utiliser` that still includes dirty exported direct host access
- full valid example in `Exemple complet valide`
- summary examples in `Résumé de la syntaxe` that still show dirty exported direct host access
- future-document-separation wording that still describes `HOST_ABI.md` in terms of `host.*` under the old surface

## Suggested rewrite ordering for SYNTAXE.md

1. Update the frozen-decision anchor points in lexical and reserved-form sections.
2. Rewrite reserved-root rules to legalize reserved `@host` while preserving other reserved-root restrictions and alias-root restrictions.
3. Rewrite module grammar to introduce the reserved `@host` exception, ABI-only body restriction, and fragmentable reserved-module wording.
4. Rewrite import grammar from top-level visibility to module-local visibility, including:
  - imports only inside modules
  - imports before word definitions
  - no imports inside word bodies
5. Rewrite alias grammar to admit qualified aliases while preserving simple aliases and excluding `@`-prefixed aliases and reserved-root aliases.
6. Introduce `require` as a syntax declaration form with:
  - canonical compact form
  - equivalent multiline form
  - relative capability-path form under `@host`
  - explicit required ABI effect
7. Rewrite the current direct `host.*` syntax surface into the source-visible ABI declaration/import model.
8. Replace host-facing examples inside the syntax chapter, preferring compact `require` form in simple examples.
9. Replace invalid syntax examples tied to direct `host.*`, old import placement, and illegal `@host` body content.
10. Rewrite summary blocks and the full valid example.
11. Sweep terminology for stale references to:
  - direct `host.*`
  - top-level import visibility
  - compilation-unit alias scope where module-local scope is now intended
  - unique module names without the reserved `@host` exception
  - `pure` as if it were a general Nicole declaration modifier
12. Run a final syntax-only consistency pass across section prose, embedded examples, and summary text.

## Risks

- partial rewrite risk: updating grammar rules without updating embedded examples will leave `SYNTAXE.md` self-contradictory
- terminology drift risk: old wording such as “top-level imports” or “direct `host.*`” may survive in summaries after the main sections are changed
- reserved-root drift risk: legalizing `@host` without carefully preserving other reserved-root prohibitions may broaden the language surface unintentionally
- mixed-scope risk: leaving compilation-unit alias wording near module-local import wording would make the syntax chapter ambiguous
- fragmentability wording risk: stating the `@host` exception too broadly could accidentally imply general open modules
- effect-surface risk: introducing `pure` imprecisely could look like a general new annotation rather than an ABI declaration surface

## Open questions

- exact notation to use in `SYNTAXE.md` grammar tables for qualified alias names versus existing `qualified_name`
- exact notation to use in `SYNTAXE.md` grammar tables for relative capability paths under `require`
- exact wording placement for the reserved `@host` fragmentability exception within the existing module-uniqueness section
- exact non-diagnostic prose needed to distinguish imported host capability references from existing user qualified references

## Recommendation

READY_FOR_SPEC_REWRITE

The syntax-surface freezes are now specific enough to begin the future `SYNTAXE.md` rewrite, with only narrow wording and notation choices left to settle during the rewrite itself.
