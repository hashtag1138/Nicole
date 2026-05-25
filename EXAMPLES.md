# EXAMPLES.md

# Exemples de programme pour Nicole

Ce document illustre la manière d’écrire des programmes en Nicole.

Il ne redéfinit pas le langage.

Les seules sources normatives sont :

- `SYNTAXE.md`
- `SEMANTIQUE.md`
- `HOST_ABI.md`

Les exemples ci-dessous servent à lire le langage, à apprendre sa forme idiomatique, et à préparer plus tard des tests de conformité.

---

## 1. Mots simples

### Addition simple

```nicole
module @examples_basics_01
  : add-one { x:Int -- y:Int }
    x 1 +
  ;
end-module
```

Explication :
- lit `x`
- pousse `1`
- applique `+`

Effet de pile :
- entrée `3`
- sortie `4`

Pourquoi :
- forme minimale claire pour illustrer les variables locales

### Carré d’un entier

```nicole
module @examples_basics_02
  : square { x:Int -- y:Int }
    x x *
  ;
end-module
```

Explication :
- lit `x` deux fois
- applique `*`

Effet de pile :
- entrée `4`
- sortie `16`

Pourquoi :
- montre une réutilisation simple d’une variable locale

### Chaînes simples

```nicole
module @examples_basics_03
  : greet { excited:Bool -- msg:String }
    excited case
      true => "hello"
      false => "hi"
    end
  ;
end-module
```

Explication :
- choisit une chaîne littérale selon un booléen

Effet de pile :
- entrée `true`
- sortie `"hello"`

Pourquoi :
- illustre un `case` simple qui retourne une chaîne littérale

---

## 2. Variables locales

### Réutilisation d’un input

```nicole
module @examples_locals_01
  : double { x:Int -- y:Int }
    x x +
  ;
end-module
```

Explication :
- lit la variable locale `x`
- la réutilise sans mutation

Effet de pile :
- entrée `5`
- sortie `10`

Pourquoi :
- montre que les variables locales sont lues, pas modifiées

### Valeur de départ et calcul

```nicole
module @examples_locals_02
  : add-five { x:Int -- y:Int }
    x 5 +
  ;
end-module
```

Explication :
- lit `x`
- ajoute `5`

Effet de pile :
- entrée `7`
- sortie `12`

Pourquoi :
- exemple simple pour relire la règle “la lecture pousse la valeur locale”

---

## 3. Sous-mots privés

### Sous-mot local explicite

```nicole
module @examples_subwords_01
  : invoice { price:Int qty:Int -- total:Int }

    : subtotal { price:Int qty:Int -- amount:Int }
      price qty *
    ;

    price qty subtotal
  ;
end-module
```

Explication :
- `subtotal` est local au mot parent
- les valeurs nécessaires sont passées explicitement
- le sous-mot ne capture pas les variables du parent

Effet de pile :
- entrée `12 3`
- sortie `36`

Pourquoi :
- montre la visibilité limitée d’un sous-mot privé

### Réutilisation d’un nom local dans une autre frame

```nicole
module @examples_subwords_02
  : foo { x:Int -- y:Int }

    : bar { x:Int -- y:Int }
      1 x +
    ;

    3 bar
    x
    +
  ;
end-module
```

Explication :
- `foo.x` et `bar.x` sont deux locals distincts
- `bar` ne capture pas `foo.x`
- le même nom peut être réutilisé dans une autre frame

Effet de pile :
- entrée `10`
- sortie `14`

Pourquoi :
- montre que l’unicité des noms locaux est une règle par frame, pas globale au programme

---

## 4. Noms explicites et récursion mutuelle

### Noms explicites

```nicole
module @examples_naming_01
  : id-int { x:Int -- y:Int }
    x
  ;

  : id-string { x:String -- y:String }
    x
  ;
end-module
```

Explication :
- chaque nom visible désigne une seule définition
- des comportements voisins doivent utiliser des noms distincts

Utilisation :
- `42 id-int` retourne `42`
- `"hello" id-string` retourne `"hello"`

Pourquoi :
- montre la forme recommandée en Nicole v1 avec des noms explicites

### Récursion directe en position terminale (accumulateur)

```nicole
module @examples_naming_02
  : sum-down-acc { n:Int acc:Int -- result:Int }
    n 0 = if
      acc
    else
      n 1 - acc n + sum-down-acc
    end
  ;
end-module
```

Note :
- Cet exemple reçoit la garantie v0.16 de pile d'appels Nicole constante, car l'appel récursif est un appel récursif direct en position terminale.

### Récursion non terminale

```nicole
module @examples_naming_03
  : fact { n:Int -- result:Int }
    n case
      0 => 1
      _ => n n 1 - fact *
    end
  ;
end-module
```

Note :
- Cet exemple reste valide, mais l'appel récursif n'est pas en position terminale, car la multiplication reste à effectuer après le retour de l'appel récursif. Il ne reçoit donc aucune garantie v0.16 de pile constante.

### Récursion mutuelle

```nicole
module @examples_naming_04
  : even { n:Int -- result:Bool }
    n 0 = if
      true
    else
      n 1 - odd
    end
  ;

  : odd { n:Int -- result:Bool }
    n 0 = if
      false
    else
      n 1 - even
    end
  ;
end-module
```

Explication :
- `even` et `odd` ont chacun un nom distinct
- la collecte préalable des signatures permet leurs appels réciproques

Utilisation :
- `0 even` retourne `true`
- `1 odd` retourne `true`

Pourquoi :
- montre que la récursion mutuelle reste naturelle avec des noms distincts

Note :
- Cette récursion mutuelle reste valide, mais la v0.16 ne garantit pas une utilisation à pile d'appels Nicole constante pour la récursion mutuelle.

---

## 5. Retours multiples

### Paire de sortie

```nicole
module @examples_returns_01
  : pair { -- a:Int b:String }
    1 "ok"
  ;
end-module
```

Explication :
- produit deux valeurs
- d’abord `1`
- puis `"ok"`

Effet de pile :
- sortie `[..., 1, "ok"]`

Pourquoi :
- montre l’ordre des sorties dans la signature

### Deux entiers

```nicole
module @examples_returns_02
  : dimensions { -- width:Int height:Int }
    800 600
  ;
end-module
```

Explication :
- produit deux entiers de manière explicite

Effet de pile :
- sortie `[..., 800, 600]`

Pourquoi :
- montre un retour multiple lisible et direct

---

## 6. `if`

### Valeur absolue

```nicole
module @examples_if_01
  : abs { x:Int -- y:Int }
    x 0 < if
      0 x -
    else
      x
    end
  ;
end-module
```

Explication :
- teste si `x` est négatif
- choisit une branche ou l’autre

Effet de pile :
- entrée `-7`
- sortie `7`

Pourquoi :
- montre un `if` idiomatique et clair

### Booléen simple

```nicole
module @examples_if_02
  : choose-yes { flag:Bool -- text:String }
    flag if
      "yes"
    else
      "no"
    end
  ;
end-module
```

Explication :
- consomme un booléen
- produit un texte selon la branche

Effet de pile :
- entrée `true`
- sortie `"yes"`

Pourquoi :
- montre la forme minimale d’un `if`

---

## 7. `case`

### `Result` avec valeur par défaut

```nicole
module @examples_case_01
  : timeout-or-default { cfg:Map<String,Int> -- n:Int }
    cfg "timeout" map.get case
      Ok(v) => v
      Err(MissingKey) => 30
    end
  ;
end-module
```

Explication :
- lit un entier dans une map
- retourne `30` si la clé manque

Effet de pile :
- clé présente : valeur lue
- clé absente : `30`

Pourquoi :
- montre un `case` idiomatique sur `Result`

### Helpers `Result`

```nicole
module @examples_case_02
  : has-timeout-result { cfg:Map<String,Int> -- b:Bool }
    cfg "timeout" map.get result.is-ok
  ;

  : timeout-or-30 { cfg:Map<String,Int> -- n:Int }
    cfg "timeout" map.get 30 result.unwrap-or
  ;
end-module
```

Explication :
- `result.is-ok` teste la forme du `Result`
- `result.unwrap-or` fournit une valeur de repli explicite

Effet de pile :
- `has-timeout-result` retourne `true` si la clé est présente
- `timeout-or-30` retourne la valeur lue ou `30`

Pourquoi :
- montre les helpers ergonomiques retenus sans remplacer `case`

### Propagation locale avec `?`

```nicole
module @examples_case_03
  : require-timeout-flag { cfg:Map<String,Int> -- r:Result<Int,MapError> }
    cfg "timeout" map.get ?
    drop
    1 Ok!
  ;
end-module
```

Explication :
- `map.get` peut retourner `Err(MissingKey)`
- `?` quitte immédiatement le mot dans ce cas
- si la lecture réussit, le mot continue dans la même frame
- la valeur lue est ignorée explicitement avec `drop`, puis le mot retourne `1 Ok!`

Effet de pile :
- clé présente : sortie `Ok(1)`
- clé absente : sortie `Err(MissingKey)`

Pourquoi :
- montre que `?` propage localement sans exception implicite
- montre qu’un mot contenant `?` doit déjà retourner un `Result`

### `Bool` exhaustif

```nicole
module @examples_case_04
  : bool-label { b:Bool -- text:String }
    b case
      true => "true"
      false => "false"
    end
  ;
end-module
```

Explication :
- distingue les deux cas possibles

Effet de pile :
- entrée `true`
- sortie `"true"`

Pourquoi :
- montre un `case` exhaustif sur `Bool`

---

## 8. Collections

Note pédagogique :
- `[]:List<T>` est une liste vide typée explicitement
- `map.empty:Map<K,V>` est une construction vide typée explicitement
- dans les deux cas, Nicole v1 privilégie la clarté locale plutôt qu’une déduction implicite du type

### Carte avec timeout

```nicole
module @examples_collections_01
  : cfg-with-timeout { -- cfg:Map<String,Int> }
    map.empty:Map<String,Int>
    "timeout" 30 map.set
  ;
end-module
```

Explication :
- construit une carte vide
- ajoute une clé `"timeout"`
- `map.set` retourne une nouvelle carte

Pourquoi :
- montre l’immuabilité des maps

### Présence d’une clé

```nicole
module @examples_collections_02
  : has-timeout { cfg:Map<String,Int> -- ok:Bool }
    cfg "timeout" map.contains
  ;
end-module
```

Explication :
- teste la présence d’une clé

Effet de pile :
- entrée une carte
- sortie `true` ou `false`

Pourquoi :
- montre une vérification simple et lisible

### Présence d’un utilisateur

```nicole
module @examples_collections_03
  : has-user { users:Map<String,Int> -- b:Bool }
    users "alice" map.contains
  ;
end-module
```

Explication :
- teste la présence d’une clé précise

Pourquoi :
- montre `map.contains` sur un cas simple

### Ajout ou remplacement dans une map

```nicole
module @examples_collections_04
  : add-user { users:Map<String,Int> -- out:Map<String,Int> }
    users "alice" 42 map.set
  ;
end-module
```

Explication :
- renvoie une nouvelle map avec la valeur associée à `"alice"`
- la map d’entrée n’est jamais mutée sur place

Pourquoi :
- montre directement l’immuabilité de `map.set`

### Suppression explicite dans une map

```nicole
module @examples_collections_05
  : remove-user
  {
    users:Map<String,Int>
    --
    r:Result<Map<String,Int>,MapError>
  }
    users "alice" map.remove
  ;
end-module
```

Explication :
- renvoie `Ok(newMap)` si la clé existe
- renvoie `Err(MissingKey)` si la clé est absente

Pourquoi :
- montre que `map.remove` ne supprime jamais silencieusement une clé absente

### Nombre d’entrées d’une map

```nicole
module @examples_collections_06
  : user-count { users:Map<String,Int> -- n:Int }
    users map.len
  ;
end-module
```

Explication :
- retourne le nombre d’entrées de la map

Pourquoi :
- montre la primitive d’observation minimale conservée en v1

### Test de vacuité d’une map

```nicole
module @examples_collections_07
  : has-no-user { users:Map<String,Int> -- b:Bool }
    users map.is-empty
  ;
end-module
```

Explication :
- retourne `true` si la map est vide
- retourne `false` si elle contient au moins une entrée

Pourquoi :
- montre `map.is-empty` comme observation simple

### Clés d’une map dans l’ordre d’insertion

```nicole
module @examples_collections_08
  : user-keys { -- xs:List<String> }
    map.empty:Map<String,Int>
    "alice" 1 map.set
    "bob" 2 map.set
    map.keys
  ;
end-module
```

Explication :
- `map.keys` renvoie les clés dans l’ordre d’insertion

Pourquoi :
- rend l’ordre d’insertion observable explicitement

### Valeurs d’une map dans l’ordre des clés

```nicole
module @examples_collections_09
  : user-values { -- xs:List<Int> }
    map.empty:Map<String,Int>
    "alice" 1 map.set
    "bob" 2 map.set
    map.values
  ;
end-module
```

Explication :
- `map.values` suit le même ordre que `map.keys`

Pourquoi :
- rend la correspondance ordre-clés/ordre-valeurs explicite

### Mise à jour sans déplacer la clé

```nicole
module @examples_collections_10
  : keys-after-update { -- xs:List<String> }
    map.empty:Map<String,Int>
    "a" 1 map.set
    "b" 2 map.set
    "a" 9 map.set
    map.keys
  ;
end-module
```

Explication :
- une mise à jour de clé existante change la valeur
- la position initiale de la clé est conservée

Pourquoi :
- fixe le comportement d’ordre pour `map.set` sur clé existante

### Suppression puis réinsertion en fin d’ordre

```nicole
module @examples_collections_11
  : keys-after-remove-set { -- xs:List<String> }
    map.empty:Map<String,Int>
    "a" 1 map.set
    "b" 2 map.set
    "c" 3 map.set
    "b" map.remove case
      Ok(m2) => m2
      Err(MissingKey) => map.empty:Map<String,Int>
    end
    "b" 22 map.set
    map.keys
  ;
end-module
```

Explication :
- `map.remove` enlève la clé de l’ordre
- une réinsertion ultérieure place la clé en fin d’ordre

Pourquoi :
- illustre la règle `remove` puis `set`

### Test de vacuité d’une liste

```nicole
module @examples_collections_12
  : has-no-value { xs:List<Int> -- b:Bool }
    xs list.is-empty
  ;
end-module
```

Explication :
- retourne `true` si la liste est vide
- retourne `false` sinon

Pourquoi :
- montre `list.is-empty` de manière directe

### Lecture dans une liste

```nicole
module @examples_collections_13
  : first { xs:List<Int> -- n:Int }
    xs 0 list.get case
      Ok(v) => v
      Err(OutOfBounds) => 0
    end
  ;
end-module
```

Explication :
- lit le premier élément si possible
- retourne `0` sinon

Effet de pile :
- entrée `[10, 20]`
- sortie `10`

Pourquoi :
- montre un accès de liste avec erreur explicite

### Premier élément avec erreur explicite

```nicole
module @examples_collections_14
  : first-or-zero-v2 { xs:List<Int> -- n:Int }
    xs list.first case
      Ok(v) => v
      Err(OutOfBounds) => 0
    end
  ;
end-module
```

Explication :
- `list.first` retourne un `Result`
- une liste vide produit `Err(OutOfBounds)`

Pourquoi :
- montre la forme idiomatique de `list.first`

### Dernier élément avec erreur explicite

```nicole
module @examples_collections_15
  : last-or-zero { xs:List<Int> -- n:Int }
    xs list.last case
      Ok(v) => v
      Err(OutOfBounds) => 0
    end
  ;
end-module
```

Explication :
- `list.last` retourne un `Result`
- une liste vide produit `Err(OutOfBounds)`

Pourquoi :
- montre la forme idiomatique de `list.last`

### Ajout en fin de liste

```nicole
module @examples_collections_16
  : append-42 { xs:List<Int> -- ys:List<Int> }
    xs 42 list.append
  ;
end-module
```

Explication :
- renvoie une nouvelle liste avec `42` ajouté en fin

Pourquoi :
- rend explicite l’opération d’ajout immuable

### Inversion d’une liste

```nicole
module @examples_collections_17
  : reversed { xs:List<Int> -- ys:List<Int> }
    xs list.reverse
  ;
end-module
```

Explication :
- renvoie une nouvelle liste dans l’ordre inverse

Pourquoi :
- documente `list.reverse` sans ambiguïté

### Transformation avec `list.map`

```nicole
module @examples_collections_18
  : inc-all { xs:List<Int> -- ys:List<Int> }
    xs :[ | x:Int -- y:Int | x 1 + ;] list.map
  ;
end-module
```

Explication :
- applique `x 1 +` à chaque élément

Effet de pile :
- entrée `[1, 2, 3]`
- sortie `[2, 3, 4]`

Pourquoi :
- exemple direct de transformation de liste

### Transformation avec `list.map` et capture explicite

```nicole
module @examples_collections_19
  : add-offset-all { xs:List<Int> offset:Int -- ys:List<Int> }
    xs
    offset
    :[ captured-offset:Int | x:Int -- y:Int |
      x captured-offset +
    ;]
    list.map
  ;
end-module
```

Explication :
- `offset` du mot parent est lu explicitement
- sa valeur est capturée dans la quotation
- `list.map` reçoit une quotation déjà construite
- la partie appelable pertinente pour `list.map` reste `x:Int -- y:Int`

Effet de pile :
- entrée `[1, 2, 3] 10`
- sortie `[11, 12, 13]`

Pourquoi :
- montre qu’une quotation capturante reste compatible avec `list.map`

### Transformation avec `list.map` et quotation retournant `Result`

```nicole
module @examples_collections_20
  : mark-timeouts { cfgs:List<Map<String,Int>> -- ys:List<Result<Int,MapError>> }
    cfgs
    :[ | cfg:Map<String,Int> -- r:Result<Int,MapError> |
      cfg "timeout" map.get ?
      drop
      1 Ok!
    ;]
    list.map
  ;
end-module
```

Explication :
- la quotation retourne elle-même un `Result`
- `?` ne quitte que la frame de la quotation courante
- `list.map` collecte donc une liste de `Result`

Effet de pile :
- entrée `[cfg1, cfg2]`
- sortie du genre `[Ok(1), Err(MissingKey)]`

Pourquoi :
- montre que `list.map` ne court-circuite pas implicitement sur `Result`
- montre la forme `List<Result<...>>` retenue en v1

### Filtrage avec `list.filter`

```nicole
module @examples_collections_21
  : keep-positive { xs:List<Int> -- ys:List<Int> }
    xs :[ | x:Int -- keep:Bool | x 0 > ;] list.filter
  ;
end-module
```

Explication :
- conserve uniquement les éléments pour lesquels la quotation retourne `true`
- l’ordre relatif des éléments conservés est préservé

Effet de pile :
- entrée `[-2, 3, 0, 5]`
- sortie `[3, 5]`

Pourquoi :
- montre la forme de base de `list.filter`

### Réduction simple

```nicole
module @examples_collections_22
  : sum { xs:List<Int> -- n:Int }
    xs 0 :[ | acc:Int x:Int -- out:Int | acc x + ;] list.fold
  ;
end-module
```

Explication :
- additionne tous les éléments
- part d’un accumulateur initial `0`

Effet de pile :
- entrée `[1, 2, 3]`
- sortie `6`

Pourquoi :
- montre un usage simple et lisible de `list.fold`

### Réduction sur liste vide avec accumulateur initial

```nicole
module @examples_collections_23
  : sum-or-zero { xs:List<Int> -- n:Int }
    xs 0 :[ | acc:Int x:Int -- out:Int | acc x + ;] list.fold
  ;
end-module
```

Explication :
- `list.fold` retourne l’accumulateur initial si la liste est vide
- la quotation n’est appliquée que sur les éléments présents

Effet de pile :
- entrée `[]:List<Int>`
- sortie `0`

Pourquoi :
- rend explicite le comportement de `list.fold` sur liste vide

### Réduction avec `list.fold` et capture explicite

```nicole
module @examples_collections_24
  : sum-with-offset { xs:List<Int> offset:Int -- n:Int }
    xs
    0
    offset
    :[ captured-offset:Int | acc:Int x:Int -- out:Int |
      acc x + captured-offset +
    ;]
    list.fold
  ;
end-module
```

Explication :
- la quotation capture explicitement `offset`
- `list.fold` utilise ensuite uniquement sa partie appelable
- l’accumulateur et l’élément courant restent les deux inputs de la réduction

Effet de pile :
- entrée `[1, 2, 3] 10`
- sortie `36`

Pourquoi :
- montre qu’une quotation capturante reste compatible avec `list.fold`

### Réduction sans valeur initiale

```nicole
module @examples_collections_25
  : sum-non-empty { xs:List<Int> -- n:Int }
    xs :[ | a:Int b:Int -- c:Int | a b + ;] list.reduce
  ;
end-module
```

Explication :
- réduit une liste non vide en additionnant les éléments
- le premier élément devient l’accumulateur implicite initial
- le parcours conceptuel est de gauche à droite

Effet de pile :
- entrée `[1, 2, 3]`
- sortie `6`

Pourquoi :
- montre la forme idiomatique de `list.reduce`

---

## 9. Quotations

### Quotation simple

```nicole
module @examples_quotes_01
  : plus-one { x:Int -- y:Int }
    x :[ | n:Int -- m:Int | n 1 + ;] call
  ;
end-module
```

Explication :
- construit une quotation
- l’appelle immédiatement

Effet de pile :
- entrée `4`
- sortie `5`

Pourquoi :
- montre le cycle complet quotation + `call`

### Quotations avec capture

```nicole
module @examples_quotes_02
  : add-captured { x:Int y:Int -- z:Int }
    x y :[ a:Int | n:Int -- m:Int | n a + ;] call
  ;
end-module
```

Explication :
- `y` est capturé comme `a`
- `x` reste sous la quotation et devient l’input `n` au moment du `call`
- entrée `3 4` produit `7`

Effet de pile :
- entrée `3 4`
- sortie `7`

Pourquoi :
- montre la capture par valeur de manière lisible

### Ordre des captures

```nicole
module @examples_quotes_03
  : capture-order { -- n:Int }
    2 3 :[ a:Int b:Int | -- r:Int | a b - ;] call
  ;
end-module
```

Explication :
- `a` capture la valeur la plus profonde du groupe capturé
- `b` capture la valeur la plus proche du sommet au moment de la construction
- ici `a=2` et `b=3`

Effet de pile :
- entrée aucune
- sortie `-1`

Pourquoi :
- rend explicite l’ordre de capture dans `:[ a:Int b:Int | ... ;]`

### Ordre des inputs de `call`

```nicole
module @examples_quotes_04
  : call-order { -- n:Int }
    2 3 :[ | x:Int y:Int -- r:Int | x y - ;] call
  ;
end-module
```

Explication :
- la quotation est au sommet de pile juste avant `call`
- `y` est la valeur immédiatement sous la quotation
- `x` est la valeur plus profonde parmi les inputs

Effet de pile :
- entrée aucune
- sortie `-1`

Pourquoi :
- rend explicite la convention `x y quote call`

### Quotation avec propagation locale

```nicole
module @examples_quotes_05
  : call-timeout-check { cfg:Map<String,Int> -- r:Result<Int,MapError> }
    cfg
    :[ | current:Map<String,Int> -- r:Result<Int,MapError> |
      current "timeout" map.get ?
      drop
      1 Ok!
    ;]
    call
  ;
end-module
```

Explication :
- `?` agit dans la frame de la quotation
- en cas d’échec, la quotation retourne immédiatement `Err(MissingKey)`
- `call` restitue simplement ce `Result` au mot appelant

Effet de pile :
- clé présente : sortie `Ok(1)`
- clé absente : sortie `Err(MissingKey)`

Pourquoi :
- montre que `?` ne traverse pas implicitement les frames parentes

### Quotation avec réutilisation d’un nom dans une autre frame

```nicole
module @examples_quotes_06
  : add-offset { x:Int offset:Int -- y:Int }
    x
    offset
    :[ offset:Int | value:Int -- out:Int |
      value offset +
    ;]
    call
  ;
end-module
```

Explication :
- `offset` du mot et `offset` de la quotation appartiennent à deux frames différentes
- la quotation ne lit pas implicitement le local du parent
- la valeur est d’abord lue explicitement, puis capturée

Effet de pile :
- entrée `3 4`
- sortie `7`

Pourquoi :
- montre qu’un même nom peut être réutilisé entre frames distinctes

### Quotation passée à `list.map`

```nicole
module @examples_quotes_07
  : inc-all-quoted { xs:List<Int> -- ys:List<Int> }
    xs :[ | x:Int -- y:Int | x 1 + ;] list.map
  ;
end-module
```

Explication :
- la quotation est passée comme valeur
- `list.map` l’applique à chaque élément

Effet de pile :
- entrée `[2, 4]`
- sortie `[3, 5]`

Pourquoi :
- montre l’usage naturel des quotations comme valeurs

---

## 10. Capacités hôte déclarées

Contrat ABI déclaré pour cette section :

```nicole
module @host
  require console.log { msg:String -- } dirty
end-module
```

### Avertir l’hôte

```nicole
module @host
  require console.log { msg:String -- } dirty
end-module

module @examples_host_warn
  import @host.console.log as console.log

  dirty : warn { msg:String -- }
    msg console.log
  ;
end-module
```

Explication :
- déclare explicitement la capacité hôte requise
- importe cette capacité dans le module qui l’utilise
- transmet une chaîne à l’hôte via l’alias local `console.log`

Effet de pile :
- entrée `"attention"`
- aucune sortie

Pourquoi :
- exemple minimal d’utilisation d’une capacité hôte source-visible

### Lecture de configuration depuis l’hôte

Contrat ABI déclaré pour cet exemple :

```nicole
module @host
  require config.get { key:String -- r:Result<String,MapError> } pure
end-module
```

```nicole
module @host
  require config.get { key:String -- r:Result<String,MapError> } pure
end-module

module @examples_host_config
  import @host.config.get as config.get

  : read-config { key:String -- r:Result<String,MapError> }
    key config.get
  ;
end-module
```

Explication :
- la capacité requise est déclarée `pure` dans `@host`
- le `Result` fait partie de la signature ABI déclarée
- le mot utilisateur reste pur parce qu’il consomme une capacité hôte déclarée `pure`

Pourquoi :
- montre que `Result` à la frontière hôte reste explicite et contractuel

### Handle de fichier opaque déclaré par l’hôte

Contrat ABI supposé pour cet exemple :

```text
type:
host.io.FileHandle
kind:
opaque
```

```nicole
module @host
  require io.open-file
    { path:String mode:String -- r:Result<host.io.FileHandle,String> }
    dirty

  require io.read-line
    { file:host.io.FileHandle -- r:Result<String,String> }
    dirty

  require io.close-file { file:host.io.FileHandle -- } dirty
end-module
```

```nicole
module @host
  require io.open-file
    { path:String mode:String -- r:Result<host.io.FileHandle,String> }
    dirty

  require io.read-line
    { file:host.io.FileHandle -- r:Result<String,String> }
    dirty

  require io.close-file { file:host.io.FileHandle -- } dirty
end-module

module @examples_host_file
  import @host.io.open-file as io.open-file
  import @host.io.read-line as io.read-line
  import @host.io.close-file as io.close-file

  dirty : open-file { path:String mode:String -- r:Result<host.io.FileHandle,String> }
    path mode io.open-file
  ;

  dirty : read-line { file:host.io.FileHandle -- r:Result<String,String> }
    file io.read-line
  ;

  dirty : close-file { file:host.io.FileHandle -- }
    file io.close-file
  ;
end-module
```

Explication :
- `host.io.FileHandle` reste un type opaque hôte déclaré par le contrat ABI
- les capacités d’ouverture, lecture et fermeture sont déclarées par `require`
- le module applicatif les importe explicitement avec des aliases qualifiés

Pourquoi :
- montre la forme canonique minimale d’un type opaque hôte et de capacités hôte qui l’utilisent

### Valeur opaque hôte dans `List<T>` et `Map<String,T>`

```nicole
module @examples_host_file_containers
  : one-file { file:host.io.FileHandle -- xs:List<host.io.FileHandle> }
    []:List<host.io.FileHandle>
    file list.append
  ;

  : remember-file { name:String file:host.io.FileHandle -- files:Map<String,host.io.FileHandle> }
    map.empty:Map<String,host.io.FileHandle>
    name file map.set
  ;
end-module
```

Explication :
- une valeur opaque hôte peut être stockée dans une liste
- une valeur opaque hôte peut être stockée comme valeur d’une map

Pourquoi :
- montre que les conteneurs restent possibles sans autoriser les clés opaques

### Transport d’une valeur opaque hôte dans une quotation

```nicole
module @examples_host_file_quote
  : keep-file { file:host.io.FileHandle -- q:Quote<{ file:host.io.FileHandle | -- file2:host.io.FileHandle }> }
    :[ file:host.io.FileHandle | -- file2:host.io.FileHandle |
      file
    ;]
  ;
end-module
```

Explication :
- la quotation capture et retransmet la valeur opaque
- elle ne l’inspecte pas et ne la construit pas

Pourquoi :
- montre le transport Nicole pur d’une valeur opaque hôte

---

## 11. `export`

### Handler de message

```nicole
module @host
  require console.log { msg:String -- } dirty
end-module

module @app
  import @host.console.log as console.log

  dirty : demo-message { msg:String -- }
    msg console.log
  ;
  export : demo-message
end-module
```

Explication :
- expose un mot du programme à l’hôte
- la capacité hôte requise est déclarée dans `@host`
- l’hôte peut l’appeler comme point d’entrée ou handler

Effet de pile :
- entrée `"hello"`
- aucune sortie

Pourquoi :
- montre un export clair et idiomatique

### Handler sans retour

```nicole
module @host
  require console.log { msg:String -- } dirty
end-module

module @app
  import @host.console.log as console.log

  dirty : tick { -- }
    "tick" console.log
  ;
  export : tick
end-module
```

Explication :
- expose un mot sans entrée ni sortie
- utilise une capacité hôte importée localement

Effet de pile :
- aucune entrée
- aucune sortie

Pourquoi :
- montre un export événementiel minimal

### Export avec type opaque hôte déclaré

Contrat hôte supposé pour cet exemple :

```text
type:
host.io.FileHandle
kind:
opaque
```

```nicole
module @app.host_file
  : keep-open { file:host.io.FileHandle -- file2:host.io.FileHandle }
    file
  ;
  export : keep-open
end-module
```

Explication :
- le mot exporté utilise un type opaque hôte déjà déclaré par le contrat ABI
- aucune valeur opaque arbitraire supplémentaire n’est introduite

Pourquoi :
- montre qu’un export peut exposer un type opaque hôte déclaré

### Export simple avec entrée et sortie

```nicole
module @app
  : run { input:String -- output:String }
    input
  ;
  export : run
end-module
```

Explication :
- expose un mot normal du programme à l’hôte
- la signature du mot exporté reste le contrat ABI visible

Pourquoi :
- montre un export minimal avec valeur de retour

---

## 12. Exemple complet court

```nicole
module @host
  require console.log { msg:String -- } dirty
end-module

module @app
  import @host.console.log as console.log

  dirty : on-message { msg:String -- }
    msg console.log
  ;
  export : on-message

  : greeting { excited:Bool -- text:String }
    excited case
      true => "hello"
      false => "hi"
    end
  ;

  dirty : demo { -- }
    true greeting console.log
  ;
end-module
```

Explication :
- `greeting` choisit un message simple
- `demo` utilise un mot local puis une capacité hôte importée

Pourquoi :
- combine les formes de base sans ajouter de complexité inutile

---

## 13. Quotation retournée comme valeur

```nicole
module @examples_quotes_return
  : make-increment { -- q:Quote<{ | x:Int -- y:Int }> }
    :[ | x:Int -- y:Int | x 1 + ;]
  ;
end-module
```

Explication :
- construit une quotation et la renvoie comme valeur

Pourquoi :
- montre qu’une quotation peut être produite par un mot comme n’importe quelle autre valeur

---

## 14. Pureté et effet `dirty` (v0.14.0)

Contrat ABI déclaré dans cette section :

```nicole
module @host
  require console.log { msg:String -- } dirty
end-module
```

### Mot pur

```nicole
module @examples_effects_01
  : add-one { x:Int -- y:Int }
    x 1 +
  ;
end-module
```

Explication :
- ce mot n’appelle que du code pur
- aucune annotation `dirty` n’est requise

### Mot dirty direct

```nicole
module @host
  require console.log { msg:String -- } dirty
end-module

module @examples_effects_02
  import @host.console.log as console.log

  dirty : log-message { msg:String -- }
    msg console.log
  ;
end-module
```

Explication :
- `console.log` importe une capacité hôte déclarée `dirty`
- l’annotation `dirty` est donc obligatoire

### Export pur

```nicole
module @app
  : pure-main { -- code:Int }
    0
  ;
  export : pure-main
end-module
```

Explication :
- `export` n’impose pas dirty
- ce mot reste pur

### Export dirty

```nicole
module @host
  require console.log { msg:String -- } dirty
end-module

module @app
  import @host.console.log as console.log

  dirty : run { -- code:Int }
    "start" console.log
    0
  ;
  export : run
end-module
```

Explication :
- l’export appelle une capacité hôte importée et déclarée `dirty`
- il doit donc être annoté `dirty`

### Sous-mot dirty appelé

```nicole
module @host
  require console.log { msg:String -- } dirty
end-module

module @examples_effects_05
  import @host.console.log as console.log

  dirty : parent { msg:String -- }

    dirty : child-log { text:String -- }
      text console.log
    ;

    msg child-log
  ;
end-module
```

Explication :
- le sous-mot `child-log` est dirty
- le parent qui l’appelle est dirty

### DirtyQuote construit et appelé dans une frame dirty

```nicole
module @host
  require console.log { msg:String -- } dirty
end-module

module @examples_effects_06
  import @host.console.log as console.log

  dirty : run-dirty-quote { x:Int -- y:Int }
    x
    :[ | n:Int -- m:Int |
      "trace" console.log
      n 1 +
    ;]
    call
  ;
end-module
```

Explication :
- la quotation appelle une capacité hôte importée et déclarée `dirty`, elle est donc de type `DirtyQuote<{ | n:Int -- m:Int }>`
- `call` est dirty dans ce cas

### DirtyQuote passé à `list.map` dans une frame dirty

```nicole
module @host
  require console.log { msg:String -- } dirty
end-module

module @examples_effects_07
  import @host.console.log as console.log

  dirty : map-with-logging { xs:List<Int> -- ys:List<Int> }
    xs
    :[ | x:Int -- y:Int |
      "item" console.log
      x 1 +
    ;]
    list.map
  ;
end-module
```

Explication :
- `list.map` reste un builtin structurellement pur
- l’appel courant devient dirty parce que la quotation fournie est dirty

### Propagation indirecte transitive

```nicole
module @host
  require console.log { msg:String -- } dirty
end-module

module @examples_effects_08
  import @host.console.log as console.log

  dirty : dirty-leaf { msg:String -- }
    msg console.log
  ;

  dirty : dirty-middle { msg:String -- }
    msg dirty-leaf
  ;

  dirty : dirty-top { msg:String -- }
    msg dirty-middle
  ;
end-module
```

Explication :
- `dirty-leaf` est dirty par appel à une capacité hôte importée
- `dirty-middle` et `dirty-top` deviennent dirty par propagation indirecte
