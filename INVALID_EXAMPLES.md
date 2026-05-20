# INVALID_EXAMPLES.md

# Exemples invalides pour Nicole

Ce document montre ce qui doit être rejeté.

Les seules sources de vérité sont :

- `SYNTAXE.md`
- `SEMANTIQUE.md`
- `HOST_ABI.md`

Chaque exemple ci-dessous viole une règle déjà définie.

---

## 1. Erreurs de typage

### Addition de types incompatibles

```nicole
: bad-add { x:Int -- y:Int }
  x "oops" +
;
```

Pourquoi c’est invalide :
- `+` reçoit des opérandes de types incompatibles

Règle violée :
- les entrées d’un mot doivent respecter les types attendus

### Liste vide sans annotation

```nicole
: bad-empty-list { -- xs:List<Int> }
  []
;
```

Pourquoi c’est invalide :
- l’annotation de type de la liste vide est absente
- le contexte de retour n’est pas utilisé pour deviner le type par choix de design v1
- la clarté locale prime sur l’inférence implicite

Règle violée :
- `[]` non annoté est invalide en v1

### Map vide sans annotation

```nicole
: bad-empty { -- m:Map<String,Int> }
  map.empty
;
```

Pourquoi c’est invalide :
- l’annotation de type de la map vide est absente
- le contexte de retour n’est pas utilisé pour deviner le type par choix de design v1
- la clarté locale prime sur l’inférence implicite

Règle violée :
- `map.empty` non annoté est invalide en v1

### Type de clé de map invalide

```nicole
: bad-map
{
  --
  m:Map<List<Int>,String>
}
  map.empty:Map<List<Int>,String>
;
```

Pourquoi c’est invalide :
- `List<Int>` n’est pas un type de clé valide en v1

Règle violée :
- seules les clés `Int`, `String` et `Bool` sont définies pour `Map<K,V>` en v1

### Noms locaux dupliqués dans une même signature

```nicole
: bad { x:Int x:Int -- y:Int }
  x
;
```

Pourquoi c’est invalide :
- les deux inputs appartiennent à la même frame
- `x` serait déclaré deux fois comme nom local dans ce mot

Règle violée :
- les noms locaux doivent être uniques dans une même frame

---

## 2. Mauvais retours

### Valeur supplémentaire au retour

```nicole
: bad-return { -- n:Int }
  1 "ok"
;
```

Pourquoi c’est invalide :
- la signature annonce une seule sortie `Int`
- le corps produit une valeur supplémentaire
- le retour ne correspond donc pas exactement aux sorties déclarées

Règle violée :
- le retour doit correspondre exactement aux sorties déclarées

### Valeur manquante au retour

```nicole
: missing-return { -- n:Int }
;
```

Pourquoi c’est invalide :
- la signature annonce une sortie `Int`
- le corps ne produit aucune valeur

Règle violée :
- le retour doit correspondre exactement aux sorties déclarées

---

## 3. Branches incompatibles

### `if` avec branches de types différents

```nicole
: bad-if { flag:Bool -- n:Int }
  flag if
    1
  else
    "no"
  end
;
```

Pourquoi c’est invalide :
- les deux branches ne produisent pas le même type de sortie

Règle violée :
- `if` doit produire le même effet de pile dans les deux branches

### `case` non exhaustif sur `Bool`

```nicole
: bad-case-non-exhaustive { b:Bool -- text:String }
  b case
    true => "true"
  end
;
```

Pourquoi c’est invalide :
- `false` n’est pas couvert

Règle violée :
- `case` doit être exhaustif lorsque le type est fermé et que l’absence de couverture est prouvable

### `case` avec branches incompatibles

```nicole
: bad-case-incompatible-branches { b:Bool -- n:Int }
  b case
    true => 1
    false => "no"
  end
;
```

Pourquoi c’est invalide :
- les branches ne produisent pas le même type
- une branche produit `Int`
- l’autre produit `String`

Règle violée :
- toutes les branches d’un `case` doivent produire le même effet de pile

### Garde conditionnelle interdite

```nicole
: bad-case-guard { r:Result<Int,MapError> -- n:Int }
  r case
    Err(e) when e => 0
    _ => 1
  end
;
```

Pourquoi c’est invalide :
- `when` n’existe pas en v1
- les gardes conditionnelles sur pattern ne font pas partie du langage

Règle violée :
- Nicole v1 ne possède aucun mécanisme de garde sur `case`

### Pattern `MissingKey` sur un scrutinee `Bool`

```nicole
: bad-case-bool-variant { b:Bool -- n:Int }
  b case
    MissingKey => 0
    _ => 1
  end
;
```

Pourquoi c’est invalide :
- `MissingKey` n’est pas un variant de `Bool`
- ce pattern n’est compatible qu’avec un type d’erreur approprié comme `MapError`

Règle violée :
- les patterns d’un `case` doivent être compatibles avec le type du scrutinee

### Mauvais variant d’erreur sur `Result<Int,ListError>`

```nicole
: bad-case-listerror { r:Result<Int,ListError> -- n:Int }
  r case
    Ok(v) => v
    Err(MissingKey) => 0
  end
;
```

Pourquoi c’est invalide :
- `MissingKey` appartient à `MapError`
- `Result<Int,ListError>` ne peut pas être matché avec `Err(MissingKey)`

Règle violée :
- un pattern `Err(...)` doit utiliser une variante compatible avec le type d’erreur du `Result`

### Mauvais variant d’erreur sur `Result<Int,MapError>`

```nicole
: bad-case-maperror { r:Result<Int,MapError> -- n:Int }
  r case
    Ok(v) => v
    Err(OutOfBounds) => 0
  end
;
```

Pourquoi c’est invalide :
- `OutOfBounds` appartient à `ListError`
- `Result<Int,MapError>` ne peut pas être matché avec `Err(OutOfBounds)`

Règle violée :
- un pattern `Err(...)` doit utiliser une variante compatible avec le type d’erreur du `Result`

### Définition directe de `call`

```nicole
: call { -- n:Int }
  1
;
```

Pourquoi c’est invalide :
- `call` est une forme réservée du langage

Règle violée :
- une forme réservée ne peut pas être définie comme mot utilisateur

### Définition directe de `Ok!`

```nicole
: Ok! { x:Int -- r:Result<Int,String> }
  x
  "bad" drop
;
```

Pourquoi c’est invalide :
- `Ok!` est un constructeur builtin réservé

Règle violée :
- un builtin réservé ne peut pas être redéfini par le programme

### Définition directe de `result.is-ok`

```nicole
: result.is-ok { -- b:Bool }
  true
;
```

Pourquoi c’est invalide :
- `result.is-ok` appartient à l’espace builtin `result.*`

Règle violée :
- un nom builtin `result.*` ne peut pas être défini ni masqué par le programme

### Définition directe de `list.map`

```nicole
: list.map { -- }
;
```

Pourquoi c’est invalide :
- `list.map` appartient à l’espace builtin `list.*`

Règle violée :
- un nom builtin `list.*` ne peut pas être défini ni masqué par le programme

### Définition directe de `map.get`

```nicole
: map.get { -- }
;
```

Pourquoi c’est invalide :
- `map.get` appartient à l’espace builtin `map.*`

Règle violée :
- un nom builtin `map.*` ne peut pas être défini ni masqué par le programme

### Définition directe de `MissingKey`

```nicole
: MissingKey { -- text:String }
  "bad"
;
```

Pourquoi c’est invalide :
- `MissingKey` est une variante d’erreur réservée en v1

Règle violée :
- une variante d’erreur fermée du langage ne peut pas être redéfinie comme mot utilisateur

### `?` dans une frame qui ne retourne pas `Result`

```nicole
: bad-propagate { cfg:Map<String,Int> -- n:Int }
  cfg "timeout" map.get ?
;
```

Pourquoi c’est invalide :
- `?` peut retourner `Err(MissingKey)`
- le mot promet pourtant une sortie simple `Int`

Règle violée :
- une frame contenant `?` doit retourner exactement une seule valeur `Result<T,E>`

### `?` dans une frame à sorties multiples

```nicole
: bad-propagate-many { cfg:Map<String,Int> -- x:Int r:Result<Int,MapError> }
  cfg "timeout" map.get ?
  1
  2 Ok!
;
```

Pourquoi c’est invalide :
- la frame annonce plusieurs sorties
- `?` n’est autorisé en v1 que si la sortie complète est exactement une seule valeur `Result<T,E>`

Règle violée :
- une frame contenant `?` doit retourner exactement une seule valeur `Result<T,E>`

### `?` avec type d’erreur incompatible

```nicole
: bad-propagate-error { xs:List<Int> -- r:Result<Int,MapError> }
  xs 0 list.get ?
  1 Ok!
;
```

Pourquoi c’est invalide :
- `list.get` produit `Result<Int,ListError>`
- la frame retourne `Result<Int,MapError>`

Règle violée :
- le type d’erreur consommé par `?` doit correspondre exactement au type d’erreur de la sortie de frame
- aucune conversion implicite entre `ListError` et `MapError` n’existe en v1

### Construction invalide par forme expressionnelle `Ok(...)`

```nicole
: bad-ok-expression { -- r:Result<Int,String> }
  Ok(1)
;
```

Pourquoi c’est invalide :
- `Ok(v)` est une forme de motif pour `case`
- la construction d’une valeur `Result` doit utiliser le mot postfixe `Ok!`

Règle violée :
- `Ok(v)` n’est pas une forme de construction par expression en v1

### Construction invalide par forme expressionnelle `Err(...)`

```nicole
: bad-err-expression { -- r:Result<Int,String> }
  Err("bad")
;
```

Pourquoi c’est invalide :
- `Err(e)` est une forme de motif pour `case`
- la construction d’une valeur `Result` doit utiliser le mot postfixe `Err!`

Règle violée :
- `Err(e)` n’est pas une forme de construction par expression en v1

---

## 4. Quotations invalides

### Capture non typée

```nicole
:[ a | x:Int -- y:Int | x 1 + ;]
```

Pourquoi c’est invalide :
- la capture `a` n’est pas typée

Règle violée :
- les captures d’une quotation doivent être typées

### Quotation fermée avec `]` seul

```nicole
:[ | x:Int -- y:Int | x 1 + ]
```

Pourquoi c’est invalide :
- le corps concaténatif de la quotation n’est pas terminé par `;`
- `]` seul ne suffit plus à fermer une quotation de valeur en v1

Règle violée :
- une quotation de valeur doit être fermée par `;]`

### `call` avec mauvais type d’input

```nicole
: bad-call { s:String -- y:Int }
  s :[ | x:Int -- y:Int | x 1 + ;] call
;
```

Pourquoi c’est invalide :
- la quotation attend un input `Int`
- la pile fournit un `String`

Règle violée :
- `call` doit recevoir les inputs déclarés par le type de la quotation

### `call` avec ordre d’inputs incorrect

```nicole
: bad-call-order { -- n:Int }
  "oops" 3 :[ | x:Int y:String -- r:Int | x ;] call
;
```

Pourquoi c’est invalide :
- `call` attend les inputs sous la quotation dans l’ordre de la signature
- l’input le plus profond devrait correspondre à `x:Int`
- ici la valeur la plus profonde est `"oops"`, qui ne peut pas satisfaire `x:Int`

Règle violée :
- `call` doit recevoir ses inputs dans l’ordre de la signature de la quotation

### `call` avec nombre d’inputs insuffisant

```nicole
: bad-call-arity { x:Int -- y:Int }
  x :[ | a:Int b:Int -- r:Int | a b + ;] call
;
```

Pourquoi c’est invalide :
- la quotation attend deux inputs
- la pile n’en fournit qu’un seul au moment de `call`

Règle violée :
- `call` doit recevoir exactement les inputs déclarés par le type de la quotation

### Capture et input de même nom dans une quotation

```nicole
: bad { x:Int -- q:Quote<{ x:Int | x:Int -- y:Int }> }
  x
  :[ x:Int | x:Int -- y:Int |
    x
  ;]
;
```

Pourquoi c’est invalide :
- la capture `x` et l’input `x` appartiennent à la même frame de quotation
- le nom local `x` y serait déclaré deux fois

Règle violée :
- les noms locaux doivent être uniques dans une même frame de quotation

### Quotation avec `?` mais sortie non `Result`

```nicole
: bad-quote-propagate { xs:List<Map<String,Int>> -- ys:List<Int> }
  xs
  :[ | cfg:Map<String,Int> -- y:Int |
    cfg "timeout" map.get ?
    1
  ;]
  list.map
;
```

Pourquoi c’est invalide :
- `?` peut quitter la quotation avec `Err(MissingKey)`
- la quotation annonce pourtant une sortie simple `Int`

Règle violée :
- une quotation contenant `?` doit retourner exactement une seule valeur `Result<T,E>`

### Quotation qui retourne trop peu de valeurs

```nicole
: bad-quote-too-few { -- q:Quote<{ | x:Int -- y:Int z:Int }> }
  :[ | x:Int -- y:Int z:Int |
    x
  ;]
;
```

Pourquoi c’est invalide :
- la quotation déclare deux sorties
- son corps n’en produit qu’une seule

Règle violée :
- une quotation doit retourner exactement les sorties déclarées dans sa signature

### Quotation qui retourne trop de valeurs

```nicole
: bad-quote-too-many { -- q:Quote<{ | x:Int -- y:Int }> }
  :[ | x:Int -- y:Int |
    x
    1
  ;]
;
```

Pourquoi c’est invalide :
- la quotation déclare une seule sortie
- son corps laisse deux valeurs sur sa pile locale au retour

Règle violée :
- une quotation doit retourner exactement les sorties déclarées dans sa signature

### Tentative de propagation implicite à travers `list.map`

```nicole
: bad-try-map { cfgs:List<Map<String,Int>> -- r:Result<List<Int>,MapError> }
  cfgs
  :[ | cfg:Map<String,Int> -- r:Result<Int,MapError> |
    cfg "timeout" map.get ?
    drop
    1 Ok!
  ;]
  list.map
;
```

Pourquoi c’est invalide :
- la quotation retourne `Result<Int,MapError>`
- `list.map` renvoie donc `List<Result<Int,MapError>>`
- aucun court-circuit implicite ne transforme ce résultat en `Result<List<Int>,MapError>`

Règle violée :
- `list.map` ne propage pas implicitement les erreurs hors de la quotation
- une tentative d’utiliser `list.map` comme `list.try-map` doit être rejetée

### Hypothèse invalide sur le retour de `map.remove`

```nicole
: bad-remove-return { users:Map<String,Int> -- out:Map<String,Int> }
  users "alice" map.remove
;
```

Pourquoi c’est invalide :
- `map.remove` retourne `Result<Map<String,Int>,MapError>`
- le mot annonce une sortie simple `Map<String,Int>`

Règle violée :
- `map.remove` ne retourne pas une map simple en v1
- le retour doit correspondre exactement à la signature déclarée

### Utilisation invalide de `map.keys`

```nicole
: bad-map-keys { users:Map<String,Int> -- xs:List<String> }
  users map.keys
;
```

Pourquoi c’est invalide :
- `map.keys` ne fait pas partie de `Map` v1

Règle violée :
- `map.keys` est différé et n’est pas défini en v1

### Utilisation invalide de `map.values`

```nicole
: bad-map-values { users:Map<String,Int> -- xs:List<Int> }
  users map.values
;
```

Pourquoi c’est invalide :
- `map.values` ne fait pas partie de `Map` v1

Règle violée :
- `map.values` est différé et n’est pas défini en v1

### Utilisation invalide de `map.items`

```nicole
: bad-map-items { users:Map<String,Int> -- xs:List<String> }
  users map.items
;
```

Pourquoi c’est invalide :
- `map.items` ne fait pas partie de `Map` v1

Règle violée :
- `map.items` est différé et n’est pas défini en v1

### Utilisation invalide de `Ok!` comme pattern de `case`

```nicole
: bad-case-constructor-pattern { r:Result<Int,MapError> -- n:Int }
  r case
    Ok! => 1
    Err(MissingKey) => 0
  end
;
```

Pourquoi c’est invalide :
- `Ok!` est un constructeur postfixe
- les patterns de `case` pour `Result` restent `Ok(v)` et `Err(e)`

Règle violée :
- la syntaxe de construction et la syntaxe de pattern sont distinctes en v1

### Captures dupliquées dans une quotation

```nicole
:[ x:Int x:Int | -- y:Int | x ;]
```

Pourquoi c’est invalide :
- les deux captures appartiennent à la même frame de quotation
- le nom local `x` y serait déclaré deux fois

Règle violée :
- les noms locaux doivent être uniques dans une même frame de quotation

### Inputs dupliqués dans une quotation

```nicole
:[ | x:Int x:Int -- y:Int | x ;]
```

Pourquoi c’est invalide :
- les deux inputs appartiennent à la même frame de quotation
- le nom local `x` y serait déclaré deux fois

Règle violée :
- les noms locaux doivent être uniques dans une même frame de quotation

---

## 5. Sous-mots privés

### Appel hors du parent

```nicole
: invoice { price:Int qty:Int -- total:Int }

  : subtotal { price:Int qty:Int -- amount:Int }
    price qty *
  ;

  price qty subtotal
;

12 3 subtotal
```

Pourquoi c’est invalide :
- `subtotal` est un sous-mot privé local à son parent

Règle violée :
- les sous-mots privés ne sont pas visibles depuis l’extérieur du mot parent

### Sous-mot qui tente de capturer une variable du parent

```nicole
: outer { a:Int -- result:Int }

  : add-a { x:Int -- y:Int }
    x a +
  ;

  10 add-a
;
```

Pourquoi c’est invalide :
- `a` n’existe pas dans la frame de `add-a`
- les sous-mots ne capturent pas lexicalement les variables du parent

Règle violée :
- les sous-mots privés n’ont pas de capture lexicale implicite

### Sous-mot qui tente de lire un local du parent

```nicole
: bad { x:Int -- y:Int }
  : child { z:Int -- r:Int }
    z x +
  ;

  1 child
;
```

Pourquoi c’est invalide :
- `x` n’existe pas dans la frame de `child`
- `child` ne peut pas lire implicitement le local du parent

Règle violée :
- les sous-mots privés n’ont pas de capture lexicale implicite

---

## 6. Collections invalides

### `list.filter` avec quotation non booléenne

```nicole
: bad-filter-type { xs:List<Int> -- ys:List<Int> }
  xs :[ | x:Int -- keep:Int | x 1 + ;] list.filter
;
```

Pourquoi c’est invalide :
- `list.filter` exige une quotation de forme `x:T -- keep:Bool`
- ici la quotation retourne `Int`

Règle violée :
- la quotation passée à `list.filter` doit retourner `Bool`

### `list.fold` avec ordre d’inputs incorrect

```nicole
: bad-fold-order { xs:List<Int> -- n:Int }
  xs 0 :[ | x:Int acc:Int -- out:Int | acc x + ;] list.fold
;
```

Pourquoi c’est invalide :
- `list.fold` exige une quotation de forme `acc:Acc x:T -- out:Acc`
- ici l’élément et l’accumulateur sont déclarés dans l’ordre inverse

Règle violée :
- la quotation passée à `list.fold` doit respecter l’ordre `acc x`

### `list.reduce` avec type de retour incompatible

```nicole
: bad-reduce-type { xs:List<Int> -- n:Int }
  xs :[ | a:Int b:Int -- c:Bool | a b = ;] list.reduce
;
```

Pourquoi c’est invalide :
- `list.reduce` exige une quotation de forme `a:T b:T -- c:T`
- ici la quotation retourne `Bool` au lieu de `Int`

Règle violée :
- la quotation passée à `list.reduce` doit retourner le même type que les éléments réduits

### `list.reduce` sur liste vide prouvable

```nicole
: bad-reduce-empty { -- n:Int }
  []:List<Int>
  :[ | a:Int b:Int -- c:Int |
    a b +
  ;]
  list.reduce
;
```

Pourquoi c’est invalide :
- `list.reduce` exige une liste non vide
- ici, la vacuité de la liste est prouvable statiquement

Règle violée :
- `list.reduce` sur une liste vide prouvable doit être rejeté statiquement

---

## 7. `host.*`

### Mot hôte absent du contrat

```nicole
: show-config { key:String -- value:String }
  key host.read-config
;
```

Pourquoi c’est invalide :
- le contrat hôte supposé ne déclare pas `host.read-config`
- l’appel est donc invalide dans cet environnement d’intégration

Règle violée :
- un mot `host.*` doit être connu ou déclaré par le contrat d’intégration

### Définition directe d’un mot `host.*`

```nicole
: host.log { msg:String -- }
;
```

Pourquoi c’est invalide :
- un programme utilisateur ne peut pas définir un mot `host.*`

Règle violée :
- `host.*` est réservé aux mots fournis par l’hôte

### Mot hôte absent mais traité comme un `Result`

```nicole
: try-read-config { key:String -- r:Result<String,MapError> }
  key host.read-config
;
```

Pourquoi c’est invalide :
- le contrat hôte supposé ne déclare pas `host.read-config`
- l’absence de binding hôte ne devient pas automatiquement `Err(...)`

Règle violée :
- l’absence d’un mot `host.*` est une erreur d’intégration
- le mécanisme de liaison hôte n’est pas modélisé comme un `Result`

### Mot hôte recevant une quotation

Contrat hôte supposé dans cet exemple :

```text
host.run-later
signature:
{ q:Quote<{ | x:Int -- y:Int }> -- }
availability:
required
effect:
dirty
```

```nicole
: send-callback { q:Quote<{ | x:Int -- y:Int }> -- }
  q host.run-later
;
```

Pourquoi c’est invalide :
- l’ABI hôte v1 n’autorise pas `Quote<{ ... }>` comme valeur d’entrée d’un mot `host.*`

Règle violée :
- les quotations ne franchissent pas l’ABI hôte en v1

### Mot hôte retournant une quotation

Contrat hôte supposé dans cet exemple :

```text
host.make-callback
signature:
{ -- q:Quote<{ | x:Int -- y:Int }> }
availability:
required
effect:
dirty
```

```nicole
: fetch-callback { -- q:Quote<{ | x:Int -- y:Int }> }
  host.make-callback
;
```

Pourquoi c’est invalide :
- l’ABI hôte v1 n’autorise pas `Quote<{ ... }>` comme valeur de retour d’un mot `host.*`

Règle violée :
- les quotations ne franchissent pas l’ABI hôte en v1

### Export recevant une quotation

```nicole
export : app.accept-callback { q:Quote<{ | x:Int -- y:Int }> -- }
;
```

Pourquoi c’est invalide :
- un mot exporté expose ici une quotation à la frontière hôte

Règle violée :
- les quotations ne franchissent pas l’ABI hôte en v1

### Export retournant une quotation

```nicole
export : app.make-callback { -- q:Quote<{ | x:Int -- y:Int }> }
  :[ | x:Int -- y:Int | x 1 + ;]
;
```

Pourquoi c’est invalide :
- un mot exporté expose ici une quotation en sortie à la frontière hôte

Règle violée :
- les quotations ne franchissent pas l’ABI hôte en v1

### Export avec corps incompatible avec sa signature

```nicole
export : app.bad { -- n:Int }
;
```

Pourquoi c’est invalide :
- le mot exporté annonce une sortie `Int`
- son corps ne produit aucune valeur

Règle violée :
- un mot exporté reste un mot Nicole normal
- son corps doit respecter exactement sa signature avant l’exécution

---

## 8. Collisions de noms visibles

### Deux mots top-level de même nom avec types différents

```nicole
: id { x:Int -- y:Int }
  x
;

: id { x:String -- y:String }
  x
;
```

Pourquoi c’est invalide :
- `id` est un seul nom visible
- Nicole v1 n’autorise pas plusieurs définitions visibles portant ce même nom

Règle violée :
- un nom visible doit désigner une seule définition

### Deux mots top-level de même nom avec arités différentes

```nicole
: foo { a:Int b:Int -- r:Int }
  a b +
;

: foo { a:Int b:Int c:Int -- r:Int }
  a b + c +
;
```

Pourquoi c’est invalide :
- la différence d’arité ne crée pas une nouvelle identité nominale
- `foo` reste un seul nom visible

Règle violée :
- un nom visible doit désigner une seule définition

### Deux sous-mots frères de même nom

```nicole
: parent { -- }

  : child { -- n:Int }
    1
  ;

  : child { -- text:String }
    "x"
  ;
;
```

Pourquoi c’est invalide :
- les deux sous-mots appartiennent au même parent
- dans ce scope local, `child` est un seul nom visible

Règle violée :
- dans un même parent, deux sous-mots ne peuvent pas partager le même nom

### Deux exports de même nom

```nicole
export : entry { -- n:Int }
  1
;

export : entry { -- text:String }
  "hello"
;
```

Pourquoi c’est invalide :
- `entry` est un seul nom public côté hôte
- un nom d’export doit désigner un seul mot exporté

Règle violée :
- deux exports ne peuvent pas partager le même nom visible

### Collision entre `pub` et `export`

```nicole
pub : foo { -- n:Int }
  1
;

export : foo { -- n:Int }
  2
;
```

Pourquoi c’est invalide :
- la visibilité ne crée pas un second namespace
- `foo` reste un seul nom visible dans le programme

Règle violée :
- `pub` et `export` n’autorisent pas deux définitions visibles de même nom

### Collision entre sous-mot et mot top-level

```nicole
: child { -- n:Int }
  0
;

: parent { -- n:Int }

  : child { -- n:Int }
    1
  ;

  child
;
```

Pourquoi c’est invalide :
- Nicole v1 rejette un sous-mot et un mot top-level qui partagent le même nom visible
- cette collision n’est pas laissée à un futur système de modules ou d’`import`

Règle violée :
- un sous-mot et un mot top-level ne peuvent pas partager le même nom visible en v1

### `export` sur un sous-mot

```nicole
: parent { -- }

  export : child { -- n:Int }
    1
  ;
;
```

Pourquoi c’est invalide :
- en v1, `export` n’est autorisé que sur un mot top-level
- un sous-mot privé interne ne peut pas devenir un point d’entrée ABI

Règle violée :
- `export` est limité aux mots top-level en v1

---

## 9. Syntaxes explicitement interdites

### `let`

```nicole
let name = "Ada"
```

Pourquoi c’est invalide :
- `let` n’appartient pas à la syntaxe validée

Règle violée :
- `SYNTAXE.md` n’introduit pas de liaison locale impérative

### `const`

```nicole
pub const pi : Float = 3.14159
```

Pourquoi c’est invalide :
- `const` n’appartient pas à la syntaxe validée

Règle violée :
- `SYNTAXE.md` n’utilise pas de déclaration `const`

### `extern`

```nicole
extern host.log { msg:String -- }
```

Pourquoi c’est invalide :
- `extern` n’appartient pas à la syntaxe validée

Règle violée :
- le contrat hôte est décrit conceptuellement dans `HOST_ABI.md`, pas avec `extern`

### Signature avec `->`

```nicole
pub word add : Int Int -> Int
  +
;
```

Pourquoi c’est invalide :
- les signatures Nicole utilisent `{ ... -- ... }`
- `->` n’appartient pas à la syntaxe validée

Règle violée :
- `SYNTAXE.md` définit les signatures avec la forme `{ ... -- ... }`

---

## 10. Pureté et effet `dirty` invalides (v0.14.0)

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

### Annotation `dirty` manquante sur appel hôte dirty

```nicole
: bad-pure-host-call { -- }
  "hello" host.log
;
```

Pourquoi c’est invalide :
- `host.log` est dirty dans le contrat hôte
- le mot est inféré dirty mais n’est pas annoté `dirty`

Règle violée :
- inféré dirty + annotation absente => erreur statique

### Mot pur appelant un mot Nicole dirty

```nicole
dirty : log-message { msg:String -- }
  msg host.log
;

: bad-pure-calls-dirty { -- }
  "hello" log-message
;
```

Pourquoi c’est invalide :
- `bad-pure-calls-dirty` appelle un mot dirty
- il devrait être annoté `dirty`

Règle violée :
- un mot pur ne peut pas appeler du code dirty

### Export pur appelant du code dirty

```nicole
export : bad-pure-export { -- code:Int }
  "start" host.log
  0
;
```

Pourquoi c’est invalide :
- l’export est inféré dirty
- l’annotation `dirty` est absente

Règle violée :
- un export pur ne peut pas appeler du code dirty
- inféré dirty + annotation absente => erreur statique

### Annotation `dirty` redondante

```nicole
dirty : bad-redundant-dirty { -- n:Int }
  1
;
```

Pourquoi c’est invalide :
- le corps est inféré pur
- l’annotation dirty ne correspond pas à l’effet inféré

Règle violée :
- inféré pur + annoté dirty => erreur statique

### Ordre invalide des modificateurs

```nicole
dirty export : bad-order-a { -- }
;
```

```nicole
dirty pub : bad-order-b { -- }
;
```

```nicole
: dirty bad-order-c { -- }
;
```

Pourquoi c’est invalide :
- l’ordre normatif est visibilité puis `dirty` puis définition

Règle violée :
- `dirty export :` et `dirty pub :` sont interdits en v1
- la forme `: dirty foo` est interdite en v1

### Définition d’un mot nommé `dirty`

```nicole
: dirty { -- }
;
```

Pourquoi c’est invalide :
- `dirty` est réservé comme identifiant exact

Règle violée :
- un mot utilisateur ne peut pas s’appeler `dirty`

### Utilisation de `dirty` comme local

```nicole
: bad-dirty-local { dirty:Int -- x:Int }
  dirty
;
```

Pourquoi c’est invalide :
- `dirty` est réservé aussi pour les noms locaux

Règle violée :
- un local ne peut pas porter l’identifiant exact `dirty`

### Utilisation de `dirty` comme capture

```nicole
:[ dirty:Int | x:Int -- y:Int | x ;]
```

Pourquoi c’est invalide :
- `dirty` est réservé aussi pour les noms de capture

Règle violée :
- une capture ne peut pas porter l’identifiant exact `dirty`

### Construction de `DirtyQuote` dans une frame pure

```nicole
: bad-construct-dirty-quote { -- q:DirtyQuote<{ | x:Int -- y:Int }> }
  :[ | x:Int -- y:Int |
    "item" host.log
    x
  ;]
;
```

Pourquoi c’est invalide :
- la quotation est dirty car elle appelle `host.log`
- la frame de construction est pure

Règle violée :
- une frame pure ne peut pas construire de `DirtyQuote`

### Appel d’un `DirtyQuote` dans une frame pure

```nicole
: bad-call-dirty-quote { x:Int q:DirtyQuote<{ | n:Int -- m:Int }> -- y:Int }
  x q call
;
```

Pourquoi c’est invalide :
- `call` sur `DirtyQuote` rend l’appel dirty
- la frame appelante est pure

Règle violée :
- une frame pure ne peut pas appeler un `DirtyQuote`

### Passage d’un `DirtyQuote` à `list.map` dans une frame pure

```nicole
: bad-map-dirty-quote {
  xs:List<Int>
  q:DirtyQuote<{ | x:Int -- y:Int }>
  -- ys:List<Int>
}
  xs q list.map
;
```

Pourquoi c’est invalide :
- l’appel higher-order devient dirty avec une quotation dirty
- la frame appelante est pure

Règle violée :
- une frame pure ne peut pas passer un `DirtyQuote` à `list.map`
