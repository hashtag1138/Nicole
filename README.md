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
- avec surcharge par types d’entrée
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
- `HOST_ABI.md` : priorité actuelle ; contrat conceptuel entre le programme Nicole et l’hôte embarquant (`host.*`, `export`)

Les règles normatives sur `export`, `host.*`, `Result`, les erreurs d’intégration et la disponibilité des mots hôte vivent dans `HOST_ABI.md`.

`HOST_ABI.md` reste une spécification conceptuelle et ne doit pas dériver vers une API C, une ABI binaire, une FFI Rust/Lua, une représentation mémoire concrète, ni des détails de runtime.

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
- signatures
- visibilité par défaut privée
- visibilité interne `pub`
- exposition à l’hôte `export`
- sous-mots
- noms qualifiés
- mots fournis par l’hôte via le préfixe réservé `host.`
- listes immuables, concaténation et décomposition
- opérations de liste `list.len`, `list.get`, `list.set`, `list.concat`, `list.map`, `list.fold`, `list.reduce`
- quotations et fonctions comme valeurs
- quotations typées `Quote<{ captures | inputs -- outputs }>`
- handlers d’événements

### Sémantique

- pile locale
- stack frame isolée
- portée des variables
- retours multiples
- surcharge
- récursion
- if / case
- structures de contrôle retenues
- exécution embarquée sur bytecode
- extension possible vers un JIT futur, sans promesse de stabilité d’implémentation
- capture par valeur dans les quotations
- export = programme → hôte
- host.* = hôte → programme

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
