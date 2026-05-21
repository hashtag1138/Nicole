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
: add-one { x:Int -- y:Int }
  x 1 +
;
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
: square { x:Int -- y:Int }
  x x *
;
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
: greet { excited:Bool -- msg:String }
  excited case
    true => "hello"
    false => "hi"
  end
;
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
: double { x:Int -- y:Int }
  x x +
;
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
: add-five { x:Int -- y:Int }
  x 5 +
;
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
: invoice { price:Int qty:Int -- total:Int }

  : subtotal { price:Int qty:Int -- amount:Int }
    price qty *
  ;

  price qty subtotal
;
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
: foo { x:Int -- y:Int }

  : bar { x:Int -- y:Int }
    1 x +
  ;

  3 bar
  x
  +
;
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
: id-int { x:Int -- y:Int }
  x
;

: id-string { x:String -- y:String }
  x
;
```

Explication :
- chaque nom visible désigne une seule définition
- des comportements voisins doivent utiliser des noms distincts

Utilisation :
- `42 id-int` retourne `42`
- `"hello" id-string` retourne `"hello"`

Pourquoi :
- montre la forme recommandée en Nicole v1 avec des noms explicites

### Récursion mutuelle

```nicole
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
```

Explication :
- `even` et `odd` ont chacun un nom distinct
- la collecte préalable des signatures permet leurs appels réciproques

Utilisation :
- `0 even` retourne `true`
- `1 odd` retourne `true`

Pourquoi :
- montre que la récursion mutuelle reste naturelle avec des noms distincts

---

## 5. Retours multiples

### Paire de sortie

```nicole
: pair { -- a:Int b:String }
  1 "ok"
;
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
: dimensions { -- width:Int height:Int }
  800 600
;
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
: abs { x:Int -- y:Int }
  x 0 < if
    0 x -
  else
    x
  end
;
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
: choose-yes { flag:Bool -- text:String }
  flag if
    "yes"
  else
    "no"
  end
;
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
: timeout-or-default { cfg:Map<String,Int> -- n:Int }
  cfg "timeout" map.get case
    Ok(v) => v
    Err(MissingKey) => 30
  end
;
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
: has-timeout-result { cfg:Map<String,Int> -- b:Bool }
  cfg "timeout" map.get result.is-ok
;

: timeout-or-30 { cfg:Map<String,Int> -- n:Int }
  cfg "timeout" map.get 30 result.unwrap-or
;
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
: require-timeout-flag { cfg:Map<String,Int> -- r:Result<Int,MapError> }
  cfg "timeout" map.get ?
  drop
  1 Ok!
;
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
: bool-label { b:Bool -- text:String }
  b case
    true => "true"
    false => "false"
  end
;
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
: cfg-with-timeout { -- cfg:Map<String,Int> }
  map.empty:Map<String,Int>
  "timeout" 30 map.set
;
```

Explication :
- construit une carte vide
- ajoute une clé `"timeout"`
- `map.set` retourne une nouvelle carte

Pourquoi :
- montre l’immuabilité des maps

### Présence d’une clé

```nicole
: has-timeout { cfg:Map<String,Int> -- ok:Bool }
  cfg "timeout" map.contains
;
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
: has-user { users:Map<String,Int> -- b:Bool }
  users "alice" map.contains
;
```

Explication :
- teste la présence d’une clé précise

Pourquoi :
- montre `map.contains` sur un cas simple

### Ajout ou remplacement dans une map

```nicole
: add-user { users:Map<String,Int> -- out:Map<String,Int> }
  users "alice" 42 map.set
;
```

Explication :
- renvoie une nouvelle map avec la valeur associée à `"alice"`
- la map d’entrée n’est jamais mutée sur place

Pourquoi :
- montre directement l’immuabilité de `map.set`

### Suppression explicite dans une map

```nicole
: remove-user
{
  users:Map<String,Int>
  --
  r:Result<Map<String,Int>,MapError>
}
  users "alice" map.remove
;
```

Explication :
- renvoie `Ok(newMap)` si la clé existe
- renvoie `Err(MissingKey)` si la clé est absente

Pourquoi :
- montre que `map.remove` ne supprime jamais silencieusement une clé absente

### Nombre d’entrées d’une map

```nicole
: user-count { users:Map<String,Int> -- n:Int }
  users map.len
;
```

Explication :
- retourne le nombre d’entrées de la map

Pourquoi :
- montre la primitive d’observation minimale conservée en v1

### Test de vacuité d’une map

```nicole
: has-no-user { users:Map<String,Int> -- b:Bool }
  users map.is-empty
;
```

Explication :
- retourne `true` si la map est vide
- retourne `false` si elle contient au moins une entrée

Pourquoi :
- montre `map.is-empty` comme observation simple

### Clés d’une map dans l’ordre d’insertion

```nicole
: user-keys { -- xs:List<String> }
  map.empty:Map<String,Int>
  "alice" 1 map.set
  "bob" 2 map.set
  map.keys
;
```

Explication :
- `map.keys` renvoie les clés dans l’ordre d’insertion

Pourquoi :
- rend l’ordre d’insertion observable explicitement

### Valeurs d’une map dans l’ordre des clés

```nicole
: user-values { -- xs:List<Int> }
  map.empty:Map<String,Int>
  "alice" 1 map.set
  "bob" 2 map.set
  map.values
;
```

Explication :
- `map.values` suit le même ordre que `map.keys`

Pourquoi :
- rend la correspondance ordre-clés/ordre-valeurs explicite

### Mise à jour sans déplacer la clé

```nicole
: keys-after-update { -- xs:List<String> }
  map.empty:Map<String,Int>
  "a" 1 map.set
  "b" 2 map.set
  "a" 9 map.set
  map.keys
;
```

Explication :
- une mise à jour de clé existante change la valeur
- la position initiale de la clé est conservée

Pourquoi :
- fixe le comportement d’ordre pour `map.set` sur clé existante

### Suppression puis réinsertion en fin d’ordre

```nicole
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
```

Explication :
- `map.remove` enlève la clé de l’ordre
- une réinsertion ultérieure place la clé en fin d’ordre

Pourquoi :
- illustre la règle `remove` puis `set`

### Test de vacuité d’une liste

```nicole
: has-no-value { xs:List<Int> -- b:Bool }
  xs list.is-empty
;
```

Explication :
- retourne `true` si la liste est vide
- retourne `false` sinon

Pourquoi :
- montre `list.is-empty` de manière directe

### Lecture dans une liste

```nicole
: first { xs:List<Int> -- n:Int }
  xs 0 list.get case
    Ok(v) => v
    Err(OutOfBounds) => 0
  end
;
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
: first-or-zero-v2 { xs:List<Int> -- n:Int }
  xs list.first case
    Ok(v) => v
    Err(OutOfBounds) => 0
  end
;
```

Explication :
- `list.first` retourne un `Result`
- une liste vide produit `Err(OutOfBounds)`

Pourquoi :
- montre la forme idiomatique de `list.first`

### Dernier élément avec erreur explicite

```nicole
: last-or-zero { xs:List<Int> -- n:Int }
  xs list.last case
    Ok(v) => v
    Err(OutOfBounds) => 0
  end
;
```

Explication :
- `list.last` retourne un `Result`
- une liste vide produit `Err(OutOfBounds)`

Pourquoi :
- montre la forme idiomatique de `list.last`

### Ajout en fin de liste

```nicole
: append-42 { xs:List<Int> -- ys:List<Int> }
  xs 42 list.append
;
```

Explication :
- renvoie une nouvelle liste avec `42` ajouté en fin

Pourquoi :
- rend explicite l’opération d’ajout immuable

### Inversion d’une liste

```nicole
: reversed { xs:List<Int> -- ys:List<Int> }
  xs list.reverse
;
```

Explication :
- renvoie une nouvelle liste dans l’ordre inverse

Pourquoi :
- documente `list.reverse` sans ambiguïté

### Transformation avec `list.map`

```nicole
: inc-all { xs:List<Int> -- ys:List<Int> }
  xs :[ | x:Int -- y:Int | x 1 + ;] list.map
;
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
: add-offset-all { xs:List<Int> offset:Int -- ys:List<Int> }
  xs
  offset
  :[ captured-offset:Int | x:Int -- y:Int |
    x captured-offset +
  ;]
  list.map
;
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
: mark-timeouts { cfgs:List<Map<String,Int>> -- ys:List<Result<Int,MapError>> }
  cfgs
  :[ | cfg:Map<String,Int> -- r:Result<Int,MapError> |
    cfg "timeout" map.get ?
    drop
    1 Ok!
  ;]
  list.map
;
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
: keep-positive { xs:List<Int> -- ys:List<Int> }
  xs :[ | x:Int -- keep:Bool | x 0 > ;] list.filter
;
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
: sum { xs:List<Int> -- n:Int }
  xs 0 :[ | acc:Int x:Int -- out:Int | acc x + ;] list.fold
;
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
: sum-or-zero { xs:List<Int> -- n:Int }
  xs 0 :[ | acc:Int x:Int -- out:Int | acc x + ;] list.fold
;
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
: sum-with-offset { xs:List<Int> offset:Int -- n:Int }
  xs
  0
  offset
  :[ captured-offset:Int | acc:Int x:Int -- out:Int |
    acc x + captured-offset +
  ;]
  list.fold
;
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
: sum-non-empty { xs:List<Int> -- n:Int }
  xs :[ | a:Int b:Int -- c:Int | a b + ;] list.reduce
;
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
: plus-one { x:Int -- y:Int }
  x :[ | n:Int -- m:Int | n 1 + ;] call
;
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
: add-captured { x:Int y:Int -- z:Int }
  x y :[ a:Int | n:Int -- m:Int | n a + ;] call
;
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
: capture-order { -- n:Int }
  2 3 :[ a:Int b:Int | -- r:Int | a b - ;] call
;
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
: call-order { -- n:Int }
  2 3 :[ | x:Int y:Int -- r:Int | x y - ;] call
;
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
: call-timeout-check { cfg:Map<String,Int> -- r:Result<Int,MapError> }
  cfg
  :[ | current:Map<String,Int> -- r:Result<Int,MapError> |
    current "timeout" map.get ?
    drop
    1 Ok!
  ;]
  call
;
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
: add-offset { x:Int offset:Int -- y:Int }
  x
  offset
  :[ offset:Int | value:Int -- out:Int |
    value offset +
  ;]
  call
;
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
: inc-all-quoted { xs:List<Int> -- ys:List<Int> }
  xs :[ | x:Int -- y:Int | x 1 + ;] list.map
;
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

## 10. `host.*`

Contrat hôte supposé dans cette section :

```text
host.log
signature:
{ msg:String -- }
availability:
required
effect:
dirty
```

### Avertir l’hôte

```nicole
dirty : warn { msg:String -- }
  msg host.log
;
```

Explication :
- transmet une chaîne à l’hôte
- `host.log` est ici un mot fourni par le contrat hôte supposé, pas une primitive standard du langage

Effet de pile :
- entrée `"attention"`
- aucune sortie

Pourquoi :
- exemple minimal d’appel à un mot fourni par l’hôte

### Lecture de configuration depuis l’hôte

Contrat hôte supposé pour cet exemple :

```text
host.config.get
signature:
{ key:String -- r:Result<String,MapError> }
availability:
required
effect:
pure
```

```nicole
: read-config { key:String -- r:Result<String,MapError> }
  key host.config.get
;
```

Explication :
- le mot hôte peut lui-même choisir de retourner un `Result`
- ce `Result` fait partie de la signature déclarée du mot hôte

Pourquoi :
- montre que `Result` à la frontière hôte reste explicite et contractuel

---

## 11. `export`

### Handler de message

```nicole
export dirty : app.demo-message { msg:String -- }
  msg host.log
;
```

Explication :
- expose un mot du programme à l’hôte
- `host.log` reste ici un mot fourni par le contrat hôte supposé
- l’hôte peut l’appeler comme point d’entrée ou handler

Effet de pile :
- entrée `"hello"`
- aucune sortie

Pourquoi :
- montre un export clair et idiomatique

### Handler sans retour

```nicole
export dirty : app.tick { -- }
  "tick" host.log
;
```

Explication :
- expose un mot sans entrée ni sortie
- `host.log` reste ici un mot fourni par le contrat hôte supposé

Effet de pile :
- aucune entrée
- aucune sortie

Pourquoi :
- montre un export événementiel minimal

### Export simple avec entrée et sortie

```nicole
export : app.run { input:String -- output:String }
  input
;
```

Explication :
- expose un mot normal du programme à l’hôte
- la signature d’export reste le contrat ABI visible

Pourquoi :
- montre un export minimal avec valeur de retour

---

## 12. Exemple complet court

Contrat hôte supposé :

```text
host.log
signature:
{ msg:String -- }
availability:
required
effect:
dirty
```

```nicole
export dirty : app.on-message { msg:String -- }
  msg host.log
;

: greeting { excited:Bool -- text:String }
  excited case
    true => "hello"
    false => "hi"
  end
;

dirty : demo { -- }
  true greeting host.log
;
```

Explication :
- `greeting` choisit un message simple
- `demo` utilise un mot local puis un mot hôte

Pourquoi :
- combine les formes de base sans ajouter de complexité inutile

---

## 13. Quotation retournée comme valeur

```nicole
: make-increment { -- q:Quote<{ | x:Int -- y:Int }> }
  :[ | x:Int -- y:Int | x 1 + ;]
;
```

Explication :
- construit une quotation et la renvoie comme valeur

Pourquoi :
- montre qu’une quotation peut être produite par un mot comme n’importe quelle autre valeur

---

## 14. Pureté et effet `dirty` (v0.14.0)

Contrat hôte supposé dans cette section :

```text
host.log
signature:
{ msg:String -- }
availability:
required
effect:
dirty
```

### Mot pur

```nicole
: add-one { x:Int -- y:Int }
  x 1 +
;
```

Explication :
- ce mot n’appelle que du code pur
- aucune annotation `dirty` n’est requise

### Mot dirty direct

```nicole
dirty : log-message { msg:String -- }
  msg host.log
;
```

Explication :
- `host.log` est dirty dans le contrat hôte
- l’annotation `dirty` est donc obligatoire

### Export pur

```nicole
export : pure-main { -- code:Int }
  0
;
```

Explication :
- `export` n’impose pas dirty
- ce mot reste pur

### Export dirty

```nicole
export dirty : app.run { -- code:Int }
  "start" host.log
  0
;
```

Explication :
- l’export appelle un binding hôte dirty
- il doit donc être annoté `dirty`

### Sous-mot dirty appelé

```nicole
dirty : parent { msg:String -- }

  dirty : child-log { text:String -- }
    text host.log
  ;

  msg child-log
;
```

Explication :
- le sous-mot `child-log` est dirty
- le parent qui l’appelle est dirty

### DirtyQuote construit et appelé dans une frame dirty

```nicole
dirty : run-dirty-quote { x:Int -- y:Int }
  x
  :[ | n:Int -- m:Int |
    "trace" host.log
    n 1 +
  ;]
  call
;
```

Explication :
- la quotation appelle `host.log`, elle est donc de type `DirtyQuote<{ | n:Int -- m:Int }>`
- `call` est dirty dans ce cas

### DirtyQuote passé à `list.map` dans une frame dirty

```nicole
dirty : map-with-logging { xs:List<Int> -- ys:List<Int> }
  xs
  :[ | x:Int -- y:Int |
    "item" host.log
    x 1 +
  ;]
  list.map
;
```

Explication :
- `list.map` reste un builtin structurellement pur
- l’appel courant devient dirty parce que la quotation fournie est dirty

### Propagation indirecte transitive

```nicole
dirty : dirty-leaf { msg:String -- }
  msg host.log
;

dirty : dirty-middle { msg:String -- }
  msg dirty-leaf
;

dirty : dirty-top { msg:String -- }
  msg dirty-middle
;
```

Explication :
- `dirty-leaf` est dirty par appel hôte direct
- `dirty-middle` et `dirty-top` deviennent dirty par propagation indirecte
