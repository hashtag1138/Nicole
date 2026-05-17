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

```sorte
: bad-add { x:Int -- y:Int }
  x "oops" +
;
```

Pourquoi c’est invalide :
- `+` reçoit des opérandes de types incompatibles

Règle violée :
- les entrées d’un mot doivent respecter les types attendus

---

## 2. Mauvais retours

### Valeur supplémentaire au retour

```sorte
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

```sorte
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

```sorte
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

```sorte
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

```sorte
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

---

## 4. Quotations invalides

### Capture non typée

```sorte
:[ a | x:Int -- y:Int | x 1 + ]
```

Pourquoi c’est invalide :
- la capture `a` n’est pas typée

Règle violée :
- les captures d’une quotation doivent être typées

### `call` avec mauvais type d’input

```sorte
: bad-call { s:String -- y:Int }
  s :[ | x:Int -- y:Int | x 1 + ] call
;
```

Pourquoi c’est invalide :
- la quotation attend un input `Int`
- la pile fournit un `String`

Règle violée :
- `call` doit recevoir les inputs déclarés par le type de la quotation

---

## 5. Sous-mots privés

### Appel hors du parent

```sorte
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

```sorte
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

---

## 6. `host.*`

### Mot hôte absent du contrat

```sorte
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

```sorte
: host.log { msg:String -- }
;
```

Pourquoi c’est invalide :
- un programme utilisateur ne peut pas définir un mot `host.*`

Règle violée :
- `host.*` est réservé aux mots fournis par l’hôte

---

## 7. Surcharge

### Deux définitions avec les mêmes entrées

```sorte
: id { x:Int -- y:Int }
  x
;

: id { x:Int -- y:String }
  "bad"
;
```

Pourquoi c’est invalide :
- la résolution ne peut pas distinguer ces deux définitions

Règle violée :
- la sortie ne participe pas à la résolution
- une ambiguïté de résolution doit être rejetée

---

## 8. Syntaxes explicitement interdites

### `let`

```sorte
let name = "Ada"
```

Pourquoi c’est invalide :
- `let` n’appartient pas à la syntaxe validée

Règle violée :
- `SYNTAXE.md` n’introduit pas de liaison locale impérative

### `const`

```sorte
pub const pi : Float = 3.14159
```

Pourquoi c’est invalide :
- `const` n’appartient pas à la syntaxe validée

Règle violée :
- `SYNTAXE.md` n’utilise pas de déclaration `const`

### `extern`

```sorte
extern host.log { msg:String -- }
```

Pourquoi c’est invalide :
- `extern` n’appartient pas à la syntaxe validée

Règle violée :
- le contrat hôte est décrit conceptuellement dans `HOST_ABI.md`, pas avec `extern`

### Signature avec `->`

```sorte
pub word add : Int Int -> Int
  +
;
```

Pourquoi c’est invalide :
- les signatures Nicole utilisent `{ ... -- ... }`
- `->` n’appartient pas à la syntaxe validée

Règle violée :
- `SYNTAXE.md` définit les signatures avec la forme `{ ... -- ... }`
