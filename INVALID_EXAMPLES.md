# INVALID_EXAMPLES.md

# Exemples invalides pour Nicole

Ce document montre ce qui doit être rejeté.

Les seules sources de vérité sont :

- `SYNTAXE.md`
- `SEMANTIQUE.md`
- `HOST_ABI.md`

Chaque exemple ci-dessous viole une règle déjà définie.

---

## 0. Confinement module (Phase 2)

### Définition utilisateur top-level

```nicole
: bad-top-level {
  --
}
;
```

Pourquoi c’est invalide :
- les mots définis par l’utilisateur doivent être contenus dans un bloc `module @... end-module`

Règle violée :
- une définition utilisateur top-level est rejetée en phase 2

---

## 0bis. Résolution et imports (Phase 3)

### Import wildcard interdit

```nicole
module @demo
  import @text.*

  : run { input:String -- out:List<String> }
    input @text.split
  ;
end-module
```

Pourquoi c’est invalide :
- la forme wildcard n’existe pas pour les imports

Règle violée :
- wildcard imports do not exist in v1

### Import top-level interdit

```nicole
import @host.console.log as console.log
```

Pourquoi c’est invalide :
- les imports ne sont autorisés qu’à l’intérieur d’un module

Règle violée :
- un import top-level est interdit en v1

### Collision d’alias d’import

```nicole
module @demo
  import @text as util
  import @tools as util
end-module
```

Pourquoi c’est invalide :
- `util` est déclaré deux fois comme alias visible

Règle violée :
- les aliases participent aux collisions de noms visibles

### Import dans le corps d’un mot interdit

```nicole
module @demo
  : run { -- }
    import @host.console.log as console.log
  ;
end-module
```

Pourquoi c’est invalide :
- les imports n’apparaissent jamais dans le corps d’un mot

Règle violée :
- un import dans le corps d’un mot est interdit

### Import sans alias n’expose pas le nom court

```nicole
module @demo
  import @text.split

  : run { input:String -- out:List<String> }
    input split
  ;
end-module
```

Pourquoi c’est invalide :
- `import @text.split` n’expose pas le nom court `split`
- sans alias, seule la forme qualifiée explicite est autorisée

Règle violée :
- sans alias, un import ciblé n’injecte pas de nom court

### Import après une définition de mot

```nicole
module @demo
  : run { -- }
  ;

  import @host.console.log as console.log
end-module
```

Pourquoi c’est invalide :
- les imports doivent apparaître avant toute définition de mot dans le module

Règle violée :
- un import ne peut pas apparaître après une définition de mot dans le même module

### Référence externe qualifiée sans import

```nicole
module @demo
  : run { input:String -- out:List<String> }
    input @text.split
  ;
end-module
```

Pourquoi c’est invalide :
- `@text.split` cible un mot utilisateur externe
- aucun import correspondant n’est déclaré

Règle violée :
- sans import, une référence externe `@text.word` est invalide

### Alias sur racine réservée

```nicole
module @demo
  import @text as host
end-module
```

Pourquoi c’est invalide :
- `host` est une racine réservée (reserved root)

Règle violée :
- un alias d’import ne peut pas occuper une racine réservée

### Alias importé utilisé hors du module importateur

```text
# a.nic
module @a
  import @host.console.log as console.log

  dirty : local-log { msg:String -- }
    msg console.log
  ;
end-module

# b.nic
module @b
  dirty : leaked-log { msg:String -- }
    msg console.log
  ;
end-module
```

Pourquoi c’est invalide :
- l’alias `console.log` est introduit dans `@a` seulement
- `@b` tente de l’utiliser sans l’avoir importé dans son propre module

Règle violée :
- les aliases d’import sont module-locaux
- un alias ne fuit pas vers les autres modules

### Alias qualifié commençant par `@`

```nicole
module @demo
  import @host.console.log as @console.log
end-module
```

Pourquoi c’est invalide :
- un alias d’import ne peut pas commencer par `@`

Règle violée :
- un alias simple ou qualifié ne peut pas commencer par `@`

### Alias qualifié occupant la racine réservée `host`

```nicole
module @demo
  import @host.console.log as host.log
end-module
```

Pourquoi c’est invalide :
- `host` est une racine réservée
- un alias qualifié reste un nom local et ne peut pas occuper cette racine

Règle violée :
- un alias simple ou qualifié ne peut pas occuper une racine réservée

### Cycle d’import interdit

```text
# a.nic
module @a
  import @b as b

  : ping { n:Int -- n2:Int }
    n b.pong
  ;
end-module

# b.nic
module @b
  import @a as a

  : pong { n:Int -- n2:Int }
    n a.ping
  ;
end-module
```

Pourquoi c’est invalide :
- le graphe d’import contient un cycle entre `@a` et `@b`

Règle violée :
- les cycles d’import sont interdits
- diagnostic shape admise :
  `cyclic import detected: @a -> @b -> @a`

---

## 1. Erreurs de typage

### Addition de types incompatibles

```nicole
module @invalid.phase6

  : bad-add { x:Int -- y:Int }
    x "oops" +
  ;

end-module
```

Pourquoi c’est invalide :
- `+` reçoit des opérandes de types incompatibles

Règle violée :
- les entrées d’un mot doivent respecter les types attendus

### Liste vide sans annotation

```nicole
module @invalid.phase6

  : bad-empty-list { -- xs:List<Int> }
    []
  ;

end-module
```

Pourquoi c’est invalide :
- l’annotation de type de la liste vide est absente
- le contexte de retour n’est pas utilisé pour deviner le type par choix de design v1
- la clarté locale prime sur l’inférence implicite

Règle violée :
- `[]` non annoté est invalide en v1

### Map vide sans annotation

```nicole
module @invalid.phase6

  : bad-empty { -- m:Map<String,Int> }
    map.empty
  ;

end-module
```

Pourquoi c’est invalide :
- l’annotation de type de la map vide est absente
- le contexte de retour n’est pas utilisé pour deviner le type par choix de design v1
- la clarté locale prime sur l’inférence implicite

Règle violée :
- `map.empty` non annoté est invalide en v1

### Type de clé de map invalide

```nicole
module @invalid.phase6

  : bad-map
  {
    --
    m:Map<List<Int>,String>
  }
    map.empty:Map<List<Int>,String>
  ;

end-module
```

Pourquoi c’est invalide :
- `List<Int>` n’est pas un type de clé valide en v1

Règle violée :
- seules les clés `Int`, `String` et `Bool` sont définies pour `Map<K,V>` en v1

### Noms locaux dupliqués dans une même signature

```nicole
module @invalid.phase6

  : bad { x:Int x:Int -- y:Int }
    x
  ;

end-module
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
module @invalid.phase6

  : bad-return { -- n:Int }
    1 "ok"
  ;

end-module
```

Pourquoi c’est invalide :
- la signature annonce une seule sortie `Int`
- le corps produit une valeur supplémentaire
- le retour ne correspond donc pas exactement aux sorties déclarées

Règle violée :
- le retour doit correspondre exactement aux sorties déclarées

### Valeur manquante au retour

```nicole
module @invalid.phase6

  : missing-return { -- n:Int }
  ;

end-module
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
module @invalid.phase6

  : bad-if { flag:Bool -- n:Int }
    flag if
      1
    else
      "no"
    end
  ;

end-module
```

Pourquoi c’est invalide :
- les deux branches ne produisent pas le même type de sortie

Règle violée :
- `if` doit produire le même effet de pile dans les deux branches

### `case` non exhaustif sur `Bool`

```nicole
module @invalid.phase6

  : bad-case-non-exhaustive { b:Bool -- text:String }
    b case
      true => "true"
    end
  ;

end-module
```

Pourquoi c’est invalide :
- `false` n’est pas couvert

Règle violée :
- `case` doit être exhaustif lorsque le type est fermé et que l’absence de couverture est prouvable

### `case` avec branches incompatibles

```nicole
module @invalid.phase6

  : bad-case-incompatible-branches { b:Bool -- n:Int }
    b case
      true => 1
      false => "no"
    end
  ;

end-module
```

Pourquoi c’est invalide :
- les branches ne produisent pas le même type
- une branche produit `Int`
- l’autre produit `String`

Règle violée :
- toutes les branches d’un `case` doivent produire le même effet de pile

### Garde conditionnelle dirty interdite

```nicole
module @host
  require console.log { msg:String -- } dirty
end-module

module @invalid.phase6
  import @host.console.log as console.log

  : bad-case-guard { r:Result<Int,MapError> -- text:String }
    r case
      Ok(v) when "trace" console.log true => "ok"
      Err(MissingKey) => "missing"
    end
  ;

end-module
```

Pourquoi c’est invalide :
- la branche gardée utilise `console.log` dans le guard
- `console.log` importe une capacité hôte déclarée `dirty`
- un guard doit rester pur

Règle violée :
- un guard ne peut pas appeler de code dirty

### Pattern `MissingKey` sur un scrutinee `Bool`

```nicole
module @invalid.phase6

  : bad-case-bool-variant { b:Bool -- n:Int }
    b case
      MissingKey => 0
      _ => 1
    end
  ;

end-module
```

Pourquoi c’est invalide :
- `MissingKey` n’est pas un variant de `Bool`
- ce pattern n’est compatible qu’avec un type d’erreur approprié comme `MapError`

Règle violée :
- les patterns d’un `case` doivent être compatibles avec le type du scrutinee

### Mauvais variant d’erreur sur `Result<Int,ListError>`

```nicole
module @invalid.phase6

  : bad-case-listerror { r:Result<Int,ListError> -- n:Int }
    r case
      Ok(v) => v
      Err(MissingKey) => 0
    end
  ;

end-module
```

Pourquoi c’est invalide :
- `MissingKey` appartient à `MapError`
- `Result<Int,ListError>` ne peut pas être matché avec `Err(MissingKey)`

Règle violée :
- un pattern `Err(...)` doit utiliser une variante compatible avec le type d’erreur du `Result`

### Mauvais variant d’erreur sur `Result<Int,MapError>`

```nicole
module @invalid.phase6

  : bad-case-maperror { r:Result<Int,MapError> -- n:Int }
    r case
      Ok(v) => v
      Err(OutOfBounds) => 0
    end
  ;

end-module
```

Pourquoi c’est invalide :
- `OutOfBounds` appartient à `ListError`
- `Result<Int,MapError>` ne peut pas être matché avec `Err(OutOfBounds)`

Règle violée :
- un pattern `Err(...)` doit utiliser une variante compatible avec le type d’erreur du `Result`

### Définition directe de `call`

```nicole
module @invalid.phase6

  : call { -- n:Int }
    1
  ;

end-module
```

Pourquoi c’est invalide :
- `call` est une forme réservée du langage

Règle violée :
- une forme réservée ne peut pas être définie comme mot utilisateur

### Définition directe de `Ok!`

```nicole
module @invalid.phase6

  : Ok! { x:Int -- r:Result<Int,String> }
    x
    "bad" drop
  ;

end-module
```

Pourquoi c’est invalide :
- `Ok!` est un constructeur builtin réservé

Règle violée :
- un builtin réservé ne peut pas être redéfini par le programme

### Définition directe de `result.is-ok`

```nicole
module @invalid.phase6

  : result.is-ok { -- b:Bool }
    true
  ;

end-module
```

Pourquoi c’est invalide :
- `result.is-ok` appartient à l’espace builtin `result.*`

Règle violée :
- un nom builtin `result.*` ne peut pas être défini ni masqué par le programme

### Définition directe de `list.map`

```nicole
module @invalid.phase6

  : list.map { -- }
  ;

end-module
```

Pourquoi c’est invalide :
- `list.map` appartient à l’espace builtin `list.*`

Règle violée :
- un nom builtin `list.*` ne peut pas être défini ni masqué par le programme

### Définition directe de `map.get`

```nicole
module @invalid.phase6

  : map.get { -- }
  ;

end-module
```

Pourquoi c’est invalide :
- `map.get` appartient à l’espace builtin `map.*`

Règle violée :
- un nom builtin `map.*` ne peut pas être défini ni masqué par le programme

### Définition directe de `MissingKey`

```nicole
module @invalid.phase6

  : MissingKey { -- text:String }
    "bad"
  ;

end-module
```

Pourquoi c’est invalide :
- `MissingKey` est une variante d’erreur réservée en v1

Règle violée :
- une variante d’erreur fermée du langage ne peut pas être redéfinie comme mot utilisateur

### `?` dans une frame qui ne retourne pas `Result`

```nicole
module @invalid.phase6

  : bad-propagate { cfg:Map<String,Int> -- n:Int }
    cfg "timeout" map.get ?
  ;

end-module
```

Pourquoi c’est invalide :
- `?` peut retourner `Err(MissingKey)`
- le mot promet pourtant une sortie simple `Int`

Règle violée :
- une frame contenant `?` doit retourner exactement une seule valeur `Result<T,E>`

### `?` dans une frame à sorties multiples

```nicole
module @invalid.phase6

  : bad-propagate-many { cfg:Map<String,Int> -- x:Int r:Result<Int,MapError> }
    cfg "timeout" map.get ?
    1
    2 Ok!
  ;

end-module
```

Pourquoi c’est invalide :
- la frame annonce plusieurs sorties
- `?` n’est autorisé en v1 que si la sortie complète est exactement une seule valeur `Result<T,E>`

Règle violée :
- une frame contenant `?` doit retourner exactement une seule valeur `Result<T,E>`

### `?` avec type d’erreur incompatible

```nicole
module @invalid.phase6

  : bad-propagate-error { xs:List<Int> -- r:Result<Int,MapError> }
    xs 0 list.get ?
    1 Ok!
  ;

end-module
```

Pourquoi c’est invalide :
- `list.get` produit `Result<Int,ListError>`
- la frame retourne `Result<Int,MapError>`

Règle violée :
- le type d’erreur consommé par `?` doit correspondre exactement au type d’erreur de la sortie de frame
- aucune conversion implicite entre `ListError` et `MapError` n’existe en v1

### Construction invalide par forme expressionnelle `Ok(...)`

```nicole
module @invalid.phase6

  : bad-ok-expression { -- r:Result<Int,String> }
    Ok(1)
  ;

end-module
```

Pourquoi c’est invalide :
- `Ok(v)` est une forme de motif pour `case`
- la construction d’une valeur `Result` doit utiliser le mot postfixe `Ok!`

Règle violée :
- `Ok(v)` n’est pas une forme de construction par expression en v1

### Construction invalide par forme expressionnelle `Err(...)`

```nicole
module @invalid.phase6

  : bad-err-expression { -- r:Result<Int,String> }
    Err("bad")
  ;

end-module
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
module @invalid.phase6

  : bad-call { s:String -- y:Int }
    s :[ | x:Int -- y:Int | x 1 + ;] call
  ;

end-module
```

Pourquoi c’est invalide :
- la quotation attend un input `Int`
- la pile fournit un `String`

Règle violée :
- `call` doit recevoir les inputs déclarés par le type de la quotation

### `call` avec ordre d’inputs incorrect

```nicole
module @invalid.phase6

  : bad-call-order { -- n:Int }
    "oops" 3 :[ | x:Int y:String -- r:Int | x ;] call
  ;

end-module
```

Pourquoi c’est invalide :
- `call` attend les inputs sous la quotation dans l’ordre de la signature
- l’input le plus profond devrait correspondre à `x:Int`
- ici la valeur la plus profonde est `"oops"`, qui ne peut pas satisfaire `x:Int`

Règle violée :
- `call` doit recevoir ses inputs dans l’ordre de la signature de la quotation

### `call` avec nombre d’inputs insuffisant

```nicole
module @invalid.phase6

  : bad-call-arity { x:Int -- y:Int }
    x :[ | a:Int b:Int -- r:Int | a b + ;] call
  ;

end-module
```

Pourquoi c’est invalide :
- la quotation attend deux inputs
- la pile n’en fournit qu’un seul au moment de `call`

Règle violée :
- `call` doit recevoir exactement les inputs déclarés par le type de la quotation

### Capture et input de même nom dans une quotation

```nicole
module @invalid.phase6

  : bad { x:Int -- q:Quote<{ x:Int | x:Int -- y:Int }> }
    x
    :[ x:Int | x:Int -- y:Int |
      x
    ;]
  ;

end-module
```

Pourquoi c’est invalide :
- la capture `x` et l’input `x` appartiennent à la même frame de quotation
- le nom local `x` y serait déclaré deux fois

Règle violée :
- les noms locaux doivent être uniques dans une même frame de quotation

### Quotation avec `?` mais sortie non `Result`

```nicole
module @invalid.phase6

  : bad-quote-propagate { xs:List<Map<String,Int>> -- ys:List<Int> }
    xs
    :[ | cfg:Map<String,Int> -- y:Int |
      cfg "timeout" map.get ?
      1
    ;]
    list.map
  ;

end-module
```

Pourquoi c’est invalide :
- `?` peut quitter la quotation avec `Err(MissingKey)`
- la quotation annonce pourtant une sortie simple `Int`

Règle violée :
- une quotation contenant `?` doit retourner exactement une seule valeur `Result<T,E>`

### Quotation qui retourne trop peu de valeurs

```nicole
module @invalid.phase6

  : bad-quote-too-few { -- q:Quote<{ | x:Int -- y:Int z:Int }> }
    :[ | x:Int -- y:Int z:Int |
      x
    ;]
  ;

end-module
```

Pourquoi c’est invalide :
- la quotation déclare deux sorties
- son corps n’en produit qu’une seule

Règle violée :
- une quotation doit retourner exactement les sorties déclarées dans sa signature

### Quotation qui retourne trop de valeurs

```nicole
module @invalid.phase6

  : bad-quote-too-many { -- q:Quote<{ | x:Int -- y:Int }> }
    :[ | x:Int -- y:Int |
      x
      1
    ;]
  ;

end-module
```

Pourquoi c’est invalide :
- la quotation déclare une seule sortie
- son corps laisse deux valeurs sur sa pile locale au retour

Règle violée :
- une quotation doit retourner exactement les sorties déclarées dans sa signature

### Tentative de propagation implicite à travers `list.map`

```nicole
module @invalid.phase6

  : bad-try-map { cfgs:List<Map<String,Int>> -- r:Result<List<Int>,MapError> }
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

Pourquoi c’est invalide :
- la quotation retourne `Result<Int,MapError>`
- `list.map` renvoie donc `List<Result<Int,MapError>>`
- aucun court-circuit implicite ne transforme ce résultat en `Result<List<Int>,MapError>`

Règle violée :
- `list.map` ne propage pas implicitement les erreurs hors de la quotation
- une tentative d’utiliser `list.map` comme `list.try-map` doit être rejetée

### Hypothèse invalide sur le retour de `map.remove`

```nicole
module @invalid.phase6

  : bad-remove-return { users:Map<String,Int> -- out:Map<String,Int> }
    users "alice" map.remove
  ;

end-module
```

Pourquoi c’est invalide :
- `map.remove` retourne `Result<Map<String,Int>,MapError>`
- le mot annonce une sortie simple `Map<String,Int>`

Règle violée :
- `map.remove` ne retourne pas une map simple en v1
- le retour doit correspondre exactement à la signature déclarée

### Utilisation invalide de `map.has`

```nicole
module @invalid.phase6

  : bad-map-has { users:Map<String,Int> -- b:Bool }
    users "alice" map.has
  ;

end-module
```

Pourquoi c’est invalide :
- `map.has` ne fait pas partie de `Map` v1

Règle violée :
- `map.has` est différé et n’est pas défini en v1

### Utilisation invalide de `map.to-list`

```nicole
module @invalid.phase6

  : bad-map-to-list { users:Map<String,Int> -- xs:List<String> }
    users map.to-list
  ;

end-module
```

Pourquoi c’est invalide :
- `map.to-list` ne fait pas partie de `Map` v1

Règle violée :
- `map.to-list` est différé et n’est pas défini en v1

### Utilisation invalide de `map.items`

```nicole
module @invalid.phase6

  : bad-map-items { users:Map<String,Int> -- xs:List<String> }
    users map.items
  ;

end-module
```

Pourquoi c’est invalide :
- `map.items` ne fait pas partie de `Map` v1

Règle violée :
- `map.items` est différé et n’est pas défini en v1

### Utilisation invalide de `list.zip`

```nicole
module @invalid.phase6

  : bad-list-zip { xs:List<Int> ys:List<Int> -- zs:List<Int> }
    xs ys list.zip
  ;

end-module
```

Pourquoi c’est invalide :
- `list.zip` ne fait pas partie de `List` v1

Règle violée :
- `list.zip` est différé et n’est pas défini en v1

### Utilisation invalide de `Ok!` comme pattern de `case`

```nicole
module @invalid.phase6

  : bad-case-constructor-pattern { r:Result<Int,MapError> -- n:Int }
    r case
      Ok! => 1
      Err(MissingKey) => 0
    end
  ;

end-module
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
module @invalid.phase6

  : invoice { price:Int qty:Int -- total:Int }
  
    : subtotal { price:Int qty:Int -- amount:Int }
      price qty *
    ;
  
    price qty subtotal
  ;
  
  12 3 subtotal

end-module
```

Pourquoi c’est invalide :
- `subtotal` est un sous-mot privé local à son parent

Règle violée :
- les sous-mots privés ne sont pas visibles depuis l’extérieur du mot parent

### Sous-mot qui tente de capturer une variable du parent

```nicole
module @invalid.phase6

  : outer { a:Int -- result:Int }
  
    : add-a { x:Int -- y:Int }
      x a +
    ;
  
    10 add-a
  ;

end-module
```

Pourquoi c’est invalide :
- `a` n’existe pas dans la frame de `add-a`
- les sous-mots ne capturent pas lexicalement les variables du parent

Règle violée :
- les sous-mots privés n’ont pas de capture lexicale implicite

### Sous-mot qui tente de lire un local du parent

```nicole
module @invalid.phase6

  : bad { x:Int -- y:Int }
    : child { z:Int -- r:Int }
      z x +
    ;
  
    1 child
  ;

end-module
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
module @invalid.phase6

  : bad-filter-type { xs:List<Int> -- ys:List<Int> }
    xs :[ | x:Int -- keep:Int | x 1 + ;] list.filter
  ;

end-module
```

Pourquoi c’est invalide :
- `list.filter` exige une quotation de forme `x:T -- keep:Bool`
- ici la quotation retourne `Int`

Règle violée :
- la quotation passée à `list.filter` doit retourner `Bool`

### `list.fold` avec ordre d’inputs incorrect

```nicole
module @invalid.phase6

  : bad-fold-order { xs:List<Int> -- n:Int }
    xs 0 :[ | x:Int acc:Int -- out:Int | acc x + ;] list.fold
  ;

end-module
```

Pourquoi c’est invalide :
- `list.fold` exige une quotation de forme `acc:Acc x:T -- out:Acc`
- ici l’élément et l’accumulateur sont déclarés dans l’ordre inverse

Règle violée :
- la quotation passée à `list.fold` doit respecter l’ordre `acc x`

### `list.reduce` avec type de retour incompatible

```nicole
module @invalid.phase6

  : bad-reduce-type { xs:List<Int> -- n:Int }
    xs :[ | a:Int b:Int -- c:Bool | a b = ;] list.reduce
  ;

end-module
```

Pourquoi c’est invalide :
- `list.reduce` exige une quotation de forme `a:T b:T -- c:T`
- ici la quotation retourne `Bool` au lieu de `Int`

Règle violée :
- la quotation passée à `list.reduce` doit retourner le même type que les éléments réduits

### `list.reduce` sur liste vide prouvable

```nicole
module @invalid.phase6

  : bad-reduce-empty { -- n:Int }
    []:List<Int>
    :[ | a:Int b:Int -- c:Int |
      a b +
    ;]
    list.reduce
  ;

end-module
```

Pourquoi c’est invalide :
- `list.reduce` exige une liste non vide
- ici, la vacuité de la liste est prouvable statiquement

Règle violée :
- `list.reduce` sur une liste vide prouvable doit être rejeté statiquement

---

## 7. Contrat ABI hôte et capacités invalides

### Appel source direct d’une capacité `host.*`

```nicole
module @invalid.phase6

  : show-config { key:String -- value:String }
    key host.read-config
  ;

end-module
```

Pourquoi c’est invalide :
- les appels source directs `host.*` ne font plus partie de la surface valide du langage
- une capacité hôte doit être déclarée dans `module @host`, puis importée dans le module consommateur

Règle violée :
- un appel source direct `host.*` est interdit en v1

### Import d’une capacité hôte absente du contrat consolidé

```nicole
module @invalid.phase6
  import @host.config.get as config.get

  : read-config { key:String -- r:Result<String,MapError> }
    key config.get
  ;
end-module
```

Pourquoi c’est invalide :
- `config.get` est importé depuis `@host`
- aucune déclaration `require config.get ...` n’existe dans le contrat consolidé `@host`

Règle violée :
- une capacité hôte importée doit être déclarée explicitement par le contrat consolidé `@host`

### Import wildcard hôte interdit

```nicole
module @invalid.phase6
  import @host.io.*
end-module
```

```nicole
module @invalid.phase6
  import @host.io.* as *
end-module
```

Pourquoi c’est invalide :
- les wildcard imports n’existent pas en v1
- `as *` ne vaut que pour une sélection explicite de symboles, pas pour un wildcard import

Règle violée :
- les wildcard imports hôte n’ont aucune forme valide en v1

### Définition directe d’un mot `host.*`

```nicole
module @invalid.phase6

  : host.log { msg:String -- }
  ;

end-module
```

Pourquoi c’est invalide :
- un programme utilisateur ne peut pas définir un mot `host.*`
- `host.*` reste réservé pour les appels source hôte interdits et comme vocabulaire historique obsolète, pas à des mots Nicole définis par l’utilisateur

Règle violée :
- un mot utilisateur ne peut pas utiliser la racine réservée `host.*`

### `module @host` contenant un mot ordinaire

```nicole
module @host

  : log-message { msg:String -- }
    msg drop
  ;

end-module
```

Pourquoi c’est invalide :
- `module @host` n’est pas un module utilisateur normal
- son corps est réservé aux déclarations ABI `require` et `opaque`

Règle violée :
- `module @host` ne peut pas contenir de définition de mot

### `module @host` contenant un `import`

```nicole
module @host
  import @text as t
end-module
```

Pourquoi c’est invalide :
- `module @host` n’est pas une surface d’import
- les imports sont interdits dans `module @host`

Règle violée :
- `module @host` ne peut pas contenir d’import

### `module @host` contenant un `export`

```nicole
module @host
  export : run
end-module
```

Pourquoi c’est invalide :
- la présence même de `export` dans `module @host` est interdite
- `module @host` n’exporte pas de mots Nicole utilisateurs
- son rôle est limité à la déclaration du contrat ABI requis

Règle violée :
- `module @host` ne peut pas contenir d’`export`

### `require` hors `module @host`

```nicole
module @invalid.phase6
  require console.log { msg:String -- } dirty
end-module
```

Pourquoi c’est invalide :
- `require` n’est légal que dans `module @host`

Règle violée :
- une déclaration `require` hors `module @host` est invalide

### `require` sans effet ABI explicite

```nicole
module @host
  require console.log { msg:String -- }
end-module
```

Pourquoi c’est invalide :
- chaque `require` doit déclarer explicitement `pure` ou `dirty`

Règle violée :
- un `require` sans effet ABI explicite est invalide

### Utilisation de `pure` comme modificateur de mot

```nicole
module @invalid.phase6

  pure : bad-pure-modifier { -- n:Int }
    1
  ;

end-module
```

Pourquoi c’est invalide :
- `pure` n’est pas un modificateur général de définition de mot en v1
- `pure` n’existe en source que dans la surface ABI de `require`

Règle violée :
- `pure` hors déclaration ABI `require` est invalide

### Déclarations divergentes d’une même capacité hôte par signature

```text
# host-a.nic
module @host
  require console.log { msg:String -- } dirty
end-module

# host-b.nic
module @host
  require console.log { msg:String level:Int -- } dirty
end-module
```

Pourquoi c’est invalide :
- les deux fragments `@host` déclarent le même chemin de capacité
- leurs signatures ABI divergent

Règle violée :
- dans le contrat consolidé `@host`, un chemin de capacité doit désigner une seule capacité cohérente

### Déclarations divergentes d’une même capacité hôte par effet

```text
# host-a.nic
module @host
  require config.get { key:String -- r:Result<String,MapError> } pure
end-module

# host-b.nic
module @host
  require config.get { key:String -- r:Result<String,MapError> } dirty
end-module
```

Pourquoi c’est invalide :
- les deux fragments `@host` déclarent le même chemin de capacité avec deux effets ABI incompatibles

Règle violée :
- dans le contrat consolidé `@host`, un chemin de capacité doit avoir un seul effet ABI cohérent

### Capacité hôte recevant une quotation

```nicole
module @host
  require callbacks.run-later
    { q:Quote<{ | x:Int -- y:Int }> -- }
    dirty
end-module
```

Pourquoi c’est invalide :
- l’ABI hôte v1 n’autorise pas `Quote<{ ... }>` comme valeur d’entrée d’une capacité hôte

Règle violée :
- les quotations ne franchissent pas l’ABI hôte en v1

### `opaque` hors `module @host`

```nicole
module @app
  opaque io.FileHandle
end-module
```

Pourquoi c’est invalide :
- `opaque` n’est valide que dans `module @host`

Règle violée :
- un type opaque hôte source-visible se déclare uniquement dans le contrat consolidé `@host`

### `type opaque`

```nicole
module @host
  type opaque io.FileHandle
end-module
```

Pourquoi c’est invalide :
- `type opaque` n’appartient pas à la syntaxe Nicole validée
- un type opaque hôte se déclare avec la forme `opaque path`

Règle violée :
- les types opaques hôte source-visibles utilisent la forme `opaque io.FileHandle`

### Déclaration source `external type`

```nicole
module @invalid.phase6

  external type FileHandle

end-module
```

Pourquoi c’est invalide :
- `external type` n’appartient pas à la syntaxe validée

Règle violée :
- le contrat hôte est décrit conceptuellement dans `HOST_ABI.md`, pas avec une déclaration source `external type`

### Construction directe d’une valeur opaque hôte

```nicole
module @host
  opaque io.FileHandle
end-module

module @invalid.phase6
  import @host.io.FileHandle as io.FileHandle

  : make-file { -- }
    io.FileHandle
  ;

end-module
```

Pourquoi c’est invalide :
- `io.FileHandle` désigne ici un symbole de type importé, pas un constructeur ni une expression appelable
- une valeur opaque hôte ne peut être produite que par une capacité hôte déclarée

Règle violée :
- un type opaque hôte importé n’est valide qu’en position de type ou de signature

### Accès à un champ d’une valeur opaque hôte

```nicole
module @host
  opaque io.FileHandle
end-module

module @invalid.phase6
  import @host.io.FileHandle as io.FileHandle

  : file-path { file:io.FileHandle -- path:String }
    file.path
  ;

end-module
```

Pourquoi c’est invalide :
- une valeur opaque hôte n’expose aucun champ structurel au langage

Règle violée :
- Nicole ne définit aucun accès aux champs d’un type opaque hôte

### Égalité générique sur valeur opaque hôte

```nicole
module @host
  opaque io.FileHandle
end-module

module @invalid.phase6
  import @host.io.FileHandle as io.FileHandle

  : same-file { a:io.FileHandle b:io.FileHandle -- ok:Bool }
    a b =
  ;

end-module
```

Pourquoi c’est invalide :
- la v1 n’attribue pas d’égalité générique aux types opaques hôte

Règle violée :
- `=` et `!=` ne s’appliquent pas aux valeurs de type opaque hôte `@host.*`

### Clé de map en type opaque hôte

```nicole
module @host
  opaque io.FileHandle
end-module

module @invalid.phase6
  import @host.io.FileHandle as io.FileHandle

  : bad-map { -- m:Map<io.FileHandle,String> }
    map.empty:Map<io.FileHandle,String>
  ;

end-module
```

Pourquoi c’est invalide :
- une clé de map v1 doit rester `Int`, `String` ou `Bool`

Règle violée :
- un type opaque hôte `@host.*` peut être une valeur de map, jamais une clé de map en v1

### Type opaque hôte non déclaré dans une signature ABI-visible

```nicole
module @host
  require io.close-file
    { file:@host.io.FileHandle -- }
    dirty
end-module
```

Pourquoi c’est invalide :
- le contrat utilise `@host.io.FileHandle` dans une signature visible à l’ABI sans déclarer `opaque io.FileHandle`

Règle violée :
- tout type opaque hôte utilisé dans une signature ABI-visible doit être déclaré explicitement par le contrat hôte

### Conflit de catégorie pour un symbole `@host`

```nicole
module @host
  opaque io.FileHandle
  require io.FileHandle { -- } dirty
end-module
```

Pourquoi c’est invalide :
- le même nom canonique `@host.io.FileHandle` ne peut pas désigner à la fois un type opaque hôte et une capacité hôte

Règle violée :
- chaque symbole du contrat consolidé `@host` possède une seule catégorie

### Alias de type opaque hôte

```nicole
module @invalid.phase6

  type alias FH = @host.io.FileHandle

end-module
```

Pourquoi c’est invalide :
- la v1 ne définit aucun mécanisme d’alias pour les types opaques hôte

Règle violée :
- les aliases de types opaques hôte sont différés à un RFC ultérieur

### Capacité hôte utilisée comme nom de type

```nicole
module @host
  require console.log { msg:String -- } dirty
end-module

module @app
  import @host.console.log as console.log

  : bad { x:console.log -- }
    x drop
  ;
end-module
```

Pourquoi c’est invalide :
- `console.log` désigne ici une capacité hôte importée
- une capacité hôte importée est un symbole appelable/valeur, pas un symbole de type

Règle violée :
- une capacité hôte importée ne peut pas être utilisée comme nom de type

### Mot hôte retournant une quotation

```nicole
module @host
  require callbacks.make-callback
    { -- q:Quote<{ | x:Int -- y:Int }> }
    dirty
end-module
```

Pourquoi c’est invalide :
- l’ABI hôte v1 n’autorise pas `Quote<{ ... }>` comme valeur de retour d’une capacité hôte

Règle violée :
- les quotations ne franchissent pas l’ABI hôte en v1

### Export recevant une quotation

```nicole
module @app
  : accept-callback { q:Quote<{ | x:Int -- y:Int }> -- }
    q drop
  ;
  export : accept-callback
end-module
```

Pourquoi c’est invalide :
- un mot exporté expose ici une quotation à la frontière hôte

Règle violée :
- les quotations ne franchissent pas l’ABI hôte en v1

### Export retournant une quotation

```nicole
module @app
  : make-callback { -- q:Quote<{ | x:Int -- y:Int }> }
    :[ | x:Int -- y:Int | x 1 + ;]
  ;
  export : make-callback
end-module
```

Pourquoi c’est invalide :
- un mot exporté expose ici une quotation en sortie à la frontière hôte

Règle violée :
- les quotations ne franchissent pas l’ABI hôte en v1

### Export avec corps incompatible avec sa signature

```nicole
module @app
  : bad { -- n:Int }
  ;
  export : bad
end-module
```

Pourquoi c’est invalide :
- le mot exporté annonce une sortie `Int`
- son corps ne produit aucune valeur

Règle violée :
- un mot exporté reste un mot Nicole normal
- son corps doit respecter exactement sa signature avant l’exécution

---

## 8. Collisions de noms visibles

Note de transition (phase 2) :
- les cas legacy qui impliquent encore des mots utilisateur top-level sont désormais masqués par l’interdiction des définitions top-level
- ils sont conservés temporairement comme repères de migration

### Deux mots de même nom avec types différents dans un même module

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

Pourquoi c’est invalide :
- les deux définitions `id` sont visibles dans le même module
- un même nom visible ne peut désigner qu’un seul mot

Règle violée :
- deux mots visibles de même nom sont interdits, quelles que soient leurs signatures

### Deux mots de même nom avec arités différentes dans un même module

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

Pourquoi c’est invalide :
- les deux définitions `foo` sont visibles dans le même module
- la différence d’arité ne crée pas de surcharge en v1

Règle violée :
- deux mots visibles de même nom sont interdits, même si leurs arités diffèrent

### Deux sous-mots frères de même nom

```nicole
module @invalid.phase6

  : parent { -- }
  
    : child { -- n:Int }
      1
    ;
  
    : child { -- text:String }
      "x"
    ;
  ;

end-module
```

Pourquoi c’est invalide :
- les deux sous-mots appartiennent au même parent
- dans ce scope local, `child` est un seul nom visible

Règle violée :
- dans un même parent, deux sous-mots ne peuvent pas partager le même nom

### `export` vers un mot absent du module

```nicole
module @app
  : run { -- code:Int }
    0
  ;
  export : missing
end-module
```

Pourquoi c’est invalide :
- `missing` n’existe pas dans `@app`
- `export : word` doit référencer un mot existant du module définissant

Règle violée :
- `export : word` doit viser un mot déjà défini dans le même module

### `export` hors module

```nicole
export : run
```

Pourquoi c’est invalide :
- une déclaration `export` n’est valide qu’à l’intérieur d’un module

Règle violée :
- le placement de `export` hors module est interdit

### Déclaration `export` dupliquée

```nicole
module @app
  : run { -- code:Int }
    0
  ;
  export : run
  export : run
end-module
```

Pourquoi c’est invalide :
- les deux déclarations produisent le même nom canonique visible hôte `@app.run`

Règle violée :
- un nom canonique visible hôte doit désigner un seul mot exporté
- une déclaration `export` dupliquée est invalide

### Collision legacy entre sous-mot et mot top-level (supprimée)

Ce cas legacy dépendait d’une coexistence avec définition utilisateur top-level.

Sous le baseline modules obligatoires :
- les définitions utilisateur top-level sont rejetées avant cette ancienne collision
- cette classe n’est plus maintenue comme invalid autonome

Décision Phase 6 :
- cas retiré du corpus d’invalides actifs
- ne pas réintroduire tant qu’une règle module-contenue équivalente n’est pas définie

### `export` sur un sous-mot

```nicole
module @app
  : parent { -- }
    : child { -- n:Int }
      1
    ;
    export : child
  ;
end-module
```

Pourquoi c’est invalide :
- `child` est un sous-mot exécutable et non un mot du scope module
- `export` ne s’applique qu’à un mot défini au niveau module

Règle violée :
- `export` sur un sous-mot exécutable reste invalide/non supporté en v1

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

### `extern type`

```nicole
extern type @host.io.FileHandle
```

Pourquoi c’est invalide :
- `extern type` n’appartient pas à la syntaxe validée

Règle violée :
- le contrat hôte est décrit conceptuellement dans `HOST_ABI.md`, pas avec `extern type`

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

### Littéral signé avec `+`

```nicole
module @invalid.syntax
  : bad-plus-int { -- n:Int }
    +5
  ;
end-module
```

Pourquoi c’est invalide :
- `+5` n’est pas un littéral numérique valide en v1
- la v1 ne définit pas de préfixe `+` pour les littéraux numériques

Règle violée :
- les littéraux numériques v1 autorisent seulement un signe `-` collé

### Littéral flottant sans chiffre avant le point

```nicole
module @invalid.syntax
  : bad-short-float { -- x:Float }
    -.5
  ;
end-module
```

Pourquoi c’est invalide :
- `-.5` n’est pas un littéral numérique valide en v1
- cette forme ne satisfait pas la grammaire des flottants

Règle violée :
- un littéral `Float` v1 requiert des chiffres avant et après le point

### Littéral flottant sans chiffre après le point

```nicole
module @invalid.syntax
  : bad-trailing-dot { -- x:Float }
    5.
  ;
end-module
```

Pourquoi c’est invalide :
- `5.` n’est pas un littéral numérique valide en v1
- cette forme ne satisfait pas la grammaire des flottants

Règle violée :
- un littéral `Float` v1 requiert des chiffres avant et après le point

### Tentative de littéral signé non collé

```nicole
module @invalid.syntax
  : bad-spaced-negative { -- n:Int }
    - 5
  ;
end-module
```

Pourquoi c’est invalide :
- `- 5` n’est pas un littéral numérique signé collé
- cette écriture produit deux tokens séparés, pas un littéral `Int`
- dans ce contexte, `-` reste l’opérateur binaire et le mot échoue faute d’opérandes suffisants

Règle violée :
- un littéral numérique négatif v1 doit être écrit de manière collée, par exemple `-5`

---

## 10. Pureté et effet `dirty` invalides (v0.14.0)

```text
module @host
  require console.log { msg:String -- } dirty
end-module
```

### Annotation `dirty` manquante sur appel hôte dirty

```nicole
module @host
  require console.log { msg:String -- } dirty
end-module

module @invalid.phase6
  import @host.console.log as console.log

  : bad-pure-host-call { -- }
    "hello" console.log
  ;

end-module
```

Pourquoi c’est invalide :
- `console.log` importe une capacité hôte déclarée `dirty`
- le mot est inféré dirty mais n’est pas annoté `dirty`

Règle violée :
- inféré dirty + annotation absente => erreur statique

### Mot pur appelant un mot Nicole dirty

```nicole
module @host
  require console.log { msg:String -- } dirty
end-module

module @invalid.phase6
  import @host.console.log as console.log

  dirty : log-message { msg:String -- }
    msg console.log
  ;
  
  : bad-pure-calls-dirty { -- }
    "hello" log-message
  ;

end-module
```

Pourquoi c’est invalide :
- `bad-pure-calls-dirty` appelle un mot dirty
- il devrait être annoté `dirty`

Règle violée :
- un mot pur ne peut pas appeler du code dirty

### Export pur appelant du code dirty

```nicole
module @host
  require console.log { msg:String -- } dirty
end-module

module @app
  import @host.console.log as console.log

  : bad-pure-export { -- code:Int }
    "start" console.log
    0
  ;
  export : bad-pure-export
end-module
```

Pourquoi c’est invalide :
- le mot exporté est inféré dirty
- l’annotation `dirty` est absente

Règle violée :
- un mot pur ne peut pas appeler du code dirty
- inféré dirty + annotation absente => erreur statique

### Annotation `dirty` redondante

```nicole
module @invalid.phase6

  dirty : bad-redundant-dirty { -- n:Int }
    1
  ;

end-module
```

Pourquoi c’est invalide :
- le corps est inféré pur
- l’annotation dirty ne correspond pas à l’effet inféré

Règle violée :
- inféré pur + annoté dirty => erreur statique

### Ordre invalide des modificateurs

```nicole
module @invalid.phase6

  dirty export : bad-order-a { -- }
  ;

end-module
```

```nicole
module @invalid.phase6

  dirty pub : bad-order-b { -- }
  ;

end-module
```

```nicole
module @invalid.phase6

  : dirty bad-order-c { -- }
  ;

end-module
```

Pourquoi c’est invalide :
- l’ordre normatif est visibilité puis `dirty` puis définition

Règle violée :
- `dirty export :` et `dirty pub :` sont interdits en v1
- la forme `: dirty foo` est interdite en v1

### Définition d’un mot nommé `dirty`

```nicole
module @invalid.phase6

  : dirty { -- }
  ;

end-module
```

Pourquoi c’est invalide :
- `dirty` est réservé comme identifiant exact

Règle violée :
- un mot utilisateur ne peut pas s’appeler `dirty`

### Utilisation de `dirty` comme local

```nicole
module @invalid.phase6

  : bad-dirty-local { dirty:Int -- x:Int }
    dirty
  ;

end-module
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
module @host
  require console.log { msg:String -- } dirty
end-module

module @invalid.phase6
  import @host.console.log as console.log

  : bad-construct-dirty-quote { -- q:DirtyQuote<{ | x:Int -- y:Int }> }
    :[ | x:Int -- y:Int |
      "item" console.log
      x
    ;]
  ;

end-module
```

Pourquoi c’est invalide :
- la quotation est dirty car elle appelle `console.log`
- la frame de construction est pure

Règle violée :
- une frame pure ne peut pas construire de `DirtyQuote`

### Appel d’un `DirtyQuote` dans une frame pure

```nicole
module @invalid.phase6

  : bad-call-dirty-quote { x:Int q:DirtyQuote<{ | n:Int -- m:Int }> -- y:Int }
    x q call
  ;

end-module
```

Pourquoi c’est invalide :
- `call` sur `DirtyQuote` rend l’appel dirty
- la frame appelante est pure

Règle violée :
- une frame pure ne peut pas appeler un `DirtyQuote`

### Passage d’un `DirtyQuote` à `list.map` dans une frame pure

```nicole
module @invalid.phase6

  : bad-map-dirty-quote {
    xs:List<Int>
    q:DirtyQuote<{ | x:Int -- y:Int }>
    -- ys:List<Int>
  }
    xs q list.map
  ;

end-module
```

Pourquoi c’est invalide :
- l’appel higher-order devient dirty avec une quotation dirty
- la frame appelante est pure

Règle violée :
- une frame pure ne peut pas passer un `DirtyQuote` à `list.map`
