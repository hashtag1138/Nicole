# HOST_ABI.md

# Contrat hôte du langage Nicole

Ce document formalise le contrat conceptuel entre un programme Nicole et l’hôte qui l’embarque.

Il décrit les frontières d’intégration du langage :

- `export` : mot du programme appelable par l’hôte
- `host.*` : mot de l’hôte appelable par le programme

Ce document ne définit pas :

- une API C
- une ABI binaire
- une FFI Rust
- une FFI Lua
- des bindings LLVM
- une représentation mémoire concrète
- des structures runtime
- des conventions de pointeurs
- un format binaire de bytecode
- des détails de VM

Le niveau visé est celui d’une spécification de langage, pas celui d’une implémentation.

---

# 1. Principes généraux

Le contrat hôte sépare deux rôles :

1. le programme Nicole expose certains mots à l’hôte ;
2. l’hôte expose certains mots au programme Nicole.

Ces deux directions sont distinctes.

Un mot `export` appartient au programme Nicole mais peut être invoqué par l’hôte.

Un mot `host.*` appartient au contrat fourni par l’hôte et peut être invoqué par le programme Nicole.

L’effet (`pure` ou `dirty`) d’un mot `host.*` appartient au contrat hôte.

Il n’existe pas de syntaxe source Nicole du type `dirty host.foo { ... }`.

Le contrat hôte ne crée pas de mutation implicite, ne partage pas de pile globale et ne contourne pas les règles de typage ou de retour définies ailleurs dans la documentation.

---

# 2. `export` : mots du programme appelables par l’hôte

`export` désigne un mot défini par le programme Nicole et rendu visible à l’hôte.

## Garanties d’un mot exporté

Un mot exporté garantit :

- un nom d’export unique dans le programme
- une signature connue
- des entrées typées
- des sorties typées
- une discipline de retour identique à celle de tout mot Nicole
- l’exécution dans une stack frame isolée
- un statut d’effet vérifié (`pure` ou `dirty`) dérivé de son corps
- pour la v0.16, la garantie d’appel récursif direct en position terminale s’applique uniquement aux frames d’exécution Nicole ; le comportement de pile native reste non spécifié

Le mot exporté reste un mot du programme.

Il peut aussi être appelé depuis d’autres mots du programme, comme tout mot visible.

`export` ne rend pas un mot dirty par lui-même.

Le statut d’effet d’un export est déterminé par la sémantique du mot, puis validé contre son annotation éventuelle.

L’hôte peut exposer ou inspecter cette information d’effet comme métadonnée de contrat, sans que cela change les règles de typage ABI.

## Appel conceptuel par l’hôte

L’hôte appelle un mot exporté en sélectionnant ce mot par son nom d’export et en lui fournissant les valeurs d’entrée attendues par sa signature.

Le nom d’export est le point de liaison public entre le programme et l’hôte.

Au niveau de l’interface hôte, un nom d’export désigne un seul point d’entrée.

Deux mots exportés ne peuvent jamais partager le même nom d’export.

Plus généralement, un nom d’export doit désigner un seul mot exporté.

Toute collision de noms d’export est invalide et doit être rejetée comme une erreur de contrat détectable statiquement.

Exemple invalide :

```nicole
export : entry { -- n:Int }
  1
;

export : entry { -- text:String }
  "hello"
;
```

Ce programme est invalide :

- `entry` est un seul nom public côté hôte
- l’hôte ne peut pas lier un même nom d’export à deux définitions distinctes

Alternative valide :

```nicole
export : entry.int { -- n:Int }
  1
;

export : entry.text { -- text:String }
  "hello"
;
```

Le programme exécute alors le mot dans sa frame propre et renvoie exactement les sorties déclarées.

L’hôte ne reçoit que ces sorties déclarées, dans l’ordre défini par la signature.

L’hôte ne voit pas la pile locale interne du mot.

## Contrat de retour

Pour un mot exporté, la conformité du retour relève de la sémantique du langage.

Un mot Nicole défini dans le programme ne peut pas avoir un retour “opaque” pour l’hôte.

Sa signature doit être respectée exactement.

La signature d’un mot exporté fait partie du contrat ABI exposé à l’hôte.

Le corps du mot exporté doit donc être entièrement vérifié avant toute exécution.

Exemple conceptuel :

```nicole
export dirty : app.on-message { msg:String -- }
  msg host.log
;
```

Dans cet exemple, l’hôte peut invoquer `app.on-message` avec une valeur de type `String`.
Le mot ne renvoie aucune valeur.

---

# 3. `host.*` : mots de l’hôte appelables par le programme

`host.*` désigne des mots fournis par l’hôte et appelables depuis le programme Nicole.

## Garanties d’un mot `host.*`

Un mot `host.*` garantit :

- un nom unique dans le contrat d’intégration
- une signature connue ou déclarée par le contrat d’intégration
- des entrées typées
- des sorties typées si le mot en déclare
- une sémantique stable du point de vue du programme Nicole
- une déclaration d’effet explicite (`pure` ou `dirty`)

Le programme peut appeler un mot `host.*` comme il appelle un mot normal, mais le mot n’est pas défini dans le code Nicole.

Le contrat de type d’un mot `host.*` fait partie du contrat ABI fourni par l’hôte.

Le contrat d’effet d’un mot `host.*` fait aussi partie de ce contrat ABI.

Forme conceptuelle canonique d’une entrée hôte :

```text
host.log

signature:
{ msg:String -- }

availability:
required

effect:
dirty
```

Autre exemple :

```text
host.timezone

signature:
{ -- tz:String }

availability:
required

effect:
pure
```

## Appel conceptuel depuis le programme

Le programme appelle le mot `host.*` selon la discipline de pile définie dans `SEMANTIQUE.md`.

Le mot hôte s’exécute selon son contrat et renvoie ses sorties déclarées sur la pile du programme.

Le programme ne doit pas supposer :

- une représentation mémoire précise
- une stratégie d’allocation
- une identité de pointeur
- une structure de fermeture
- un format de sérialisation particulier

Exemple conceptuel :

```nicole
dirty : save-log { msg:String -- }
  msg host.log
;
```

Ici, le programme appelle un mot fourni par l’hôte et lui transmet une chaîne.

---

# 4. Obligations de typage

Le contrat hôte repose sur le typage statique déjà défini dans le langage.

## Pour `export`

Un mot exporté doit avoir une signature explicite.

L’hôte ne peut appeler ce mot qu’en respectant :

- le nombre d’entrées
- l’ordre des entrées
- les types des entrées
- le nombre de sorties attendues
- l’ordre des sorties attendues
- les types des sorties attendues

## Pour `host.*`

Un mot `host.*` doit aussi être vu comme une entité typée.

Le programme n’a pas à connaître l’implémentation du mot hôte, mais il doit connaître son contrat de type.

Le contrat d’intégration doit donc fournir :

- le nom du mot
- sa signature
- le statut de disponibilité du mot
- son effet (`pure` ou `dirty`)

La déclaration d’effet est obligatoire en v1.

Il n’existe pas de valeur implicite par défaut pour l’effet dans le contrat hôte.

Le statut de disponibilité est conceptuellement l’un des deux suivants :

- requis
- optionnel

L’effet est indépendant du statut de disponibilité :

- un mot requis peut être `pure` ou `dirty`
- un mot optionnel peut être `pure` ou `dirty`

Un mot `host.*` requis doit être présent pour que le contrat soit valide.

Son absence constitue une erreur d’intégration.

Un mot `host.*` optionnel peut être absent sans invalider le contrat en lui-même.

En v1, un appel direct à un mot `host.*` dans le code source suppose que ce mot est requis pour le programme considéré.

Le programme ne peut donc pas appeler directement un mot `host.*` optionnel comme s’il était garanti présent.

La v1 ne définit aucun mécanisme standard de test de présence, de fallback ou d’appel conditionnel d’un mot hôte optionnel.

Le statut “optionnel” peut exister dans le contrat d’intégration comme information conceptuelle ou comme base d’extensions futures, mais il n’autorise pas à lui seul un appel direct en Nicole v1.

Si ces informations sont insuffisantes ou ambiguës, le contrat n’est pas valable pour la v1.

## Unicité des noms hôte

Dans l’espace visible du programme, un nom `host.*` doit désigner un seul mot fourni par le contrat hôte.

Le contrat hôte ne définit donc pas plusieurs bindings concurrents sous le même nom visible.

La v1 ne définit aucun mécanisme de surcharge dynamique, de fallback implicite ou de sélection à l’exécution entre plusieurs bindings `host.*`.

---

# 5. Obligations de contrat

Le contrat hôte impose que les appels respectent les signatures annoncées.

## Pour les mots exportés

L’hôte doit :

- fournir les entrées attendues
- accepter exactement les sorties annoncées
- traiter les erreurs de contrat si le mot ne peut pas être invoqué correctement

Le programme ne peut pas exiger de l’hôte qu’il accepte des entrées d’un autre type ou qu’il ignore des sorties non déclarées.

## Pour les mots `host.*`

Le programme doit :

- appeler le mot avec les types attendus
- ne pas inventer d’arguments
- ne pas attendre de sortie non déclarée

L’hôte doit :

- fournir le mot annoncé
- respecter sa signature
- signaler toute absence ou tout échec de liaison comme une erreur d’intégration

Le contrat hôte n’autorise pas de conversions implicites au niveau de la frontière.

Il n’autorise pas non plus d’inférence de type dynamique au moment de l’appel.

Le binding hôte doit satisfaire une signature déjà connue et déjà vérifiée.

La métadonnée d’effet :

- ne modifie pas la compatibilité des types ABI
- ne modifie pas les règles de frontière de valeurs
- ne remplace pas la vérification de signature

---

# 6. Erreurs d’intégration

Une erreur d’intégration est un échec de liaison entre le programme Nicole et l’hôte.

Ce n’est ni une erreur normale représentée par `Result`, ni une erreur de simple logique métier du programme.

## Cas typiques

- un mot `host.*` est absent alors que le contrat hôte le déclare
- un mot exporté est demandé par l’hôte mais n’est pas exposé
- une signature déclarée par le contrat hôte ne correspond pas à la signature attendue
- l’hôte ne peut pas satisfaire une liaison requise par le programme ou par l’export

## Erreur statique ou erreur d’exécution

Si le contrat hôte est connu statiquement et qu’un mot manque, l’erreur doit pouvoir être détectée avant exécution.

Si l’environnement hôte est dynamique et que la liaison disparaît ou n’existe pas au moment de l’appel, l’erreur peut apparaître à l’exécution.

Dans les deux cas, il s’agit d’une erreur d’intégration.

Lorsqu’elle apparaît à l’exécution, une erreur d’intégration constitue aussi une erreur de contrat d’exécution.

## Différence avec `Result`

Une erreur d’intégration n’est pas un `Result`, sauf si le mot hôte lui-même a explicitement été défini pour renvoyer un `Result`.

Dans ce cas, le `Result` fait partie du contrat du mot, pas du mécanisme de liaison lui-même.

---

# 7. Valeurs franchissant l’ABI en v1

La v1 privilégie des valeurs de données simples à la frontière hôte.

Types autorisés à travers l’ABI v1 :

- `Int`
- `Float`
- `String`
- `Bool`
- `Unit`
- `List<T>`
- `Map<K,V>`
- `Result<T,E>`
- `ListError`
- `MapError`

Règles :

- `List<T>` n’est autorisé que si `T` est lui-même une valeur compatible avec l’ABI v1
- `Map<K,V>` n’est autorisé que si `K` et `V` sont eux-mêmes compatibles avec l’ABI v1
- `Map<K,V>` n’est autorisé que si `K` reste l’un des types de clé valides en v1 : `Int`, `String`, `Bool`
- `Result<T,E>` n’est autorisé que si `T` et `E` sont eux-mêmes compatibles avec l’ABI v1
- `ListError` et `MapError` sont eux-mêmes des valeurs ABI v1 autorisées comme types d’erreur fermés du langage

Les quotations ne franchissent pas l’ABI hôte en v1.

Autrement dit :

- un mot `host.*` ne reçoit pas de `Quote<{ ... }>` ni de `DirtyQuote<{ ... }>` en entrée
- un mot `host.*` ne retourne pas de `Quote<{ ... }>` ni de `DirtyQuote<{ ... }>`
- un mot `export` n’expose pas de `Quote<{ ... }>` ni de `DirtyQuote<{ ... }>` en entrée
- un mot `export` n’expose pas de `Quote<{ ... }>` ni de `DirtyQuote<{ ... }>` en sortie

Cette limitation garde la frontière ABI simple et purement orientée données.

Toute extension future de l’ABI vers des callbacks, quotations, handles exécutables ou objets hôte reste explicitement différée.

---

# 8. Différences de niveau d’erreur

Le dépôt distingue trois catégories.

## Erreur normale

Une erreur normale est un cas attendu du domaine, représenté explicitement par `Result`.

Exemples conceptuels :

- clé absente dans une map
- calcul impossible que l’API choisit d’exprimer explicitement

## Erreur de contrat d’exécution

Une erreur de contrat d’exécution est une violation d’un contrat supposé valide, observée au moment de l’exécution.

Elle couvre des cas comme :

- `host.*` absent dans un environnement dynamique
- primitive fournie par intégration mais non satisfaisable au moment de l’appel
- `list.reduce` sur une liste vide non prouvable statiquement

Ce type d’erreur n’est pas un `Result`.

## Erreur d’intégration

Une erreur d’intégration est la catégorie spécifique d’erreur liée à la frontière entre le programme Nicole et l’hôte.

Elle peut être détectée avant exécution si le contrat hôte est connu statiquement, ou à l’exécution dans un environnement dynamique.

Lorsqu’elle apparaît à l’exécution, elle constitue aussi une erreur de contrat d’exécution.

---

# 9. Frontière de vérification et d’exécution

L’hôte exécute un programme Nicole déjà vérifié.

La frontière ABI v1 n’implique donc pas :

- parsing dynamique du programme
- checking dynamique du programme
- inférence de type à l’exécution

Le contrat hôte doit satisfaire des signatures déjà connues.

Une fois le programme vérifié, l’exécution consomme ce programme vérifié et applique le contrat d’intégration déclaré.

---

# 10. Non-objectifs et limites de la v1

`HOST_ABI.md` ne définit pas :

- un mécanisme concret de découverte dynamique
- un registre d’exports concret
- un protocole de sérialisation
- des callbacks hôte basés sur quotations
- un modèle async/thread
- des valeurs streamées
- des itérateurs
- des générateurs
- une FFI native
- une API ou interface native C, Rust, Lua ou LLVM
- une représentation mémoire des valeurs
- une stratégie d’allocation
- une convention de pointeurs
- un format binaire ou ABI binaire
- des détails de VM ou de runtime

La seule chose normée ici est le contrat conceptuel entre un programme Nicole et un hôte embarquant.

---

# 11. Règle de fond

Le contrat hôte doit rester :

- explicite
- typé
- conceptuel
- stable
- indépendant des détails d’implémentation

Il doit permettre de documenter l’intégration sans transformer le dépôt en spécification de VM ou de FFI.
