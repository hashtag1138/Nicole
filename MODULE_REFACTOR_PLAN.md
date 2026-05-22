# Nicole mandatory modules refactor plan

## Status

Document status:

`stable`

Current global status:

`pre-audit`

## Status vocabulary

- `planned`
- `pre-audit`
- `ready-to-patch`
- `patching`
- `post-audit`
- `implemented`
- `blocked`
- `deferred`

## Frozen design decisions

- All user-defined words must be defined inside modules.
- Top-level user word definitions are invalid.
- External user word references use explicit module qualification: `@module.word`.
- Host ABI export names preserve the leading `@`: `@module.word`.
- `@module.word` is allowed inside the same module, though short local names are preferred there.
- `.` is a structural separator, not an identifier character.
- `@` is not an identifier character.
- Modules exist only at top-level.
- Modules cannot be nested.
- Modules are not executable words.
- Module names require `@`.
- Module names must be unique.
- Empty modules are valid.
- `export : word` is a declaration only.
- `export : word` must reference an existing word in the same module.
- Subwords are private by default.
- Public subword paths require every exposed path segment to be public.
- `pub` exposes only qualified paths, not short names.
- Import cycles are forbidden.
- Recursion inside one module is unchanged.
- Cross-module mutual recursion through cyclic imports is invalid.
- `include` is explicit textual inclusion.
- Include paths are relative to the file containing the include.
- Included files inside modules are module-body fragments.
- Included module-body fragments must not contain `module ... end-module`.
- Duplicate includes are allowed only if normal collision rules still pass.
- Implicit module merging does not exist.
- Import aliases are scoped to the compilation unit after textual inclusion.
- Reserved namespace roots are reserved both as roots and namespace forms:
  - `host`, `host.*`
  - `list`, `list.*`
  - `map`, `map.*`
  - `result`, `result.*`

## Phase overview table

| Phase | Name | Status | Commit/tag | Notes |
|---|---|---|---|---|
| 0 | Baseline cleanup and existing contradictions | implemented | | Fix existing `case when` contradictions before module migration |
| 1 | Lexical and grammar foundation | implemented | | Add `@`, structural `.`, module/import/include grammar shells |
| 2 | Mandatory module model | implemented | | Forbid top-level user words; define module containment |
| 3 | Resolution, imports, and namespaces | implemented | | Define aliases, collisions, reserved roots, import graph |
| 4 | Export and HOST_ABI rewrite | pre-audit | | Host-visible names become `@module.word` |
| 5 | Valid examples rewrite | planned | | Rewrite all valid examples into module form |
| 6 | Invalid examples rewrite | planned | | Preserve intended invalid reasons under new baseline |
| 7 | Final consistency audit and tagging | planned | | Cross-file audit, release readiness, tag proposal |

## Phase dependencies

- Phase 0 → Phase 1
- Phase 1 → Phase 2
- Phase 2 → Phase 3
- Phase 3 → Phase 4
- Phase 4 → Phase 5
- Phase 5 → Phase 6
- Phase 6 → Phase 7

A phase cannot enter `patching` unless all predecessor phases are `implemented`.

## Phase 0 — Baseline cleanup and existing contradictions

- Goal: Fix pre-existing specification contradictions before module refactor semantics are introduced.
- Dependencies: none
- Scope: Resolve known cross-file contradictions that can block reliable migration work.
- Files expected to change: `README.md`, `SYNTAXE.md`, `SEMANTIQUE.md`, `INVALID_EXAMPLES.md`.
- Explicit exclusions: No module/import/include syntax introduction; no global example rewrite.
- Pre-audit checklist:
- Confirm clean worktree and pinned baseline.
- Re-audit contradictions with concrete line references.
- Confirm contradiction resolution target wording across normative files.
- Patch checklist:
- Apply minimal contradiction fixes only.
- Keep old naming model intact in this phase except where contradiction forces alignment.
- Post-audit checklist:
- Re-run contradiction grep checks.
- Confirm no new divergences between syntax and semantics.
- Validation checks:
- `grep -Rni "when n.existe pas en v1|when n’existe pas en v1|pattern when guard" *.md`
- `git diff --stat`
- Risks:
- Fixes may accidentally reopen closed wording decisions if scope is not tightly enforced.
- Status: `implemented`
- Result commit: 49c882146d17060ec6d614122e94215292b10687
- Result tag:
- Notes:
- Guard contradiction resolved
- Invalid guard example rewritten
- Contributor guidance aligned with current name resolution model

## Phase 1 — Lexical and grammar foundation

- Goal: Define lexical and grammar primitives required by mandatory modules.
- Dependencies: Phase 0
- Scope: Introduce tokenization and grammar shells for `@`, structural `.`, `module`, `import`, `include`.
- Files expected to change: `SYNTAXE.md`, `SEMANTIQUE.md`, `README.md`.
- Explicit exclusions: Full semantics of import graph, full ABI rewrite, full example corpus rewrite.
- Pre-audit checklist:
- Inventory all current lexical rules that conflict with structural qualification.
- Inventory all references treating `.` as identifier content.
- Patch checklist:
- Update lexical rules and reserved forms.
- Add grammar shells for module/import/include.
- Add grammar foundations required for mandatory-module syntax.
- Do not yet enforce mandatory-module semantic rules.
- Post-audit checklist:
- Verify lexical rules are internally consistent.
- Verify grammar summary and detailed sections agree.
- Validation checks:
- `grep -Rni "après le premier caractère.*\\." SYNTAXE.md`
- `grep -Rni "module|end-module|import|include" SYNTAXE.md SEMANTIQUE.md`
- Risks:
- Partial lexical changes can make examples and invalid examples temporarily inconsistent until later phases.
- Status: `implemented`
- Result commit: 74565733f76378dc05f72681a1a363e5ea26d265
- Result tag:
- Notes:
- Lexical groundwork added for `@`
- `.` changed to structural separator in syntax foundation
- Reserved forms added for `module`, `end-module`, `import`, `include`
- Grammar shells added for module/import/include
- Phase 1 post-audit passed

## Phase 2 — Mandatory module model

- Goal: Enforce module containment as the only user-definition model.
- Dependencies: Phase 1
- Scope: Forbid top-level user words and define module-local vs external name usage.
- Files expected to change: `SYNTAXE.md`, `SEMANTIQUE.md`, `README.md`, `INVALID_EXAMPLES.md`.
- Explicit exclusions: Alias collision matrix details; full import graph details; HOST_ABI naming rewrite.
- Pre-audit checklist:
- Confirm all top-level-definition references are identified.
- Confirm module constraints list is frozen.
- Patch checklist:
- Add mandatory-module rule.
- Add top-level word invalid rule and diagnostic shape.
- Define local short-name use and external `@module.word` requirement.
- Post-audit checklist:
- Confirm no normative section still states that user top-level words are valid.
- Validation checks:
- `grep -Rni "Il n’existe pas de graphe de modules|aucun graphe de modules" SYNTAXE.md SEMANTIQUE.md`
- Audit that every user word definition appears inside a `module @... end-module` block.
- Risks:
- Legacy examples can obscure whether failures are from intended rule or top-level prohibition.
- Status: `implemented`
- Result commit: cc945fbcda1dc0304a9bbc8a9b9a484412871144
- Result tag:
- Notes:
- Mandatory module containment added
- Top-level user word definitions marked invalid
- Local module short-name references documented
- External user references documented as `@module.word`
- Phase 2 corrective post-audit passed

## Phase 3 — Resolution, imports, and namespaces

- Goal: Specify static name resolution with imports, aliases, reserved roots, and acyclic imports.
- Dependencies: Phase 2
- Scope: Define import forms, alias visibility/collisions, namespace reservations, and cycle rules.
- Files expected to change: `SYNTAXE.md`, `SEMANTIQUE.md`, `README.md`, `INVALID_EXAMPLES.md`.
- Explicit exclusions: Full valid examples rewrite and full ABI rewrite.
- Pre-audit checklist:
- Map all current name-resolution assumptions to new module model.
- Identify required new invalid cases for imports/cycles/reserved roots.
- Patch checklist:
- Add resolution ordering and collision rules.
- Add reserved root constraints (`host`, `list`, `map`, `result`).
- Add import cycle prohibition and cross-module recursion consequence.
- Post-audit checklist:
- Confirm resolution rules are aligned between syntax and semantics.
- Validation checks:
- `grep -Rni "import \\*|wildcard|cycle|reserved" SYNTAXE.md SEMANTIQUE.md INVALID_EXAMPLES.md`
- `grep -Rni "@host|@list|@map|@result" INVALID_EXAMPLES.md`
- Risks:
- Under-specified alias scoping can lead to inconsistent compiler interpretations.
- Status: `implemented`
- Result commit: d87a4550944fff370a439a0c6ea08c4e37b9cd07
- Result tag:
- Notes:
- Static module-aware resolution defined
- Import forms and alias semantics defined
- External `@module.word` references require corresponding imports
- Alias scope after textual inclusion specified
- Reserved namespace roots added
- Import cycles forbidden
- Cross-module recursion through cyclic imports invalid
- Phase 3 corrective post-audit passed

## Phase 4 — Export and HOST_ABI rewrite

- Goal: Reframe export and host ABI naming around module-qualified names with leading `@`.
- Dependencies: Phase 3
- Scope: Define module-local export declarations and canonical host-visible names `@module.word`.
- Files expected to change: `HOST_ABI.md`, `SYNTAXE.md`, `SEMANTIQUE.md`, `README.md`, `INVALID_EXAMPLES.md`.
- Explicit exclusions: Full valid examples rewrite.
- Pre-audit checklist:
- Inventory all existing ABI/export examples using legacy names (`entry`, `entry.*`, `app.*`).
- Confirm export declaration semantics are frozen.
- Patch checklist:
- Replace top-level export assumptions with in-module declaration model.
- Update uniqueness and collision wording for `@module.word`.
- Post-audit checklist:
- Confirm all ABI examples use canonical `@module.word`.
- Validation checks:
- `grep -Rni "export : entry|entry\\.|app\\." HOST_ABI.md SYNTAXE.md SEMANTIQUE.md`
- `grep -Rni "@[a-zA-Z0-9_-]*\\.[a-zA-Z0-9_-]" HOST_ABI.md`
- Risks:
- ABI naming drift between syntax and host contract can break downstream implementation planning.
- Status: `pre-audit`
- Result commit:
- Result tag:
- Notes:

## Phase 5 — Valid examples rewrite

- Goal: Rewrite all valid examples into mandatory module form without changing intended semantics.
- Dependencies: Phase 4
- Scope: Convert code blocks and inline examples across valid-example surfaces.
- Files expected to change: `EXAMPLES.md`, `SYNTAXE.md`, `SEMANTIQUE.md`, `HOST_ABI.md`, `DESIGN_NOTES.md`, `README.md`.
- Explicit exclusions: Invalid examples rewrite.
- Pre-audit checklist:
- Inventory all top-level `: ...` valid examples.
- Inventory all external call examples requiring explicit `@module.word`.
- Patch checklist:
- Wrap valid examples in `module @... end-module`.
- Update exports to module-local declaration shape.
- Update external invocation forms to explicit qualification.
- Post-audit checklist:
- Confirm every valid example compiles conceptually under new model.
- Validation checks:
- Audit that every user word definition appears inside a `module @... end-module` block.
- `grep -Rni "@[a-zA-Z0-9_-]*\\." EXAMPLES.md`
- Risks:
- High-volume edits can introduce accidental semantic regressions in pedagogical examples.
- Status: `planned`
- Result commit:
- Result tag:
- Notes:

## Phase 6 — Invalid examples rewrite

- Goal: Ensure invalid examples fail for the intended reason under the new baseline.
- Dependencies: Phase 5
- Scope: Rewrite, remove, invert, or add invalid cases as required by mandatory modules.
- Files expected to change: `INVALID_EXAMPLES.md`, `SYNTAXE.md`, `SEMANTIQUE.md`, `HOST_ABI.md`.
- Explicit exclusions: New feature work outside frozen decisions.
- Pre-audit checklist:
- Classify each invalid example: keep/rewrite/remove/invert.
- Identify invalid cases masked by top-level prohibition.
- Patch checklist:
- Add new invalid classes: top-level words, bad imports, alias collisions, cycles, reserved-root modules, include violations.
- Rewrite old invalids inside modules where necessary to preserve original failure reason.
- Post-audit checklist:
- Verify each invalid has a precise violated rule citation.
- Validation checks:
- `grep -Rni "top-level word definitions are not allowed|unqualified external module reference|cyclic import" INVALID_EXAMPLES.md`
- Audit that invalid examples still fail for their intended rule.
- Audit that invalid examples containing `: word` definitions place them inside module blocks unless the intended failure is "top-level definition forbidden".
- Risks:
- If not rewritten carefully, invalid examples can silently test the wrong rule.
- Status: `planned`
- Result commit:
- Result tag:
- Notes:

## Phase 7 — Final consistency audit and tagging

- Goal: Complete final cross-file consistency audit and prepare release/tag proposal.
- Dependencies: Phase 6
- Scope: Full spec consistency check after all refactor phases.
- Files expected to change: none expected; audit-only unless defects require micro-fixes.
- Explicit exclusions: No new semantics or feature expansion.
- Pre-audit checklist:
- Confirm all prior phases are `post-audit` complete.
- Confirm clean worktree and expected baseline for final audit.
- Patch checklist:
- Apply only critical consistency corrections if required.
- Post-audit checklist:
- Confirm syntax/semantics/ABI/examples/invalids all aligned.
- Produce final release readiness report and tagging recommendation.
- Validation checks:
- `git status --short`
- `git diff --stat`
- `grep -Rni "no modules|no import|top-level export" README.md SYNTAXE.md SEMANTIQUE.md HOST_ABI.md`
- Risks:
- Late micro-fixes can unintentionally reopen scoped decisions.
- Status: `planned`
- Result commit:
- Result tag:
- Notes:

## Status history

| Date | Phase | Old status | New status | Reason |
|---|---:|---|---|---|
| 2026-05-22 | Phase 0 | planned | implemented | Phase 0 post-audit passed |
| 2026-05-22 | Phase 1 | planned | pre-audit | Next phase opened |
| 2026-05-22 | Phase 1 | pre-audit | patching | Grammar groundwork implementation started |
| 2026-05-22 | Phase 1 | patching | implemented | Phase 1 post-audit passed |
| 2026-05-22 | Phase 2 | planned | pre-audit | Next phase opened |
| 2026-05-22 | Phase 2 | pre-audit | patching | Mandatory module model implementation started |
| 2026-05-22 | Phase 2 | patching | implemented | Phase 2 corrective post-audit passed |
| 2026-05-22 | Phase 3 | planned | pre-audit | Next phase opened |
| 2026-05-22 | Phase 3 | pre-audit | patching | Resolution, imports, and namespace implementation started |
| 2026-05-22 | Phase 3 | patching | implemented | Phase 3 corrective post-audit passed |
| 2026-05-22 | Phase 4 | planned | pre-audit | Next phase opened |

## Important constraints

- Each phase requires pre-audit before patching.
- Each patch phase requires post-audit before the next phase starts.
- Large example rewrites must not be mixed with lexer/grammar patches.
- HOST_ABI changes must be reviewed independently.
- No implementation repository work starts until the spec refactor is tagged.
- NicolePy must later be audited against the final tagged spec.
