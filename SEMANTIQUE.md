# SEMANTIQUE.md

# Sémantique officielle provisoire du langage Nicole

Ce document formalise le comportement du langage.

La syntaxe de surface est définie et gelée dans `SYNTAXE.md`.
Ce fichier ne redéfinit pas la syntaxe.

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

```sorte
: ok { -- x:Int }
  1
;
```

```sorte
: bad { -- x:Int }
  1 2
;
```

Le second exemple est invalide parce que la sortie attendue n’est pas respectée.

## Sorties multiples

Un mot peut produire zéro, une ou plusieurs valeurs.

L’ordre des sorties suit l’ordre de la signature.

La forme `{ -- }` ne produit aucune valeur.

La forme `{ -- a:Int b:String }` pousse d’abord `a`, puis `b`, de sorte que `b` soit au sommet de la pile appelante après retour.

Exemple :

```sorte
: pair { -- a:Int b:String }
  1 "ok"
;
```

Après appel, la pile appelante reçoit :

```sorte
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

```sorte
: square { x:Int -- y:Int }
  x x *
;
```

Ici, `x` ne modifie rien.

Il lit la valeur locale `x` et la pousse sur la pile locale.

Règles :

- les variables locales sont en lecture seule
- elles ne peuvent pas être mutées
- elles n’existent que dans le mot courant
- elles ne sont pas visibles dans les sous-mots

---

# 3. Résolution des appels

La résolution des appels est statique.

Un mot est résolu par :

- son nom
- son arité
- les types de ses entrées

La sortie ne participe pas à la résolution.

Si plusieurs mots sont compatibles avec le même appel, l’ambiguïté est une erreur de compilation.

Exemple :

```sorte
: id { x:Int -- y:Int }
  x
;

: id { x:String -- y:String }
  x
;
```

Ces deux définitions sont valides parce que leurs types d’entrée diffèrent.

Exemple interdit :

```sorte
: foo { x:Int -- y:Int }
  x
;

: foo { x:Int -- y:String }
  "bad"
;
```

L’appel `12 foo` serait ambigu, donc la deuxième définition doit être rejetée.

---

# 4. `if`

`if` consomme un `Bool` au sommet de la pile locale.

Syntaxe de surface :

```sorte
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

La validation est statique quand elle est possible.

Même effet de pile signifie :

- même nombre de valeurs produites
- mêmes types
- même ordre
- même pile préexistante préservée

Cette vérification doit être statique quand les branches sont écrites en Nicole.

Exemple :

```sorte
: abs { x:Int -- y:Int }
  x 0 < if
    0 x -
  else
    x
  end
;
```

Les deux branches laissent la pile locale dans le même état de sortie.

---

# 5. `case`

`case` consomme la valeur à matcher depuis le sommet de la pile locale.

Syntaxe de surface :

```sorte
value case
  pattern => expression
  pattern => expression
  _       => expression
end
```

Sémantique :

- la valeur à matcher est consommée
- les branches sont testées dans l’ordre
- la première branche compatible est exécutée
- `_` match tout ce qui n’a pas été retenu avant
- toutes les branches doivent produire le même effet de pile

Même effet de pile signifie :

- même nombre de valeurs produites
- mêmes types
- même ordre
- même pile préexistante préservée

Cette vérification doit être statique quand les branches sont écrites en Nicole.

Patterns v1 retenus :

- littéraux `Int`
- littéraux `String`
- littéraux `Bool`
- `Ok(v)`
- `Err(e)`
- `MissingKey`
- `OutOfBounds`
- `_`

Pour les types somme fermés comme `Result`, `ListError` et `MapError`, le compilateur doit pouvoir vérifier l’exhaustivité quand c’est possible.

- un `case` exhaustif est valide sans `_`
- un `case` non exhaustif sur un type somme fermé doit être rejeté si l’absence de couverture est prouvable
- pour des valeurs ouvertes comme `Int` ou `String`, l’absence de `_` peut rester une erreur de contrat d’exécution si aucune branche ne matche
- `Bool` peut être vérifié exhaustivement si les deux littéraux `true` et `false` sont couverts ; sinon, l’absence de `_` peut rester une erreur de contrat d’exécution

Pour les motifs imbriqués sur `Result` :

- `Err(MissingKey)` couvre uniquement le cas `Err` contenant exactement `MissingKey`
- `Err(e)` couvre tous les cas `Err`
- `Ok(v)` couvre tous les cas `Ok`
- pour `Result<V,MapError>`, si `MapError` ne contient que `MissingKey`, alors `Ok(v)` et `Err(MissingKey)` suffisent pour l’exhaustivité
- pour `Result<V,E>`, si `E` n’est pas couvert exhaustivement, il faut un motif plus général comme `Err(e)` ou `_`

Exemple :

```sorte
: sign-label { n:Int -- text:String }
  n case
    0 => "zero"
    1 => "one"
    _ => "many"
  end
;
```

---

# 6. Quotations et `call`

Une quotation est une valeur exécutable de première classe.

Elle peut :

- capturer des valeurs au moment de sa construction
- être stockée
- être passée à `list.map`, `list.fold`, `list.reduce`
- être appelée plus tard avec `call`

## Captures

Les captures sont prises au moment de la construction de la quotation.
Elles sont capturées par valeur.
Elles deviennent des données internes immuables de la quotation.

L’ordre des captures suit l’ordre de déclaration.

## `call`

`call` consomme d’abord la quotation placée au sommet de la pile.

La convention de pile est :

```sorte
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

```sorte
[... x:Int, y:Int, quote] call
```

Précisions :

- la quotation est au sommet de pile
- `y` est la valeur immédiatement sous la quotation
- `x` est la valeur plus profonde
- les inputs sont consommés dans l’ordre de la signature

Ensuite, il consomme les inputs attendus par cette quotation depuis la pile courante, selon la même convention de lecture qu’un mot normal.

Enfin, il exécute le corps de la quotation dans sa propre frame et pousse ses outputs sur la pile courante.

Le type-checker vérifie trois moments distincts :

1. à la construction de la quotation, les captures présentes sur la pile doivent correspondre aux captures déclarées ;
2. à l’appel par `call`, les inputs présents sous la quotation doivent correspondre aux inputs déclarés ;
3. au retour de la quotation, le corps doit produire exactement les outputs déclarés.

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

Pour une quotation avec captures :

```sorte
:[ a:Int b:Int | x:Int -- y:Int | x a + b + ]
```

les captures sont prises à la construction depuis une pile de forme :

```sorte
[... a:Int, b:Int]
```

`a` correspond à la valeur la plus profonde du groupe capturé et `b` à la valeur la plus proche du sommet.

Exemples conceptuels :

```sorte
3 :[ | x:Int -- y:Int | x 1 + ] call
```

Résultat conceptuel :

- `4`

```sorte
3 4 :[ a:Int | x:Int -- y:Int | x a + ] call
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

Exemple :

```sorte
: timeout-or-default { cfg:Map<String,Int> -- n:Int }
  cfg "timeout" map.get case
    Ok(v) => v
    Err(MissingKey) => 30
  end
;
```

## `ListError`

`ListError` sert aux erreurs normales des opérations de liste.

V1 retient :

- `OutOfBounds`

Utilisation attendue :

- `list.get`
- `list.set`

## `MapError`

`MapError` sert aux erreurs normales des opérations de map.

V1 retient :

- `MissingKey`

Utilisation attendue :

- `map.get`

## `list.reduce`

`list.reduce` est défini uniquement sur une liste non vide.

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

- ambiguïtés de résolution
- incompatibilité de types d’entrée
- branches de `if` ou `case` qui n’ont pas le même effet de pile
- retour qui ne peut pas satisfaire la signature
- capture non typée dans une quotation
- capture incompatible avec le type annoncé

## Peut rester une erreur d’exécution

- appel d’un mot hôte absent de l’environnement d’exécution
- `list.reduce` sur une liste vide si ce vide n’est pas prouvable statiquement
- autres cas où le type-checker ne peut pas décider, mais où le contrat d’exécution est violé

Exemple :

```sorte
: reduce-safely { xs:List<Int> -- n:Int }
  xs :[ | a:Int b:Int -- c:Int | a b + ] list.reduce
;
```

Si `xs` est prouvée vide à la compilation, l’appel doit être rejeté.
Sinon, une liste vide observée à l’exécution constitue une erreur d’utilisation.
Cette situation constitue une erreur de contrat d’exécution.

---

# 9. Contrat hôte

Deux directions officielles existent :

- `export` : mot défini par le programme et appelable par l’hôte
- `host.*` : mot fourni par l’hôte et appelable depuis le programme

## `export`

`export` expose un mot du programme vers l’hôte.

Le mot exporté reste un mot du programme.

Il peut aussi être appelé dans le programme comme n’importe quel mot visible.

Exemple :

```sorte
export : app.on-message { msg:String -- }
  msg host.log
;
```

## `host.*`

`host.*` désigne des mots fournis par l’hôte.

Le programme peut les appeler, mais ne peut pas les définir.

Exemple :

```sorte
: save-log { msg:String -- }
  msg host.log
;
```

Règles :

- un programme utilisateur ne peut pas définir un mot `host.*`
- si un mot `host.*` est absent alors que le contrat hôte est connu statiquement, c’est une erreur d’intégration détectable avant exécution
- si l’environnement hôte est dynamique et que le binding disparaît ou manque à l’exécution, c’est une erreur d’intégration à l’exécution
- dans les deux cas, l’absence du mot est une erreur de contrat d’exécution observée à la frontière hôte
- `Result` ne s’applique qu’au contrat de retour d’un mot `host.*` qui existe effectivement
- le mécanisme de liaison lui-même n’est jamais modélisé comme un `Result`
- la résolution statique traite `host.*` comme des mots connus, avec signatures connues

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

## Surcharge des sous-mots locaux

POINT OUVERT :
la surcharge des sous-mots locaux reste à spécifier.

Deux options sont possibles :

1. appliquer les mêmes règles que pour les mots normaux ;
2. interdire la surcharge locale en v1 pour simplifier la résolution.

Tant que ce point n’est pas décidé, les exemples normatifs doivent éviter les sous-mots locaux surchargés.
