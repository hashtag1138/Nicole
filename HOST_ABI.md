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

`export` est une déclaration module-locale :

```nicole
export : word
```

Règles normatives :

- `export : word` est une déclaration uniquement
- elle apparaît dans le module qui définit `word`
- `word` doit exister dans ce même module
- `export` ne définit pas un nouveau mot
- `export` ne crée pas d’alias visible dans le programme Nicole
- `export` n’utilise pas les aliases d’import
- `export` ne modifie ni signature, ni typage, ni pureté/dirty, ni récursion du mot référencé
- `pub` règle la visibilité Nicole, `export` règle la visibilité hôte
- `export` hors module est invalide
- `export` sur un sous-mot exécutable est invalide en v1

## Nom canonique visible hôte

Le nom canonique visible côté hôte est :

```text
@module.word
```

Propriétés :

- le `@` initial est conservé
- le nom est dérivé du module définissant et du mot référencé
- les aliases d’import n’affectent jamais ce nom
- le nom canonique est le seul point de liaison hôte normatif

## Unicité et collisions

Un nom canonique visible hôte désigne un seul mot exporté.

Conséquences :

- les noms canoniques visibles hôte doivent être uniques dans le programme
- une déclaration `export` dupliquée produisant le même nom canonique est invalide
- deux déclarations différentes ne peuvent jamais produire le même nom canonique

Exemple valide :

```nicole
module @app
  : run { -- code:Int }
    0
  ;
  export : run
end-module
```

Nom visible hôte : `@app.run`.

Exemple invalide (duplication) :

```nicole
module @app
  : run { -- code:Int }
    0
  ;
  export : run
  export : run
end-module
```

## Appel conceptuel par l’hôte

L’hôte appelle un mot exporté en sélectionnant son nom canonique `@module.word` et en fournissant les valeurs d’entrée attendues par sa signature.

Le programme exécute ce mot dans sa frame propre et renvoie exactement les sorties déclarées.

L’hôte ne reçoit que ces sorties déclarées, dans l’ordre de la signature.

L’hôte ne voit pas la pile locale interne du mot.

## Contrat de retour

Pour un mot exporté, la conformité du retour relève de la sémantique du langage.

Un mot Nicole défini dans le programme ne peut pas avoir un retour opaque arbitraire pour l’hôte.

En revanche, un mot exporté peut utiliser un type opaque hôte déclaré par le contrat ABI si ce type figure explicitement dans la signature visible à l’ABI.

Sa signature doit être respectée exactement.

La signature d’un mot exporté fait partie du contrat ABI exposé à l’hôte.

Le corps du mot exporté doit donc être entièrement vérifié avant toute exécution.

Exemple conceptuel :

```nicole
module @app
  dirty : handle-message { msg:String -- }
    msg host.log
  ;
  export : handle-message
end-module
```

Dans cet exemple, l’hôte invoque `@app.handle-message` avec une valeur de type `String`.
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
module @abi.host_usage
  dirty : save-log { msg:String -- }
    msg host.log
  ;
end-module
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

Le contrat d’intégration peut aussi déclarer des types opaques hôte.

Pour chaque type opaque hôte, le contrat doit fournir au minimum :

- son nom canonique sous `host.*`
- son genre conceptuel : opaque
- son identité nominale

Les noms imbriqués sont autorisés :

- `host.FileHandle`
- `host.io.FileHandle`
- `host.net.TcpSocket`

Un type opaque hôte n’est jamais déclaré par le code source Nicole.

S’il apparaît dans une signature visible à l’ABI, il doit être déclaré explicitement par le contrat hôte.

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

De même, dans l’espace des types visibles à l’ABI, un nom canonique `host.*` doit désigner un seul type opaque hôte.

L’identité d’un type opaque hôte est nominale : deux noms canoniques distincts désignent deux types distincts.

Aucun mécanisme d’alias de types opaques hôte n’est défini en v1.

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
- types opaques hôte `host.*` déclarés par le contrat

Règles :

- `List<T>` n’est autorisé que si `T` est lui-même une valeur compatible avec l’ABI v1
- `Map<K,V>` n’est autorisé que si `K` et `V` sont eux-mêmes compatibles avec l’ABI v1
- `Map<K,V>` n’est autorisé que si `K` reste l’un des types de clé valides en v1 : `Int`, `String`, `Bool`
- `Result<T,E>` n’est autorisé que si `T` et `E` sont eux-mêmes compatibles avec l’ABI v1
- `ListError` et `MapError` sont eux-mêmes des valeurs ABI v1 autorisées comme types d’erreur fermés du langage
- un type opaque hôte `host.*` n’est autorisé que s’il est déclaré explicitement par le contrat hôte
- un type opaque hôte `host.*` peut apparaître récursivement dans `List<T>`, `Map<K,V>` et `Result<T,E>` si les autres contraintes ABI restent satisfaites
- un type opaque hôte `host.*` peut être une valeur de `Map<K,V>`, mais pas une clé de map en v1

Les types opaques hôte restent des valeurs opaques nominales du point de vue Nicole.

Leur rendu de debug éventuel est laissé à l’implémentation.

Les quotations ne franchissent pas l’ABI hôte en v1.

Autrement dit :

- un mot `host.*` ne reçoit pas de `Quote<{ ... }>` ni de `DirtyQuote<{ ... }>` en entrée
- un mot `host.*` ne retourne pas de `Quote<{ ... }>` ni de `DirtyQuote<{ ... }>`
- un mot `export` n’expose pas de `Quote<{ ... }>` ni de `DirtyQuote<{ ... }>` en entrée
- un mot `export` n’expose pas de `Quote<{ ... }>` ni de `DirtyQuote<{ ... }>` en sortie

Cette limitation garde la frontière ABI simple et orientée données, même lorsque certaines valeurs de données sont opaques et gérées par l’hôte.

Le cycle de vie d’un type opaque hôte reste contrôlé par l’hôte.

En particulier :

- une opération de fermeture explicite reste un mot `host.*` ordinaire
- aucune finalisation automatique n’est garantie par la v1
- le comportement d’une valeur déjà fermée relève du contrat du mot hôte utilisé

Toute extension future de l’ABI vers des callbacks, quotations, handles exécutables, objets hôte structurés ou aliases de types opaques hôte reste explicitement différée.

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
- un système d’ownership ou de move semantics pour les types opaques hôte
- des destructeurs ou garanties de finalisation automatique
- des handles nullables
- un mécanisme d’alias pour les types opaques hôte
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
