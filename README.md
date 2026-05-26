# README.md

# Projet : Manuel de référence d’un langage concaténatif typé

## Objectif

Définir entièrement un langage de programmation avant toute implémentation.

Le projet porte sur :

- la spécification du langage
- le manuel de référence
- les exemples de programmation
- les cas invalides et comportements attendus
- les conventions de design

Le projet ne porte pas sur l’implémentation.

---

## Vision

Le langage recherché est un langage :

- concaténatif
- statiquement structuré
- avec signatures typées obligatoires
- avec variables locales immuables
- avec stack frames isolées
- avec sous-mots privés, éventuellement nommés de façon qualifiée en interne
- avec résolution statique par nom visible unique
- uniquement embarqué
- pensé autour d’un modèle d’exécution en bytecode
- éventuellement compatible avec un JIT plus tard, sans que cela fasse partie de la v1

Il doit ressembler à une forme moderne et disciplinée de Forth, sans les mécanismes historiques complexes.

Références conceptuelles :

- Forth
- Factor
- Lua (pour l’embarqué)
- approches fonctionnelles simples

---

## Ce qui doit être documenté

### Rôle des fichiers

- `SYNTAXE.md` : syntaxe figée de v1
- `SEMANTIQUE.md` : sémantique figée de la v1 ; référence officielle du comportement du langage
- `HOST_ABI.md` : priorité actuelle ; contrat conceptuel entre le programme Nicole et l’hôte embarquant (`module @host`, `require`, `opaque`, `export`, types opaques hôte)

Les règles normatives sur `export`, `module @host`, `require`, `opaque`, les capacités hôte importables, les types opaques hôte importables, `Result`, les erreurs d’intégration et la frontière de confiance runtime vivent dans `HOST_ABI.md`.

Les types opaques hôte sont des types nominaux déclarés source-visiblement dans ce contrat, sous des noms canoniques `@host.*` comme `@host.io.FileHandle`.

Forme minimale :

```nicole
module @host
  opaque io.FileHandle
end-module
```

Un type opaque hôte importable utilise ensuite la même forme d’import explicite que les capacités hôte :

```nicole
import @host.io.FileHandle as io.FileHandle
```

Il n’existe pas de syntaxe d’import séparée pour les types opaques hôte.

`HOST_ABI.md` reste une spécification conceptuelle et ne doit pas dériver vers une API C, une ABI binaire, une FFI Rust/Lua, une représentation mémoire concrète, ni des détails de runtime.

Les aliases éventuels pour ces types opaques hôte restent différés.

`SYNTAXE.md`, `SEMANTIQUE.md` et `HOST_ABI.md` sont les seules sources normatives de la v1.

`EXAMPLES.md` et `INVALID_EXAMPLES.md` sont des documents dérivés qui expliquent, illustrent et consolident la spécification.

`REFERENCE_MANUAL.md` et `LANGUAGE_SPEC.md` sont des livrables dérivés futurs possibles du dépôt.

Ils ne doivent jamais redéfinir la syntaxe ou la sémantique.

`LANGUAGE_SPEC.md` est un document de consolidation et de lecture.

Il ne constitue pas une nouvelle source normative.

Il ne doit jamais redéfinir la syntaxe, la sémantique ou le contrat hôte.

En cas de divergence, ce sont toujours `SYNTAXE.md`, `SEMANTIQUE.md` et `HOST_ABI.md` qui font autorité.

### Syntaxe

- définition des mots
- mots utilisateur définis dans des blocs `module @... end-module`
- définitions utilisateur top-level invalides
- références externes aux mots utilisateur via `@module.word`
- résolution statique module-aware (local, module, alias, qualifié)
- imports explicites et aliases explicites (pas de wildcard)
- racines de namespace réservées : `host`, `list`, `map`, `result`
- cycles d’import interdits
- signatures
- constructions vides typées explicitement : `[]:List<T>` et `map.empty:Map<K,V>`
- visibilité par défaut privée
- visibilité interne `pub`
- déclaration d’export module-locale `export : word`
- noms visibles hôte canoniques `@module.word` (avec `@` conservé)
- annotation d’effet `dirty` pour les mots Nicole ; `pure` n’existe que dans la surface ABI de `require`
- sous-mots
- noms qualifiés
- fondations lexicales/grammaticales pour `@module.word`, `module`, `end-module`, `import`, `include` (sémantique différée)
- déclaration source-visible des capacités hôte via `module @host` et `require`
- déclaration source-visible des types opaques hôte via `module @host` et `opaque`
- imports module-locaux explicites depuis `@host` pour les capacités et les types opaques hôte
- imports groupés comme sucre de surface seulement, par exemple :

```nicole
import @host.io.{
  open-file
  close-file
  FileHandle
} as io
```

- imports groupés `as *` autorisés seulement pour une sélection explicite de symboles, par exemple :

```nicole
import @host.console.{
  log
  read-line
} as *
```

- `as *` n’introduit pas de sémantique de wildcard import et reste moins auditable qu’un alias préfixé
- listes immuables, concaténation et décomposition
- opérations de liste `list.len`, `list.is-empty`, `list.get`, `list.first`, `list.last`, `list.set`, `list.append`, `list.concat`, `list.reverse`, `list.map`, `list.filter`, `list.fold`, `list.reduce`
- opérations de map `map.empty`, `map.get`, `map.contains`, `map.set`, `map.remove`, `map.len`, `map.is-empty`, `map.keys`, `map.values`
- quotations et fonctions comme valeurs
- quotations de valeur fermées par `;]`
- quotations typées `Quote<{ captures | inputs -- outputs }>`
- quotations dirty typées `DirtyQuote<{ captures | inputs -- outputs }>`
- handlers d’événements

### Sémantique

- pile locale
- pile locale vide au début d’un mot
- stack frame isolée
- portée des variables
- inputs de signature = variables locales immuables
- retours multiples
- un nom visible désigne une seule définition
- résolution statique à la compilation uniquement (pas de lookup dynamique)
- récursion
- if / case
- `case` avec guards en v1
- structures de contrôle retenues
- exécution embarquée sur bytecode
- extension possible vers un JIT futur, sans promesse de stabilité d’implémentation
- capture par valeur dans les quotations
- pureté implicite + effet `dirty` explicite et vérifié statiquement
- export = programme → hôte via nom canonique `@module.word`
- capacités hôte = hôte → programme via contrat source-visible déclaré dans `module @host`
- types opaques hôte = types nominaux ABI sous noms canoniques `@host.*`, déclarés dans `module @host`
- aucune surface d’appel directe `host.*` en source ; l’interaction hôte passe par `module @host`, puis par des imports explicites et des aliases module-locaux
- import des symboles hôte au niveau module, sans visibilité globale implicite
- imports groupés = désignation explicite de dépendances, sans injection de namespace implicite
- effet ABI (`pure` ou `dirty`) déclaré explicitement par `require`
- runtime de l’hôte considéré comme trusted, mais contraint à satisfaire le contrat ABI déclaré

### Types

- Int
- Float
- Bool
- String
- List<T>
- Map<K,V>
- ListError
- MapError
- Result<V,E>
- Quote<{ captures | inputs -- outputs }>
- DirtyQuote<{ captures | inputs -- outputs }>
- Unit

et éventuelles extensions futures.

### Exemples

Produire des programmes complets commentés :

- exemples valides
- exemples invalides
- sortie attendue
- comportement attendu
- erreurs attendues

`EXAMPLES.md` ne sert pas à inventer le langage.

Son rôle est de :

- montrer les usages normaux
- illustrer les formes idiomatiques
- servir de référence pédagogique
- devenir plus tard une base de tests de conformité

Les exemples ne doivent jamais :

- introduire une nouvelle syntaxe
- inventer de nouvelles primitives
- modifier la sémantique
- supposer une VM concrète
- supposer une FFI native

`INVALID_EXAMPLES.md` ne sert pas à définir de nouvelles interdictions.

Chaque exemple invalide doit être justifié par une règle déjà présente dans :

- `SYNTAXE.md`
- `SEMANTIQUE.md`
- `HOST_ABI.md`

Si une invalidité ne peut pas être démontrée depuis la spécification, elle ne doit pas apparaître dans `INVALID_EXAMPLES.md`.

Les exemples invalides servent à vérifier la spécification, pas à l’étendre.

---

## Résultat attendu

À la fin, le dépôt doit ressembler à un vrai manuel de référence :

comme la documentation officielle d’un langage.

Pas à un prototype technique.

---

## Priorité

Ordre de travail recommandé :

1. syntaxe figée (déjà validée)
2. sémantique figée (déjà validée)
3. formaliser `HOST_ABI.md`
4. écrire les exemples valides et invalides
5. consolider le manuel de référence

Jamais l’inverse.

## Frontière du projet

- ce dépôt ne produit pas l’implémentation
- une future implémentation devra vivre dans un dépôt séparé
- ce dépôt est la source de vérité
- l’implémentation devra suivre cette documentation, pas l’inverse
- le présent dépôt reste exclusivement documentaire
