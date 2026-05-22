# SEMANTIQUE.md

# Sémantique officielle provisoire du langage Nicole

Ce document formalise le comportement du langage.

La syntaxe de surface est définie et gelée dans `SYNTAXE.md`.
Ce fichier ne redéfinit pas la syntaxe.

## Formes réservées et builtins

Les formes spéciales du langage, les variantes d’erreur fermées et les builtins fournis par le langage ne sont pas redéfinissables en v1.

Cela couvre notamment :

- `if`
- `else`
- `end`
- `case`
- `pub`
- `export`
- `dirty`
- `call`
- `?`
- `Ok!`
- `Err!`
- `MissingKey`
- `OutOfBounds`
- `host`
- `list`
- `map`
- `result`
- `result.*`
- `list.*`
- `map.*`
- `host.*`

Ces noms participent à la résolution visible du programme.

Une définition utilisateur qui tente de réutiliser ou de masquer l’un de ces noms doit être rejetée statiquement.

Le but est de préciser :

- le modèle d’exécution
- les règles de type et de pile
- la résolution des appels
- les structures de contrôle
- les quotations
- les erreurs explicites
- la frontière entre compilation, exécution et contrat hôte

---

# 1. Modèle d’exécution

Le langage s’exécute avec deux niveaux de pile :

- la pile appelante
- la pile locale du mot courant

Chaque mot s’exécute dans une stack frame isolée.

## Appel d’un mot

Lorsqu’un mot est appelé :

1. les arguments sont pris depuis la pile appelante
2. ils deviennent des variables locales immuables
3. la pile locale du mot commence vide
4. le corps du mot s’exécute
5. les valeurs de sortie sont transférées sur la pile appelante

La pile locale n’est pas partagée avec l’appelant.

## Définitions v0.16 pour l’appel récursif direct en position terminale

Les définitions suivantes sont normatives pour la garantie v0.16 :

- frame courante : la frame d’exécution Nicole du mot nommé actuellement en cours d’exécution
- pile d'appels Nicole : la pile conceptuelle des frames d’exécution Nicole actives
- appel récursif direct : un appel dont l'appelé résolu statiquement est exactement le même mot nommé que celui de la frame courante
- position terminale : position d’un chemin de contrôle où, après le retour normal de l’appel, aucune autre opération Nicole n’est exécutée dans la frame courante avant le retour de cette frame
- chemin de contrôle : un chemin d’exécution concret depuis un point donné jusqu’au retour de la frame courante, incluant les choix de branche
- garantie de pile constante : garantie qu’une suite d’appels récursifs directs ne fait pas croître la profondeur de la pile d'appels Nicole

## Garantie v0.16 d’appel récursif direct en position terminale

Un appel récursif direct en position terminale ne doit pas augmenter la profondeur de la pile d'appels Nicole.

Cette garantie est normative pour la v0.16.

Cette garantie concerne uniquement les frames d’exécution Nicole.
Le comportement de pile native, de runtime hôte ou de machine sous-jacente reste non spécifié.

Une implémentation peut réutiliser la frame courante ou la remplacer par une frame équivalente.
Dans tous les cas, le comportement observable du programme doit rester identique.

Portée :

- la garantie s’applique uniquement au mot nommé de la frame courante
- aucune garantie n’est fournie pour la récursion mutuelle
- aucune garantie n’est fournie pour la récursion indirecte
- aucune garantie n’est fournie pour les quotations

## Retour d’un mot

Au retour, la pile locale doit correspondre exactement aux sorties déclarées par la signature.

Règles :

- valeur manquante : erreur
- valeur supplémentaire : erreur
- type incompatible : erreur

Pour les mots définis en Nicole, toute divergence de retour doit être rejetée à la compilation.

Une telle divergence ne relève pas du contrat d’exécution.

Le langage ne conserve pas silencieusement des valeurs en excès.
Une valeur ignorée doit être supprimée explicitement avec `drop`.

Exemples conceptuels :

```nicole
module @semantics.exec
  : ok { -- x:Int }
    1
  ;
end-module
```

```nicole
module @invalid.phase6
  : bad { -- x:Int }
    1 2
  ;
end-module
```

Le second exemple est invalide parce que la sortie attendue n’est pas respectée.

## Sorties multiples

Un mot peut produire zéro, une ou plusieurs valeurs.

L’ordre des sorties suit l’ordre de la signature.

La forme `{ -- }` ne produit aucune valeur.

La forme `{ -- a:Int b:String }` pousse d’abord `a`, puis `b`, de sorte que `b` soit au sommet de la pile appelante après retour.

Exemple :

```nicole
module @semantics.exec
  : pair { -- a:Int b:String }
    1 "ok"
  ;
end-module
```

Après appel, la pile appelante reçoit :

```nicole
[..., 1, "ok"]
```

## `Unit`

La forme `{ -- }` signifie qu’aucune valeur n’est produite.

La forme `{ -- u:Unit }` signifie qu’une valeur est produite, et que cette valeur est de type `Unit`.

`Unit` n’est donc pas équivalent à l’absence de sortie.

Le littéral concret de `Unit` reste un point ouvert si `SYNTAXE.md` ne le fixe pas encore.

---

# 2. Variables locales immuables

Les entrées de signature deviennent des variables locales immuables.

Lire une variable locale pousse sa valeur sur la pile locale courante.

Exemple :

```nicole
module @semantics.exec
  : square { x:Int -- y:Int }
    x x *
  ;
end-module
```

Ici, `x` ne modifie rien.

Il lit la valeur locale `x` et la pousse sur la pile locale.

Règles :

- les variables locales sont en lecture seule
- elles ne peuvent pas être mutées
- elles n’existent que dans le mot courant
- elles ne sont pas visibles dans les sous-mots

Les noms locaux doivent être uniques dans une même frame.

Deux entrées d’une même signature ne peuvent donc pas partager le même nom local.

En revanche, des frames différentes peuvent réutiliser le même nom local sans ambiguïté.

---

# 3. Résolution des appels

La résolution des appels est statique.

Phase 2 établit le modèle obligatoire suivant :

- les définitions de mots utilisateur sont contenues dans des blocs `module @... end-module`
- une définition utilisateur top-level est rejetée
- dans un module, un appel peut utiliser un nom court pour viser un mot du même module
- hors module, un mot utilisateur externe est référencé via `@module.word` avec import correspondant
- dans `module @text`, la forme `@text.word` reste autorisée sans import, mais la forme courte locale est préférée

Phase 3 complète ce modèle :

- la résolution est entièrement statique et contextuelle
- les imports sont des déclarations de compilation uniquement
- les imports existent uniquement au top-level
- les imports ne sont pas des mots exécutables
- les imports n’ont aucun effet de pile
- il n’existe ni import dynamique ni lookup namespace runtime
- les aliases d’import participent aux collisions de noms visibles
- le graphe d’import doit être acyclique

Phase 4 complète le modèle d’exposition hôte :

- `export : word` est une déclaration de compilation, pas un mot exécutable
- `export : word` existe uniquement au top-level interne d’un module (pas dans un sous-mot)
- `export : word` n’a aucun effet de pile
- `export : word` résout `word` dans le module définissant
- le mot référencé doit exister dans ce module
- le nom canonique visible hôte est `@module.word`
- les aliases d’import n’affectent jamais ce nom canonique
- les noms canoniques visibles hôte doivent rester uniques
- sans import, une référence externe `@text.word` reste invalide
- dans `module @text`, la forme `@text.word` vers le module courant reste valide sans import

Ordre de résolution dans un module :

1. noms locaux dans le scope courant
2. mots du même module appelés en nom court
3. aliases d’import visibles
4. noms qualifiés explicites (`@module.word`) autorisés dans le module courant ou via import externe correspondant
5. namespaces réservés/builtins (`host.*`, `list.*`, `map.*`, `result.*`)

Hors module :

- aucun mot utilisateur non qualifié n’est résolu
- un mot utilisateur externe exige `@module.word` et un import correspondant
- un alias n’est utilisable que s’il est introduit explicitement par `import`

Sémantique des imports :

- `import @text` autorise uniquement l’usage qualifié explicite `@text.*` pour les mots publics de `@text`
- `import @text as t` crée une racine alias `t`, utilisable sous la forme `t.word`
- `import @text.split` autorise uniquement `@text.split`
- `import @text.split as split` crée l’alias court `split`
- sans alias, `import @text.split` ne rend pas `split` visible
- sans import, une référence externe `@text.word` est invalide
- la portée des aliases d’import suit l’unité de compilation après inclusion textuelle
- les fragments inclus ne créent pas de scope alias séparé

Racines réservées :

- `host`, `list`, `map`, `result` sont réservées comme racines
- `host.*`, `list.*`, `map.*`, `result.*` restent réservées comme namespaces
- un module utilisateur ne peut pas être `@host`, `@list`, `@map` ou `@result`
- un alias d’import ne peut pas être `host`, `list`, `map` ou `result`
- un nom utilisateur ne peut pas occuper une racine réservée

La collecte des signatures précède l’analyse des corps.

Elle sert à :

- connaître les mots visibles avant validation des appels
- permettre la récursion et la récursion mutuelle
- détecter tôt les collisions de noms visibles

Dans un même espace de résolution, un nom visible doit désigner une seule définition.

La résolution d’un appel se fait donc par le nom dans l’espace donné.

`pub` et les déclarations `export` n’introduisent pas d’espace nominal séparé.

Toute collision visible est une erreur de compilation.

Cette règle évite qu’un appel dépende de valeurs résiduelles présentes sur la pile pour sélectionner une définition.

Les signatures de sortie ne servent jamais à distinguer deux mots, car deux définitions de même nom sont interdites quelles que soient leurs signatures.

Imports et récursion :

- la récursion interne à un module est inchangée
- les cycles d’import sont interdits
- une récursion mutuelle inter-modules qui dépend d’un cycle d’import est invalide

Note de transition :

- certains exemples plus bas gardent une forme top-level legacy
- la règle normative de phase 2 prévaut : une définition utilisateur valide est module-contenue

Exemple invalide :

```nicole
module @invalid.phase6
  : id { x:Int -- y:Int }
    x
  ;

  : id { x:String -- y:String }
    x
  ;
end-module
```

Ces deux définitions sont interdites parce qu’un même nom visible ne peut désigner qu’un seul mot.

Exemple interdit :

```nicole
module @invalid.phase6
  : foo { a:Int b:Int -- r:Int }
    a b +
  ;

  : foo { a:Int b:Int c:Int -- r:Int }
    a b + c +
  ;
end-module
```

Ces deux définitions sont interdites, même si leurs arités diffèrent.

Formes recommandées :

```nicole
module @semantics.resolution
  : id-int { x:Int -- y:Int }
    x
  ;

  : id-string { x:String -- y:String }
    x
  ;

  : foo2 { a:Int b:Int -- r:Int }
    a b +
  ;

  : foo3 { a:Int b:Int c:Int -- r:Int }
    a b + c +
  ;
end-module
```

---

## Effets `pure` / `dirty` en v1

Nicole est pure par défaut.

La v1 n’introduit pas de mot-clé `pure`.

`dirty` est l’annotation d’effet explicite.

Le check d’effet est exact :

- inféré `pure` + annoté `dirty` => erreur
- inféré `dirty` + annotation `dirty` absente => erreur
- inféré `dirty` + annoté `dirty` => valide
- inféré `pure` + sans annotation => valide

Le checker suit l’ordre suivant :

1. inférer l’effet sur le graphe d’appels ;
2. valider l’annotation source contre l’effet inféré.

En v1, seuls les bindings `host.*` peuvent introduire l’impureté directement.

Les builtins du langage sont purs en v1, sauf `call` dont l’effet dépend du type de quotation appelée.

La propagation est transitive :

- appel direct d’un mot dirty => appelant dirty
- appel indirect via d’autres mots => dirty aussi

Règles :

- un mot pur ne peut pas appeler du code dirty
- un mot exporté suit exactement les mêmes règles d’effet que tout autre mot
- `export` ne change jamais l’effet du mot référencé

Le contrôle est statique uniquement.

Il n’existe pas de violation dirty runtime en v1.

`Result`, `Err` et `?` restent orthogonaux à ce système d’effet.

Récursion et récursion mutuelle :

- l’inférence dirty se fait sur les composantes fortement connexes (SCC) du graphe d’appels
- un cycle devient dirty si un membre appelle directement un binding dirty
- un cycle devient dirty si la propagation depuis l’extérieur lui apporte un appel dirty
- la récursion mutuelle reste autorisée ; seul l’effet inféré doit être cohérent avec les annotations

Sous-mots :

- un sous-mot peut être annoté `dirty`
- un parent devient dirty s’il appelle ce sous-mot dirty
- un sous-mot dirty non appelé ne force pas le parent à devenir dirty

L’effet se propage donc par usage, pas par simple présence textuelle.

Interaction avec la garantie v0.16 d’appel récursif direct en position terminale :

- les règles `pure` / `dirty` restent inchangées
- la garantie d’appel récursif direct ne modifie ni l’inférence d’effet, ni les contraintes d’annotation
- un appel récursif direct dirty reste soumis aux mêmes règles d’effet qu’un appel dirty non optimisé

---

# 4. `if`

`if` consomme un `Bool` au sommet de la pile locale.

Syntaxe de surface :

```nicole
condition if
  ...
else
  ...
end
```

Sémantique :

- la condition est consommée depuis la pile locale
- la branche choisie s’exécute dans la même frame
- les deux branches doivent produire le même effet de pile
- la position terminale se détermine localement, chemin de contrôle par chemin de contrôle
- un appel récursif direct est garanti seulement sur les chemins où il est effectivement en position terminale

La validation est statique quand elle est possible.

Même effet de pile signifie :

- même nombre de valeurs produites
- mêmes types
- même ordre
- même pile préexistante préservée

Cette vérification doit être statique quand les branches sont écrites en Nicole.

Exemple :

```nicole
module @semantics.exec
  : abs { x:Int -- y:Int }
    x 0 < if
      0 x -
    else
      x
    end
  ;
end-module
```

Les deux branches laissent la pile locale dans le même état de sortie.

---

# 5. `case`

`case` consomme la valeur à matcher depuis le sommet de la pile locale.

Syntaxe de surface :

```nicole
value case
  pattern => expression
  pattern when guard => expression
  pattern => expression
  _       => expression
end
```

Sémantique :

- la valeur à matcher est consommée
- les branches sont testées dans l’ordre
- une branche est compatible si son pattern matche
- si une branche compatible possède un guard, ce guard est évalué seulement après le matching de son pattern
- une branche est sélectionnée seulement si son pattern matche et si son guard éventuel évalue à `true`
- si le pattern matche mais que le guard évalue à `false`, le matching continue vers les branches suivantes
- la première branche sélectionnée est exécutée
- `_` match tout ce qui n’a pas été retenu avant
- toutes les branches doivent produire le même effet de pile
- le guard lui-même n’est jamais en position terminale
- la position terminale du corps de branche se détermine localement, chemin de contrôle par chemin de contrôle
- un appel récursif direct est garanti seulement sur les chemins où il est effectivement en position terminale

Même effet de pile signifie :

- même nombre de valeurs produites
- mêmes types
- même ordre
- même pile préexistante préservée

Cette vérification doit être statique quand les branches sont écrites en Nicole.

Règles des guards :

- le guard est évalué avec les bindings produits par le pattern déjà en scope
- le guard doit avoir exactement l’effet de pile `-- Bool`
- le guard ne doit consommer aucune valeur de la pile locale préexistante
- le `Bool` produit par le guard est consommé immédiatement par la sélection de branche
- le guard doit être pur
- un guard ne peut pas appeler de code dirty
- `?` est interdit dans un guard
- un appel récursif direct situé dans un guard ne relève d’aucune garantie de pile constante

Patterns v1 retenus :

- littéraux `Int`
- littéraux `String`
- littéraux `Bool`
- `Ok(v)`
- `Err(e)`
- `MissingKey`
- `OutOfBounds`
- `_`

Règles de liaison :

- `Ok(v)` crée un binding local `v`
- `Err(e)` crée un binding local `e`
- `Err(MissingKey)` ne crée aucun binding local
- `Err(OutOfBounds)` ne crée aucun binding local
- `MissingKey` et `OutOfBounds` seuls ne créent aucun binding local
- `_` ne crée aucun binding local
- les bindings créés par le pattern sont visibles dans le guard éventuel, puis dans le corps de branche sélectionné

Pour les types somme fermés comme `Result`, `ListError` et `MapError`, l’exhaustivité doit être vérifiée statiquement quand le type du scrutinee est connu.

- une branche gardée ne compte pas comme couverture statique inconditionnelle
- `_ when guard` est autorisé, mais reste conditionnel et ne rend pas le `case` exhaustif à lui seul
- pour des valeurs ouvertes comme `Int` ou `String`, `_` est nécessaire si le programme veut garantir qu’aucune valeur non couverte ne provoquera d’échec de matching
- en l’absence de `_`, si aucune branche ne matche à l’exécution, cela relève d’une erreur de contrat d’exécution
- `Bool` peut être vérifié exhaustivement si les deux littéraux `true` et `false` sont couverts ; sinon, l’absence de `_` peut rester une erreur de contrat d’exécution

Pour les motifs imbriqués sur `Result` :

- `Err(MissingKey)` couvre uniquement le cas `Err` contenant exactement `MissingKey`
- `Err(e)` couvre tous les cas `Err`
- `Ok(v)` couvre tous les cas `Ok`
- pour `Result<V,MapError>`, si `MapError` ne contient que `MissingKey`, alors `Ok(v)` et `Err(MissingKey)` suffisent pour l’exhaustivité
- pour `Result<V,E>`, si `E` n’est pas couvert exhaustivement, il faut un motif plus général comme `Err(e)` ou `_`

Exemple de liaison :

```nicole
module @semantics.case
  : unwrap-result { r:Result<Int,MapError> -- n:Int }
    r case
      Ok(v) => v
      Err(e) => 0
    end
  ;
end-module
```

Exemple :

```nicole
module @semantics.case
  : sign-label { n:Int -- text:String }
    n case
      0 => "zero"
      1 => "one"
      _ => "many"
    end
  ;
end-module
```

Exemple avec guard :

```nicole
module @semantics.case
  : classify-result { r:Result<Int,MapError> -- text:String }
    r case
      Ok(v) when v 0 > => "positive"
      Ok(v) => "non-positive"
      Err(MissingKey) => "missing"
    end
  ;
end-module
```

---

# 6. Quotations et `call`

Une quotation est une valeur exécutable de première classe.
Elle se comporte comme un mot anonyme : elle a sa propre frame, une pile locale vide au départ, des variables locales immuables, et un retour exact conforme à sa signature.

Deux types de quotations existent en v1 :

- `Quote<{ captures | inputs -- outputs }>` pour une quotation pure
- `DirtyQuote<{ captures | inputs -- outputs }>` pour une quotation dirty

Elle peut :

- capturer des valeurs au moment de sa construction
- être stockée
- être passée à `list.map`, `list.filter`, `list.fold`, `list.reduce`
- être appelée plus tard avec `call`

Quand une quotation est passée à `list.map`, `list.filter`, `list.fold` ou `list.reduce`, le builtin consomme une quotation déjà construite.

Les captures sont donc déjà vérifiées au moment de la construction de cette quotation.

La compatibilité avec le builtin higher-order se fait ensuite sur la seule partie appelable `inputs -- outputs`.

## Captures

Les captures sont prises au moment de la construction de la quotation.
Elles sont capturées par valeur.
Elles deviennent des données internes immuables de la quotation.
Les captures ne sont pas prises au moment du `call`.

L’ordre des captures suit l’ordre de déclaration.

- la première capture déclarée correspond à la valeur la plus profonde du groupe capturé
- la dernière capture déclarée correspond à la valeur la plus proche du sommet au moment de la construction

## `call`

`call` consomme d’abord la quotation placée au sommet de la pile.
La quotation n'est pas un bloc qui réutilise la pile courante : les inputs ne deviennent des variables locales qu'au moment du `call`, dans la frame propre de la quotation.

Effet de `call` :

- `call` appliqué à `Quote<{ ... }>` reste pur
- `call` appliqué à `DirtyQuote<{ ... }>` est dirty

La convention de pile est :

```nicole
[... input1, input2, quote] call
```

La quotation est au sommet de pile.
Les inputs sont sous la quotation, dans l’ordre de la signature.

L’ordre est normatif :

- le dernier input déclaré dans la signature est la valeur la plus proche du sommet de pile, juste sous la quotation
- le premier input déclaré est la valeur la plus profonde parmi les inputs consommés par `call`

Exemple typé explicite :

Pour une quotation de type `Quote<{ | x:Int y:Int -- r:Int }>`,

`call` attend une pile de forme :

```nicole
[... x:Int, y:Int, quote] call
```

Précisions :

- la quotation est au sommet de pile
- `y` est la valeur immédiatement sous la quotation
- `x` est la valeur plus profonde
- les inputs sont consommés dans l’ordre de la signature

Ensuite, il consomme les inputs attendus par cette quotation depuis la pile courante, selon la même convention de lecture qu’un mot normal.

Enfin, il exécute le corps de la quotation dans sa propre frame et pousse ses outputs sur la pile courante.

La pile locale de la quotation reste distincte de la pile du caller pendant toute son exécution.

Le type-checker vérifie trois moments distincts :

1. à la construction de la quotation, les captures présentes sur la pile doivent correspondre aux captures déclarées ;
2. à l’appel par `call`, les inputs présents sous la quotation doivent correspondre aux inputs déclarés ;
3. au retour de la quotation, le corps doit produire exactement les outputs déclarés.

Vérifications d’effet :

- une quotation dont le corps appelle du code dirty est de type `DirtyQuote<{ ... }>`
- une quotation dont le corps n’appelle que du code pur est de type `Quote<{ ... }>`
- une frame pure ne peut pas construire de `DirtyQuote<{ ... }>`
- une frame pure ne peut pas appeler un `DirtyQuote<{ ... }>` via `call`
- une frame dirty peut construire et appeler les deux formes

La quotation suit la même discipline de retour qu’un mot normal :

- sorties exactes
- même ordre
- mêmes types

## Portée

Dans le corps d’une quotation :

- les captures sont accessibles en lecture seule
- les inputs du `call` sont accessibles en lecture seule
- aucune capture par référence implicite n’existe
- aucune mutation des captures n’existe
- si `?` apparaît dans le corps, la quotation doit elle-même déclarer exactement une seule sortie de type `Result<T,E>`
- dans une quotation, `?` quitte uniquement cette quotation

Les noms locaux doivent être uniques dans la frame de la quotation.

Une capture et un input de `call` ne peuvent donc pas partager le même nom dans une même quotation.

Une quotation peut toutefois réutiliser le nom d’un local du mot qui la construit, car il s’agit d’une autre frame.

Pour une quotation avec captures :

```nicole
:[ a:Int b:Int | x:Int -- y:Int | x a + b + ;]
```

les captures sont prises à la construction depuis une pile de forme :

```nicole
[... a:Int, b:Int]
```

`a` correspond à la valeur la plus profonde du groupe capturé et `b` à la valeur la plus proche du sommet.

Exemples conceptuels :

```nicole
3 :[ | x:Int -- y:Int | x 1 + ;] call
```

Résultat conceptuel :

- `4`

```nicole
3 4 :[ a:Int | x:Int -- y:Int | x a + ;] call
```

Résultat conceptuel :

- `7`

---

# 7. Collections et erreurs explicites

Le langage évite les erreurs implicites quand une erreur normale et attendue peut être représentée explicitement.

## `Result<V,E>`

`Result<V,E>` représente :

- `Ok(v)` pour un succès
- `Err(e)` pour un échec explicite

`case` est la manière normale d’inspecter un `Result`.

Dans `case`, les motifs de `Result` s’écrivent `Ok(v)` et `Err(e)`.

Hors `case`, la construction d’une valeur `Result` utilise les mots postfixes `Ok!` et `Err!`.

Sémantique de construction :

- `Ok!` a l’effet de pile `T -- Result<T,E>`
- `Ok!` consomme la valeur au sommet de pile et produit `Ok(value)`
- `Err!` a l’effet de pile `E -- Result<T,E>`
- `Err!` consomme la valeur d’erreur au sommet de pile et produit `Err(error)`
- `Ok(v)` et `Err(e)` ne sont pas des formes de construction par expression en v1

## Helpers retenus en v1

Les helpers suivants sont retenus :

- `result.is-ok`
- `result.is-err`
- `result.unwrap-or`

Sémantique :

- `result.is-ok` a l’effet de pile `Result<T,E> -- Bool`
- `result.is-ok` retourne `true` pour `Ok(_)` et `false` pour `Err(_)`
- `result.is-err` a l’effet de pile `Result<T,E> -- Bool`
- `result.is-err` retourne `true` pour `Err(_)` et `false` pour `Ok(_)`
- `result.unwrap-or` a l’effet de pile `Result<T,E> T -- T`
- `result.unwrap-or` retourne la valeur de `Ok(v)` dans le cas `Ok(v)`
- `result.unwrap-or` retourne la valeur de repli fournie dans le cas `Err(_)`

Ils restent ergonomiques.

Ils ne remplacent pas `case` pour l’inspection structurée.

## Propagation avec `?`

L’opérateur `?` agit sur une valeur de type `Result<V,E>`.

Son comportement est :

- `Ok(v) ?` pousse `v` et l’exécution continue dans la même frame
- `Err(e) ?` retourne immédiatement `Err(e)` depuis la frame courante

La portée de cette propagation est strictement locale :

- dans un mot, `?` quitte ce mot
- dans une quotation, `?` quitte cette quotation
- `?` ne traverse jamais implicitement une frame parente
- `?` ne provoque jamais de sortie implicite spéciale de `list.map`, `list.fold` ou `list.reduce`

Le type-checker doit rejeter toute frame contenant `?` si cette frame ne déclare pas exactement une seule sortie, de type `Result<T,E>`.

Une frame qui annonce plusieurs sorties, aucune sortie, ou une sortie simple non `Result` doit être rejetée si son corps contient `?`.

Le type d’erreur produit par la valeur consommée par `?` doit correspondre exactement au type d’erreur `E` de la sortie de frame.

Il n’existe en v1 ni élargissement implicite, ni conversion implicite entre types d’erreur.

Interaction avec la garantie v0.16 d’appel récursif direct en position terminale :

- les règles de `?` restent inchangées
- `?` reste interdit dans un guard de `case`
- un appel récursif direct suivi d’une opération `?` n’est pas en position terminale
- un `?` exécuté avant un appel peut terminer la frame avant que cet appel ne soit atteint

## Interaction avec les builtins d’ordre supérieur

Quand une quotation passée à `list.map` retourne `Result<U,E>`, le résultat est `List<Result<U,E>>`.

Ce n’est pas `Result<List<U>,E>`.

Le même principe de non-propagation implicite s’applique à `list.filter`, `list.fold` et `list.reduce`.

Ces builtins consomment une quotation déjà construite.

Ils n’introduisent aucune propagation spéciale qui traverserait la frame de cette quotation.

Les builtins d’ordre supérieur restent structurellement purs en v1.

Leur effet au point d’appel dépend du type de quotation fourni :

- avec `Quote<{ ... }>` : l’appel reste pur
- avec `DirtyQuote<{ ... }>` : l’appel est dirty

Une frame pure ne peut pas passer un `DirtyQuote<{ ... }>` à `list.map`, `list.filter`, `list.fold` ni `list.reduce`.

## Builtins de liste structurels v1

Les builtins de liste suivants sont purement structurels :

- `list.len` a l’effet `List<T> -- Int`
- `list.is-empty` a l’effet `List<T> -- Bool`
- `list.get` a l’effet `List<T> Int -- Result<T,ListError>`
- `list.first` a l’effet `List<T> -- Result<T,ListError>`
- `list.last` a l’effet `List<T> -- Result<T,ListError>`
- `list.set` a l’effet `List<T> Int T -- Result<List<T>,ListError>`
- `list.append` a l’effet `List<T> T -- List<T>`
- `list.concat` a l’effet `List<T> List<T> -- List<T>`
- `list.reverse` a l’effet `List<T> -- List<T>`

Sémantique :

- `list.is-empty` retourne `true` pour une liste vide et `false` sinon
- `list.first` retourne `Ok(first)` pour une liste non vide, sinon `Err(OutOfBounds)`
- `list.last` retourne `Ok(last)` pour une liste non vide, sinon `Err(OutOfBounds)`
- un index négatif passé à `list.get` ou `list.set` est hors limites et retourne `Err(OutOfBounds)`
- `list.append` retourne une nouvelle liste avec l’élément ajouté en fin
- `list.concat` retourne une nouvelle liste contenant d’abord les éléments de gauche puis ceux de droite
- `list.reverse` retourne une nouvelle liste avec l’ordre inversé
- ces builtins n’exécutent aucune quotation
- ces builtins restent purs en v1

## `list.map`

`list.map` préserve l’ordre des éléments.

Son parcours conceptuel est de gauche à droite.

Sur une liste vide, il retourne une liste vide.

## `list.filter`

`list.filter` consomme une quotation compatible avec `x:T -- keep:Bool`.

Il préserve l’ordre relatif des éléments retenus.

Son parcours conceptuel est de gauche à droite.

Sur une liste vide, il retourne une liste vide.

La quotation de `list.filter` doit retourner `Bool`.

Si une quotation retourne `Result<Bool,E>`, cela ne devient pas un comportement spécial de `list.filter` en v1.

## `list.fold`

`list.fold` consomme une quotation compatible avec `acc:Acc x:T -- out:Acc`.

L’accumulateur courant est le premier input de la quotation.

L’élément courant est le second input de la quotation.

Son parcours conceptuel est de gauche à droite.

Sur une liste vide, il retourne l’accumulateur initial fourni à l’appel.

Toute opération future qui court-circuite explicitement sur `Result` devra être distincte.

## Différé

Les éléments suivants restent hors de cette phase :

- `result.unwrap`
- `result.map`
- `result.map-err`
- `result.and-then`
- `result.match`
- `list.try-map`
- `list.try-filter`
- `list.try-fold`

Exemple :

```nicole
module @semantics.result
  : timeout-or-default { cfg:Map<String,Int> -- n:Int }
    cfg "timeout" map.get case
      Ok(v) => v
      Err(MissingKey) => 30
    end
  ;
end-module
```

## `ListError`

`ListError` sert aux erreurs normales des opérations de liste.

V1 retient :

- `OutOfBounds`

Utilisation attendue :

- `list.get`
- `list.set`
- `list.first`
- `list.last`

## `MapError`

`MapError` sert aux erreurs normales des opérations de map.

V1 retient :

- `MissingKey`

Utilisation attendue :

- `map.get`
- `map.remove`

## Sémantique des maps v1

Les maps sont immuables en v1.

- `map.empty:Map<K,V>` construit une map vide explicitement typée
- `map.empty` non annoté doit être rejeté
- `map.get` a l’effet `Map<K,V> K -- Result<V,MapError>`
- `map.get` retourne `Ok(value)` si la clé existe et `Err(MissingKey)` sinon
- `map.contains` a l’effet `Map<K,V> K -- Bool`
- `map.contains` retourne `true` si la clé existe et `false` sinon
- `map.set` a l’effet `Map<K,V> K V -- Map<K,V>`
- `map.set` retourne une nouvelle map avec insertion ou remplacement de la valeur
- `map.set` ne mute jamais la map d’entrée
- `map.remove` a l’effet `Map<K,V> K -- Result<Map<K,V>,MapError>`
- `map.remove` retourne `Ok(newMap)` si la clé existe et `Err(MissingKey)` sinon
- `map.remove` ne mute jamais la map d’entrée
- `map.len` a l’effet `Map<K,V> -- Int`
- `map.len` retourne le nombre d’entrées
- `map.is-empty` a l’effet `Map<K,V> -- Bool`
- `map.is-empty` retourne `true` si la map est vide et `false` sinon
- `map.keys` a l’effet `Map<K,V> -- List<K>`
- `map.values` a l’effet `Map<K,V> -- List<V>`
- seules les clés `Int`, `String` et `Bool` sont définies en v1
- les types de clé définis par l’utilisateur ne sont pas supportés en v1
- les maps préservent l’ordre d’insertion des clés
- `map.keys` retourne les clés dans cet ordre d’insertion
- `map.values` retourne les valeurs dans le même ordre que `map.keys`
- `map.set` sur une clé existante met à jour la valeur sans déplacer cette clé
- `map.remove` retire aussi la clé de cet ordre
- un `map.set` effectué après suppression réinsère la clé en fin d’ordre
- ces builtins de map n’exécutent aucune quotation
- ces builtins restent purs en v1

Éléments différés :

- types de clé définis par l’utilisateur
- support des handles hôte comme clés
- `Keyable`
- `Hashable`
- `map.has`
- `map.to-list`
- `map.entries`
- `map.items`
- `map.map`
- `map.filter`
- `map.fold`

## Constructions vides typées

En v1, les constructions vides ne reposent pas sur une déduction implicite depuis le contexte.

- `[]:List<T>` est une liste vide typée explicitement
- `map.empty:Map<K,V>` est une map vide typée explicitement
- `[]` non annoté doit être rejeté
- `map.empty` non annoté doit être rejeté

## `list.reduce`

`list.reduce` est défini uniquement sur une liste non vide.

- le premier élément sert d’accumulateur implicite initial
- le parcours conceptuel est de gauche à droite
- si la liste vide est prouvable statiquement, l’appel doit être rejeté à la compilation
- si la liste vide n’est découverte qu’à l’exécution, c’est une erreur de contrat d’exécution
- ce n’est pas un `Err(...)` parce que `list.reduce` ne retourne pas un `Result` en v1

## Absence d’exceptions implicites

Les cas normaux d’échec doivent être représentés par `Result`.

Les exceptions implicites ne font pas partie du modèle sémantique v1.

---

# 8. Frontière compile-time / runtime

Le langage sépare ce qui doit être rejeté à la compilation de ce qui peut encore relever d’une erreur d’exécution.

## Contrat d’exécution

Une erreur de contrat d’exécution est une violation d’un contrat supposé valide, détectée lorsque l’environnement d’exécution ne peut pas satisfaire l’attente exprimée par le programme ou par une primitive fournie par intégration.

Elle ne concerne pas les mots Nicole normaux.

Elle concerne surtout :

- les mots hôte `host.*`
- les primitives fournies par intégration
- certains cas runtime explicitement dépendants de valeurs observées, comme `list.reduce` sur une liste vide non prouvable statiquement

Ce n’est pas un `Result`.
Ce n’est pas une exception implicite métier.

## Doit être rejeté à la compilation quand c’est prouvable

- collision de noms visibles dans un même espace de résolution
- incompatibilité de types d’entrée
- liste vide sans annotation de type explicite
- map vide sans annotation de type explicite
- branches de `if` ou `case` qui n’ont pas le même effet de pile
- retour qui ne peut pas satisfaire la signature
- capture non typée dans une quotation
- capture incompatible avec le type annoncé

## Peut rester une erreur d’exécution

- appel d’un mot hôte absent de l’environnement d’exécution
- `list.reduce` sur une liste vide si ce vide n’est pas prouvable statiquement
- autres cas où le type-checker ne peut pas décider, mais où le contrat d’exécution est violé

Exemple :

```nicole
module @semantics.collections
  : reduce-safely { xs:List<Int> -- n:Int }
    xs :[ | a:Int b:Int -- c:Int | a b + ;] list.reduce
  ;
end-module
```

Si `xs` est prouvée vide à la compilation, l’appel doit être rejeté.
Sinon, une liste vide observée à l’exécution constitue une erreur d’utilisation.
Cette situation constitue une erreur de contrat d’exécution.

---

# 9. Contrat hôte

Deux directions officielles existent :

- `export` : déclaration module-locale exposant un mot du programme à l’hôte
- `host.*` : mot fourni par l’hôte et appelable depuis le programme

## `export`

`export : word` publie vers l’hôte un mot déjà défini dans le module courant.

Règles :

- `export : word` est une déclaration uniquement
- la déclaration est valide uniquement dans le module qui définit `word`
- `word` doit exister dans ce même module
- `export` ne définit pas de nouveau mot et ne crée pas d’alias Nicole
- `export` ne modifie ni typage, ni effet, ni récursion du mot référencé
- `pub` règle la visibilité Nicole, `export` règle la visibilité hôte
- `export` ne dépend jamais des imports ni des aliases
- le nom canonique visible hôte est `@module.word` (avec `@` conservé)
- ce nom canonique est dérivé du module définissant et du mot référencé
- les aliases d’import n’affectent jamais ce nom canonique
- les noms canoniques visibles hôte doivent rester uniques dans le programme
- une déclaration `export` dupliquée qui produit le même nom canonique est invalide

Exemple :

```nicole
module @app
  dirty : on-message { msg:String -- }
    msg host.log
  ;
  export : on-message
end-module
```

## `host.*`

`host.*` désigne des mots fournis par l’hôte.

Le programme peut les appeler, mais ne peut pas les définir.

Exemple :

```nicole
module @abi.host_usage
  dirty : save-log { msg:String -- }
    msg host.log
  ;
end-module
```

Règles :

- un programme utilisateur ne peut pas définir un mot `host.*`
- si un mot `host.*` est absent alors que le contrat hôte est connu statiquement, c’est une erreur d’intégration détectable avant exécution
- si l’environnement hôte est dynamique et que le binding disparaît ou manque à l’exécution, c’est une erreur d’intégration à l’exécution
- dans les deux cas, l’absence du mot est une erreur de contrat d’exécution observée à la frontière hôte
- `Result` ne s’applique qu’au contrat de retour d’un mot `host.*` qui existe effectivement
- le mécanisme de liaison lui-même n’est jamais modélisé comme un `Result`
- la résolution statique traite `host.*` comme des mots connus, avec signatures connues et noms visibles uniques
- l’effet (`pure`/`dirty`) d’un mot `host.*` est défini par `HOST_ABI.md`
- le code Nicole source ne déclare jamais l’effet d’un mot `host.*` par une définition locale

`host.file.open` n’est pas un mot de v1.
S’il est documenté plus tard, ce sera comme extension future du contrat hôte.

---

# 10. Règle de fond

La sémantique doit rester :

- explicite
- statique quand c’est possible
- compatible avec des frames isolées
- compatible avec des erreurs explicites
- sans capture lexicale implicite
- sans mutation des variables locales

Le but de ce fichier est de définir le comportement du langage, pas de rouvrir la conception de la syntaxe.

---

# Points ouverts

## Nom identique entre sous-mots dans un même parent

En phase 2, le conflit sous-mot vs mot utilisateur top-level n’est plus applicable car les mots utilisateur top-level sont interdits.

La contrainte locale reste normative :

La règle suivante reste également normative :

- dans un même parent, deux sous-mots ne peuvent pas partager le même nom
