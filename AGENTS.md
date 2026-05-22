# AGENTS.md

## Mission

Ce dépôt sert uniquement à produire la documentation du langage.

Objectif :

- définir la spécification du langage
- écrire le manuel de référence
- produire des exemples valides et invalides
- expliquer les choix de design
- documenter la sémantique attendue

Ce dépôt ne sert PAS à implémenter le langage.

`SYNTAXE.md` est la source canonique de la syntaxe v1.
Codex ne doit plus modifier la syntaxe sauf demande explicite.

---

## Interdictions strictes

Ne pas produire :

- lexer
- parser
- AST
- bytecode
- VM
- runtime
- compilateur
- backend LLVM
- interpréteur
- benchmark
- optimisation d’exécution
- infrastructure technique non liée à la documentation

Si une décision d’implémentation apparaît, elle doit rester descriptive et conceptuelle, jamais sous forme de code.

Ne pas réintroduire :

- `const`
- `let`
- `extern`
- signatures avec `->`
- syntaxes alternatives du type `word add : Int Int -> Int`

---

## Livrables attendus

Produire uniquement des documents markdown tels que :

- LANGUAGE_SPEC.md
- REFERENCE_MANUAL.md
- EXAMPLES.md
- INVALID_EXAMPLES.md
- DESIGN_NOTES.md
- GLOSSARY.md
- SEMANTIQUE.md
- HOST_ABI.md

Les documents non encore présents dans le dépôt doivent être compris ici comme des livrables futurs possibles.

Le nom exact peut évoluer si cela améliore la clarté.

---

## Style attendu

Le langage doit être décrit comme un vrai langage de programmation :

- précis
- cohérent
- non ambigu
- pédagogique
- orienté référence

Toujours inclure :

- exemples valides
- contre-exemples invalides
- comportement attendu
- explication de pile quand pertinent
- justification des règles importantes

---

## Philosophie du langage

Le langage visé est :

- concaténatif
- typé
- à stack frames isolées
- avec variables locales immuables
- avec sous-mots privés, éventuellement nommés de façon qualifiée en interne
- avec noms explicites et résolution statique par nom visible unique
- sans macros
- sans métaprogrammation
- sans capture lexicale implicite
- sans pile globale partagée
- uniquement embarqué
- avec contrat d’intégration réservé via le préfixe `host.`
- pensé autour d’une cible conceptuelle bytecode
- JIT éventuellement plus tard, sans en faire une promesse de v1

La priorité de travail devient :

1. formaliser `HOST_ABI.md`
2. produire `EXAMPLES.md` et `INVALID_EXAMPLES.md`
3. consolider `REFERENCE_MANUAL.md`

`HOST_ABI.md` doit décrire le contrat conceptuel entre le programme Nicole et l’hôte embarquant. Il ne doit pas définir une API C, Rust, Lua, LLVM, ni une représentation mémoire concrète.

Les règles normatives sur `export`, `host.*`, `Result`, les erreurs d’intégration et la disponibilité des mots hôte vivent dans `HOST_ABI.md`.

`SYNTAXE.md` est figé.
`SEMANTIQUE.md` est considéré comme figé pour la v1, sauf contradiction réelle ou bug sémantique évident.

Codex ne doit plus faire de micro-corrections stylistiques sur `SEMANTIQUE.md`.

Codex ne doit pas rouvrir les décisions déjà prises sur la syntaxe ou la sémantique, sauf contradiction réelle signalée explicitement.

Le style recherché est :

Forth moderne, strict, lisible, sans magie.

## Règle spécifique pour `EXAMPLES.md` et `INVALID_EXAMPLES.md`

`EXAMPLES.md` ne sert pas à redéfinir le langage.

Son rôle est de :

- montrer comment écrire de vrais programmes en Nicole
- illustrer les usages normaux du langage
- montrer les formes idiomatiques recommandées
- servir de référence de lecture pour un utilisateur humain
- pouvoir devenir plus tard des tests de conformité d’implémentation

Les exemples doivent utiliser uniquement ce qui est déjà défini dans :

- `SYNTAXE.md`
- `SEMANTIQUE.md`
- `HOST_ABI.md`

Les exemples ne doivent pas :

- introduire de nouvelle syntaxe
- inventer de nouvelles primitives
- modifier la sémantique
- contourner les règles de pile
- supposer une VM concrète
- supposer une FFI native
- dériver vers du pseudo-code d’implémentation

`INVALID_EXAMPLES.md` doit montrer explicitement ce qui doit être rejeté.

Exemples attendus :

- erreur de typage
- ambiguïté de résolution
- mauvais retour
- branches incompatibles (`if`, `case`)
- quotation invalide
- usage interdit de `host.*`
- violations de contrat détectables statiquement

Chaque exemple invalide doit expliquer précisément pourquoi il est rejeté.

`SYNTAXE.md`, `SEMANTIQUE.md` et `HOST_ABI.md` sont les seules sources normatives de la v1.

`EXAMPLES.md` et `INVALID_EXAMPLES.md` servent uniquement à illustrer, expliquer et vérifier ces règles.

Ils ne doivent jamais :

- redéfinir une règle
- corriger implicitement une ambiguïté
- introduire une interprétation alternative
- devenir une nouvelle source de vérité

Si un exemple semble contredire la spécification, c’est l’exemple qui doit être corrigé.

La syntaxe, la sémantique et le contrat hôte ne changent pas à cause des exemples, sauf contradiction réelle explicitement validée.

Les exemples doivent privilégier la clarté de lecture.

La forme idiomatique simple doit être préférée.

Un exemple pédagogique n’a pas pour but de montrer la version la plus “maligne” ou la plus abstraite.

Il faut éviter les constructions inutilement complexes si une version plus simple montre mieux la règle.

Exemple : préférer

```nicole
: add-one { x:Int -- y:Int }
  x 1 +
;
```

à une version inutilement sophistiquée qui complique la lecture sans apporter de valeur sémantique.

Les exemples doivent être pensés pour :

- apprendre le langage
- relire rapidement une règle
- servir plus tard de tests de conformité

et non pour démontrer une virtuosité de style.

## Règle spécifique pour `INVALID_EXAMPLES.md`

`INVALID_EXAMPLES.md` ne sert pas à définir une spec parallèle.

Il sert uniquement à :

- montrer ce qui doit être rejeté
- rendre explicites les erreurs statiquement détectables
- éviter les implémentations divergentes
- servir plus tard de base de tests de rejet

Chaque exemple invalide doit :

- être réellement invalide selon `SYNTAXE.md`, `SEMANTIQUE.md` ou `HOST_ABI.md`
- violer une règle déjà définie
- expliquer précisément pourquoi il est rejeté
- indiquer clairement la règle concernée

Un exemple invalide ne doit jamais :

- inventer une nouvelle interdiction
- supposer une règle implicite non écrite
- corriger la spécification par l’exemple
- devenir une source normative parallèle

Si une invalidité ne peut pas être démontrée depuis la spécification existante, elle ne doit pas apparaître dans `INVALID_EXAMPLES.md`.

En cas de doute, la spécification prime toujours sur l’intuition.

---

## Règle importante

Toujours privilégier :

clarté > puissance implicite

explicite > magique

spécification > implémentation

La syntaxe et la sémantique sont déjà figées pour la v1.

Le travail porte maintenant sur :

- `HOST_ABI.md`
- les exemples valides et invalides
- le manuel de référence

avant toute réflexion d’implémentation concrète.

AGENTS.md doit rester court, strict, orienté contraintes, et ne pas laisser place à une réinvention du langage.
