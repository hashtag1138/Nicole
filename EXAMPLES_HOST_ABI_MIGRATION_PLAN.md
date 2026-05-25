# EXAMPLES Host ABI Migration Plan

## Scope

This document plans the future migration of `EXAMPLES.md` only.

This plan is limited to example migration preparation after the committed host ABI refactor in:

- `SYNTAXE.md`
- `SEMANTIQUE.md`
- `HOST_ABI.md`

This plan does not:

- rewrite `EXAMPLES.md` yet
- rewrite `INVALID_EXAMPLES.md` yet
- rewrite normative syntax, semantics, or ABI text
- define implementation strategy
- discuss NicolePy internals
- modify any other specification file

This document is planning/tracking text only.

## Current example model summary

Current `EXAMPLES.md` contains two broad classes of material:

- sections that are independent of the host ABI refactor
- sections that still illustrate the old direct-call `host.*` model

Current host-sensitive areas:

- `## 10. host.*`
  - built entirely around direct host calls such as `msg host.log`
  - presents external host contract records such as `host.log`, `host.config.get`, `host.io.open-file`
  - uses old availability wording (`required`)
- `## 11. export`
  - several export examples still call `host.log` directly
- `## 12. Exemple complet court`
  - still uses direct `host.log`
- `## 14. Pureté et effet dirty`
  - still sources impurity from direct `host.log`
  - still phrases dirty propagation through direct host calls

Current host-opaque examples are mixed:

- some examples must be rewritten because they pair opaque host types with direct `host.*` callable words
- some examples can mostly survive because they illustrate storage or transport of `host.io.FileHandle` as a type rather than direct call syntax

Current host-neutral areas likely unaffected:

- `## 1. Mots simples`
- `## 2. Variables locales`
- `## 3. Sous-mots privés`
- `## 4. Noms explicites et récursion mutuelle`
- `## 5. Retours multiples`
- `## 6. if`
- `## 7. case`
- `## 8. Collections`
- `## 9. Quotations`
- `## 13. Quotation retournée comme valeur`

## Frozen target example model summary

Examples must align with the committed normative documents.

Target assumptions:

- programs no longer call `host.*` directly
- required host capabilities are declared in `module @host`
- application modules import host capabilities explicitly from `@host`
- imports are module-local
- aliases are module-local
- qualified aliases are valid
- every ABI declaration uses explicit `pure` or `dirty`
- `pure` remains ABI-only syntax
- `@host` may be fragmentable, but examples should stay simple unless a fragmentability example is pedagogically necessary
- builtins `list.*`, `map.*`, `result.*` remain unchanged
- opaque host type vocabulary under `host.*` remains valid

## Current examples using old `host.*`

Direct old-model examples currently present in `EXAMPLES.md`:

- `## 10. host.*`
  - `Avertir l’hôte`
  - `Lecture de configuration depuis l’hôte`
  - `Handle de fichier opaque déclaré par l’hôte`
- `## 11. export`
  - `Handler de message`
  - `Handler sans retour`
- `## 12. Exemple complet court`
- `## 14. Pureté et effet dirty`
  - `Mot dirty direct`
  - `Export dirty`
  - `Sous-mot dirty appelé`
  - `DirtyQuote construit et appelé dans une frame dirty`
  - `DirtyQuote passé à list.map dans une frame dirty`
  - `Propagation indirecte transitive`

Migration implication:

- these sections cannot remain as-is because they visibly contradict the committed syntax and semantics

## Examples needing `module @host`

Examples that should explicitly introduce `module @host`:

- the replacement for `## 10. host.*`
  - this section should be reframed around host capability declarations rather than direct host words
- the host-sensitive examples under `## 11. export`
- `## 12. Exemple complet court`
- the host-dependent examples under `## 14. Pureté et effet dirty`

Recommended example pattern:

- declare one compact `module @host` block before the example module when only one or two capabilities are needed
- keep the `@host` block minimal and directly relevant to the example
- prefer compact single-line `require` form in simple examples

## Examples needing module-local imports

Examples that must show module-local imports:

- all rewritten host capability call examples
- all rewritten export examples that depend on host capabilities
- all rewritten dirty-propagation examples sourced from host capabilities

Module-local import migration points:

- imports should appear inside the module that uses the capability
- imports should appear before any word definitions in that module
- imports should not be repeated in explanatory prose as if they were global

## Examples needing qualified aliases

Qualified aliases are not required everywhere, but S4 should include them where they clearly improve continuity with the imported capability path.

Best candidates:

- logging examples:
  - `import @host.console.log as console.log`
- host I/O examples:
  - `import @host.io.open-file as io.open-file`
  - `import @host.io.read-line as io.read-line`
  - `import @host.io.close-file as io.close-file`

Planning rule:

- use qualified aliases in at least a few canonical examples so the new surface is actually illustrated
- do not force qualified aliases into every example if a simpler local alias is more readable

## Examples involving `dirty`

Host-dependent dirty examples requiring rewrite:

- `Mot dirty direct`
- `Export dirty`
- `Sous-mot dirty appelé`
- `DirtyQuote construit et appelé dans une frame dirty`
- `DirtyQuote passé à list.map dans une frame dirty`
- `Propagation indirecte transitive`

Rewrite goal:

- preserve the same teaching purpose
- change only the impurity source from direct `host.log` to an imported capability declared by `require`

Important alignment points:

- ordinary Nicole words still use `dirty`, not `pure`
- the example text should say impurity comes from the imported host capability’s declared ABI effect
- `list.map` and similar builtins should remain described as unchanged

## Examples involving host opaque types

Examples involving `host.io.FileHandle` divide into two groups.

Examples needing partial rewrite:

- `Handle de fichier opaque déclaré par l’hôte`
  - keep `host.io.FileHandle`
  - replace direct calls such as `host.io.open-file` with imported capability use sourced from `@host`

Examples likely reusable with light wording cleanup only:

- `Valeur opaque hôte dans List<T> et Map<String,T>`
- `Transport d’une valeur opaque hôte dans une quotation`
- `Export avec type opaque hôte déclaré`

Reason:

- these examples mainly illustrate ABI-compatible opaque host type transport rather than the direct-call surface
- they still need surrounding contract wording updated so they refer to declared capabilities or declared opaque types rather than the old external-only host-call model

## Examples that should remain unchanged

The following categories should remain unchanged or require at most minimal wording cleanup unrelated to host ABI:

- basic arithmetic and locals
- subwords
- explicit naming and recursion examples
- multiple returns
- `if`
- `case`
- non-host collection examples
- general quotation examples that do not use host capabilities
- pure export example without host interaction

Reason:

- these examples do not depend on the host ABI surface refactor
- touching them would increase scope without improving alignment

## Suggested rewrite ordering

1. Rewrite `## 10. host.*` into a new host-capability section built around `module @host`, `require`, and imports.
2. Rewrite the host-dependent examples in `## 11. export`.
3. Rewrite `## 12. Exemple complet court`.
4. Rewrite the host-dependent examples in `## 14. Pureté et effet dirty`.
5. Perform light wording cleanup in host-opaque examples that remain structurally valid.
6. Sweep the document for residual direct `host.*` call wording.
7. Run a final consistency pass against committed `SYNTAXE.md`, `SEMANTIQUE.md`, and `HOST_ABI.md`.

Why this order is safer:

- the dedicated host example section should establish the new idiom first
- export and dirty examples depend on that idiom
- opaque host type examples should be adjusted only after the new host-capability examples are stable
- host-neutral sections can stay untouched unless a residual wording contradiction is discovered

## Risks

- mixed-model risk:
  - leaving direct `host.*` examples beside `@host` examples would create a contradictory learning surface
- scope-creep risk:
  - rewriting host-neutral examples would turn S4 into a general editorial pass
- readability risk:
  - overloading every example with large `@host` blocks could make `EXAMPLES.md` harder to read
- alias-confusion risk:
  - introducing qualified aliases without clear local context could make them look like module references
- opaque-type drift risk:
  - overcorrecting direct-call removal could accidentally obscure the still-valid `host.*` opaque type vocabulary
- dirty-explanation drift risk:
  - if effect explanations keep talking about direct host words, the examples will contradict committed `SEMANTIQUE.md`

## Recommendation

CONTINUE_SPEC_INVESTIGATION

Reason:

- the impacted example regions are now clearly identified
- the normative host model is already committed
- the remaining work is a bounded example-migration step, but the exact rewrite prompt should preserve strong boundaries so host-neutral examples remain untouched
