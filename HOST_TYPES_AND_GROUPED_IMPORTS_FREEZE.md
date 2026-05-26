# Host Types and Grouped Imports Freeze

## Status

Document status:

`stable`

Current global status:

`implemented in active specification`

## Scope

This file is a tracking/freeze document only.

Supersession note:

- this freeze supersedes `HOST_OPAQUE_TYPES_PLAN.md`
- the old plan froze the previous model in which Nicole source could not declare opaque host types and canonical opaque host type names remained under `host.*`
- this freeze replaces that model with source declarations such as `opaque io.FileHandle` inside `module @host` and canonical opaque host type names under `@host.*`

It records the frozen architecture decisions now integrated into the active Nicole specification concerning:

- host opaque type declarations inside `module @host`
- canonical opaque host type names under `@host.*`
- host opaque types as importable symbols
- grouped imports with prefix alias
- grouped imports with `as *`
- auditability guidance for grouped direct exposure

This file is not normative specification text.

Normative source of truth remains:

- `SYNTAXE.md`
- `SEMANTIQUE.md`
- `HOST_ABI.md`

If this freeze conflicts with the current normative specification, the normative specification remains the active source of truth until later migration phases are executed.

## Frozen decisions

### 1. Host opaque type declaration syntax

Canonical declaration form:

```nicole
module @host
  opaque io.FileHandle
end-module
```

Frozen rules:

- `opaque` is valid only inside `module @host`
- `opaque` declares an opaque host ABI type
- there is no `type opaque` syntax
- Nicole source defines no constructor for an opaque host type
- Nicole source defines no structural inspection for an opaque host type
- this decision does not introduce a general user-defined type system

### 2. Canonical opaque host type identity

Canonical type identity:

```text
@host.io.FileHandle
```

Frozen rules:

- canonical opaque host type names move from `host.*` to `@host.*`
- `host.io.FileHandle` becomes obsolete legacy vocabulary
- `@host` becomes the unified ABI symbol namespace
- opaque host type identity remains nominal

### 3. Opaque host types are importable symbols

Canonical form:

```nicole
import @host.io.FileHandle as io.FileHandle
```

Frozen rules:

- opaque host types are importable symbols
- type aliases created this way are module-local
- the same import mechanism is used for capabilities and opaque host types
- there is no separate type-import syntax
- grouped import syntax remains part of the general import surface, not a host-only special case

### 4. Grouped imports with prefix alias

Canonical form:

```nicole
module @app
  import @host.io.{
    open-file
    close-file
    FileHandle
  } as io
end-module
```

Frozen equivalence:

```nicole
import @host.io.open-file as io.open-file
import @host.io.close-file as io.close-file
import @host.io.FileHandle as io.FileHandle
```

Frozen rules:

- grouped imports with prefix alias are syntax sugar only
- they do not introduce a new semantic import category
- module-local visibility is preserved
- existing collision rules remain unchanged
- imported symbols keep their original categories

### 5. Grouped imports with `as *`

Canonical form:

```nicole
module @app
  import @host.console.{
    log
    read-line
  } as *
end-module
```

Frozen equivalence:

```nicole
import @host.console.log as log
import @host.console.read-line as read-line
```

Frozen rules:

- `as *` imports an explicit selected set of symbols only
- `as *` is not a wildcard import
- `as *` remains module-local
- collisions remain errors
- imported names remain ordinary imported symbols

### 6. Auditability guidance

Frozen guidance:

- prefix alias style is recommended for most normative examples
- `as *` is allowed but less auditable
- `as *` is appropriate mainly for tiny modules, local helper modules, or examples where brevity is intentionally preferred
- future spec text and examples should preserve explicit dependency visibility even when using grouped syntax sugar

### 7. No wildcard imports

Invalid forms:

```nicole
import @host.io.*
import @host.io.* as *
```

Frozen rules:

- wildcard imports remain invalid
- grouped imports do not weaken this rule
- explicit selected imports and wildcard imports remain distinct concepts

### 8. Future compatibility

Frozen rules:

- this direction must remain compatible with future user-defined types and structs
- the same import mechanism should apply to words, capabilities, opaque host types, structs, and future symbol categories
- this freeze does not define structs now

## Non-goals

This freeze does not:

- redesign effects
- redesign modules
- redesign runtime semantics
- redesign type checking
- define user structs
- implement generics
- introduce implicit imports
- introduce wildcard imports
- weaken module-local visibility
- weaken ABI auditability

## Rationale

- Host opaque types should live in the same source-visible ABI namespace as host capabilities.
- `module @host` already establishes the visible ABI contract boundary; declaring opaque types there keeps the contract unified.
- Moving canonical opaque type names under `@host.*` eliminates the split between capability naming and opaque type naming.
- Importing opaque host types through the same mechanism as capabilities avoids a second parallel import system.
- Grouped imports with prefix alias reduce repeated namespace segments without weakening module-local reasoning.
- Grouped imports with `as *` are accepted only as explicit selected-import sugar, not as a general wildcard facility.

## Auditability constraints

- Source-visible ABI boundaries must remain explicit.
- Dependency visibility must remain local to the importing module.
- Collision rules must remain strict and deterministic.
- Prefix alias style remains the preferred form for most normative examples because it preserves origin visibility better than direct exposure.
- `as *` must never be framed as the default style for capability-heavy modules.
- The language must not regress toward implicit dependency discovery.

## Compatibility impact

- The coordinated migration to canonical `@host.*` opaque type names has been applied in the active normative specification.
- Active valid and invalid examples now align with source-visible `opaque` declarations inside `module @host`.
- Grouped import syntax is now integrated into the active syntax and semantics as explicit sugar only.

## Files changed by this freeze wave

- `SYNTAXE.md`
- `SEMANTIQUE.md`
- `HOST_ABI.md`
- `EXAMPLES.md`
- `INVALID_EXAMPLES.md`
- `README.md`

Historical supporting tracking documents may remain archived separately.

## Risks

- canonical renaming from `host.*` to `@host.*` is not a local syntax tweak; it changes the current ABI/type naming model globally
- grouped imports with `as *` may be overused in examples and reduce auditability if style guidance is weak
- importing symbols across multiple categories through one syntax surface may expose hidden category assumptions in the current resolver and checker model
- later user-defined type work could inflate grouped import complexity if category rules are not kept uniform
- legacy wording may survive in examples or invalid examples unless migration is audited globally first

## Historical notes after integration

- Grouped imports are now integrated as a general import surface form in v1, not restricted to `@host`.
- Prefix alias style remains the preferred normative style when dependency origin visibility matters.
- Obsolete legacy `host.*` opaque type wording remains appropriate only as explicit historical contrast in archival material such as this freeze.

## Recommendation

`READY_FOR_GLOBAL_SPEC_PATCH_PLANNING`
