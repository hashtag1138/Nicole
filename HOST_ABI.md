# HOST_ABI.md

# Contrat hôte du langage Nicole

Ce document formalise le contrat conceptuel entre un programme Nicole et l’hôte qui l’embarque.

Il décrit les frontières d’intégration du langage :

- `export` : mot du programme appelable par l’hôte
- `module @host` / `require` : déclarations source-visibles des capacités hôte requises par le programme

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
2. le programme Nicole déclare explicitement certaines capacités hôte requises, que l’hôte doit satisfaire.

Ces deux directions sont distinctes.

Un mot `export` appartient au programme Nicole mais peut être invoqué par l’hôte.

Une capacité déclarée dans `module @host` appartient au contrat ABI requis par le programme. Elle n’est pas définie comme mot Nicole ordinaire dans le code utilisateur, mais elle devient importable depuis `@host`.

L’effet (`pure` ou `dirty`) d’une capacité hôte fait partie du contrat ABI déclaré par `require`.

Dans ce contexte, `pure` appartient uniquement à la surface ABI de `require` ; il ne devient pas un modificateur général des définitions de mots Nicole.

Il n’existe plus de surface source Nicole où le programme appelle directement `host.*` comme des mots normaux.

En revanche, la terminologie `host.*` reste valide pour les types opaques hôte et plus généralement comme vocabulaire ABI/type.

Cette évolution ne modifie pas les builtins `list.*`, `map.*` et `result.*`.

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
module @host
  require console.log { msg:String -- } dirty
end-module

module @app
  import @host.console.log as console.log

  dirty : handle-message { msg:String -- }
    msg console.log
  ;
  export : handle-message
end-module
```

Dans cet exemple, l’hôte invoque `@app.handle-message` avec une valeur de type `String`.
Le mot ne renvoie aucune valeur.

---

# 3. `module @host` et `require` : contrat ABI déclaré par le programme

`module @host` est la surface de déclaration ABI réservée du langage.

Il ne s’agit pas d’un module utilisateur normal.

Il sert à déclarer les capacités hôte requises par le programme Nicole.

## Rôle de `module @host`

Un bloc `module @host` :

- déclare des capacités hôte requises
- contribue au contrat ABI visible en source
- n’introduit pas de logique exécutable Nicole
- n’expose pas de mots utilisateur ordinaires

Les modules applicatifs consomment ensuite ces capacités uniquement via des imports depuis `@host`.

Exemple :

```nicole
module @host
  require console.log { msg:String -- } dirty
  require console.read-line { -- line:String } dirty
end-module

module @app
  import @host.console.log as console.log
  import @host.console.read-line as console.read-line

  dirty : main { -- }
    "hello" console.log
    console.read-line
    console.log
  ;
end-module
```

## Rôle de `require`

Un `require` est l’unité normative de déclaration ABI d’une capacité hôte.

Forme canonique :

```nicole
require console.log { msg:String -- } dirty
```

Chaque `require` déclare :

- un chemin de capacité
- une signature
- un effet ABI explicite (`pure` ou `dirty`)
- une capacité importable depuis `@host`

Le chemin déclaré après `require` est relatif à `@host`.

Ainsi :

```nicole
require console.log { msg:String -- } dirty
```

désigne la capacité importable comme `@host.console.log`.

Cette déclaration fait partie du contrat ABI normatif du programme.

## Contrat consolidé `@host`

`@host` est fragmentable à travers plusieurs fichiers.

Toutes les déclarations `module @host` contribuent à un seul contrat ABI hôte consolidé.

Règles normatives :

- seul `@host` bénéficie de cette fragmentabilité
- l’ordre des fragments n’affecte pas la signification du contrat consolidé
- deux déclarations identiques pour le même chemin de capacité sont autorisées
- deux déclarations divergentes pour le même chemin de capacité constituent une erreur ABI

Dans ce document, “identiques” signifie :

- même chemin de capacité
- même signature
- même effet ABI

Exemple conceptuel :

```nicole
module @host
  require console.log { msg:String -- } dirty
end-module
```

```nicole
module @host
  require console.read-line { -- line:String } dirty
end-module
```

Le contrat ABI consolidé contient alors les deux capacités requises.

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

## Pour les capacités déclarées par `require`

Une capacité hôte déclarée par `require` est une entité typée du contrat ABI.

Le programme n’a pas à connaître l’implémentation concrète de cette capacité, mais il doit connaître son contrat de type.

Chaque `require` fournit donc au minimum :

- le chemin de capacité
- la signature
- l’effet ABI (`pure` ou `dirty`)

La déclaration d’effet est obligatoire en v1.

Il n’existe pas de valeur implicite par défaut pour l’effet ABI.

Une capacité déclarée dans le contrat consolidé doit être satisfaite par le runtime si le programme la requiert.

## Types opaques hôte

Le contrat d’intégration peut aussi déclarer des types opaques hôte.

Pour chaque type opaque hôte, le contrat doit fournir au minimum :

- son nom canonique sous `host.*`
- son genre conceptuel : opaque
- son identité nominale

Les noms imbriqués sont autorisés :

- `host.FileHandle`
- `host.io.FileHandle`
- `host.net.TcpSocket`

Un type opaque hôte n’est jamais défini par un mot Nicole utilisateur.

S’il apparaît dans une signature visible à l’ABI, il doit être déclaré explicitement par le contrat hôte.

## Unicité des noms ABI

Dans le contrat consolidé, un chemin de capacité désigne une seule capacité hôte.

Le contrat ABI ne définit donc pas plusieurs bindings concurrents sous le même chemin visible.

La v1 ne définit aucun mécanisme de surcharge dynamique, de fallback implicite ou de sélection à l’exécution entre plusieurs capacités déclarées sous le même chemin.

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

## Pour les capacités hôte déclarées

Le programme ne peut consommer une capacité hôte qu’à travers le contrat consolidé déclaré dans `@host`.

L’hôte doit :

- satisfaire chaque capacité requise par ce contrat consolidé
- respecter la signature déclarée
- respecter l’effet ABI déclaré
- signaler toute absence ou tout échec de satisfaction comme une erreur d’intégration

Le contrat hôte n’autorise pas de conversions implicites au niveau de la frontière.

Il n’autorise pas non plus d’inférence de type dynamique au moment de l’appel.

Le runtime doit satisfaire une signature déjà connue et déjà vérifiée.

La métadonnée d’effet :

- ne modifie pas la compatibilité des types ABI
- ne modifie pas les règles de frontière de valeurs
- ne remplace pas la vérification de signature

---

# 6. Erreurs d’intégration

Une erreur d’intégration est un échec de liaison entre le programme Nicole et l’hôte.

Ce n’est ni une erreur normale représentée par `Result`, ni une erreur de simple logique métier du programme.

## Cas typiques

- deux `require` divergents déclarent le même chemin de capacité
- une capacité déclarée par le contrat consolidé `@host` ne peut pas être satisfaite par l’hôte
- une signature déclarée dans le contrat ABI ne correspond pas à la capacité fournie
- un mot exporté est demandé par l’hôte mais n’est pas exposé

## Erreur statique ou erreur d’exécution

Si le contrat ABI déclaré est incohérent en lui-même, l’erreur doit être détectée avant exécution.

Si le contrat ABI déclaré est valide mais que l’hôte ne peut pas le satisfaire, l’erreur relève du contrat d’intégration.

Si l’environnement hôte est dynamique et que la satisfaction disparaît ou n’existe pas au moment de l’exécution, l’erreur peut apparaître à l’exécution.

Dans tous les cas, il s’agit d’une erreur d’intégration.

Lorsqu’elle apparaît à l’exécution, une erreur d’intégration constitue aussi une erreur de contrat d’exécution.

## Différence avec `Result`

Une erreur d’intégration n’est pas un `Result`, sauf si la capacité hôte elle-même a explicitement été définie pour renvoyer un `Result`.

Dans ce cas, le `Result` fait partie du contrat de la capacité, pas du mécanisme de satisfaction ABI lui-même.

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

- une capacité hôte déclarée ne reçoit pas de `Quote<{ ... }>` ni de `DirtyQuote<{ ... }>` en entrée
- une capacité hôte déclarée ne retourne pas de `Quote<{ ... }>` ni de `DirtyQuote<{ ... }>`
- un mot `export` n’expose pas de `Quote<{ ... }>` ni de `DirtyQuote<{ ... }>` en entrée
- un mot `export` n’expose pas de `Quote<{ ... }>` ni de `DirtyQuote<{ ... }>` en sortie

Cette limitation garde la frontière ABI simple et orientée données, même lorsque certaines valeurs de données sont opaques et gérées par l’hôte.

Le cycle de vie d’un type opaque hôte reste contrôlé par l’hôte.

En particulier :

- une opération de fermeture explicite reste une capacité hôte déclarée ordinaire
- aucune finalisation automatique n’est garantie par la v1
- le comportement d’une valeur déjà fermée relève du contrat de la capacité hôte utilisée

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

- une capacité hôte déclarée mais non satisfiable au moment de l’appel
- primitive fournie par intégration mais non satisfaisable au moment de l’appel
- `list.reduce` sur une liste vide non prouvable statiquement

Ce type d’erreur n’est pas un `Result`.

## Erreur d’intégration

Une erreur d’intégration est la catégorie spécifique d’erreur liée à la frontière entre le programme Nicole et l’hôte.

Elle peut être détectée avant exécution si le contrat ABI déclaré est incohérent ou si sa satisfaction est connue impossible statiquement, ou à l’exécution dans un environnement dynamique.

Lorsqu’elle apparaît à l’exécution, elle constitue aussi une erreur de contrat d’exécution.

---

# 9. Frontière de vérification et d’exécution

L’hôte exécute un programme Nicole déjà vérifié.

La frontière ABI v1 n’implique donc pas :

- parsing dynamique du programme
- checking dynamique du programme
- inférence de type à l’exécution

Le langage vérifie :

- la cohérence des déclarations `require`
- la visibilité des capacités importées selon les règles statiques du langage
- la compatibilité ABI des signatures déclarées
- la distinction entre contrat ABI déclaré et contrat ABI fourni

Le runtime doit satisfaire le contrat ABI consolidé déjà déclaré.

Le runtime reste toutefois trusted : la spécification valide la cohérence déclarée et la compatibilité observable, mais elle ne prouve pas la correction interne de l’implémentation hôte.

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
