# SYNTAXE.md

# Syntaxe officielle provisoire du langage

Ce document fixe la syntaxe de surface à utiliser pour rédiger la spécification et le manuel de référence du langage.

Il ne faut pas proposer une autre syntaxe sauf demande explicite.

Le langage est concaténatif, typé, à signatures obligatoires, avec stack frames isolées et variables locales immuables.

Il est conçu pour être embarqué dans un hôte qui fournit l’exécution, les entrées/sorties et les services externes.

La cible conceptuelle de la v1 est le bytecode.

Un JIT peut exister plus tard comme optimisation d’exécution, mais il ne fait pas partie du langage lui-même.

Le langage n’est pas un Forth pur :

- les corps sont concaténatifs
- les entrées nommées de signature deviennent des variables locales immuables
- lire une variable locale pousse sa valeur sur la pile locale courante

---

# 1. Forme générale d’un mot

Un mot se définit avec `:` et se termine par `;`.

```sorte
: add { a:Int b:Int -- result:Int }
  a b +
;
```

La signature est toujours écrite entre `{` et `}`.

La séparation entre entrées et sorties est toujours `--`.

Les noms d’entrée créent des variables locales immuables.

Les noms de sortie sont documentaires : ils décrivent les valeurs produites, mais ne créent pas de variables.

---

# 2. Visibilité interne, export et contrats hôte

Sans modificateur, un mot est privé au module courant.
En v1, un module peut être compris comme une unité de compilation.

`pub` rend un mot visible dans le programme.

`export` rend un mot visible à l’hôte et implique `pub`.
Tout mot exporté est appelable par l’hôte.

Règle :

```text
sans modificateur = privé
pub = visibilité interne au programme
export = visibilité hôte + visibilité interne
```

Exemples :

```sorte
: helper { x:Int -- y:Int }
  x 1 +
;

pub : shared-helper { x:Int -- y:Int }
  x 1 +
;

export : entry { args:List<String> -- code:Int }
  0
;
```

`export` ne remplace pas `host.*` :

- `export` concerne les mots écrits par le programme
- `host.*` désigne les mots fournis par l’hôte
- le programme appelle l’hôte via `host.*`
- l’hôte appelle le programme via `export`

---

# 3. Nature concaténative

Le langage est concaténatif dans les corps, mais les entrées de signature deviennent des variables locales immuables.

Lire une variable locale pousse sa valeur sur la pile locale courante.

Exemple :

```sorte
: square { x:Int -- y:Int }
  x x *
;
```

Ici, `x` ne désigne pas une variable mutable.  
`x` lit la valeur locale `x` et la pousse sur la pile locale.

---

# 4. Variables locales immuables

Les arguments d’entrée deviennent des variables locales.

```sorte
: square { x:Int -- y:Int }
  x x *
;
```

Les variables locales :

- sont immuables
- sont en lecture seule
- n’existent que dans le mot courant
- ne sont pas visibles dans les sous-mots

---

# 5. Stack frame isolée et règle de retour

Chaque mot s’exécute dans une frame isolée.

À l’appel :

```text
1. les arguments sont pris depuis la pile appelante
2. ils deviennent des variables locales
3. la pile locale du mot commence vide
4. le corps du mot s’exécute
5. les valeurs de sortie sont repoussées sur la pile appelante
```

Au point de retour, la pile locale doit contenir exactement les valeurs de sortie déclarées, dans le bon ordre et avec les bons types.

Règles :

- valeur manquante : erreur de compilation
- valeur supplémentaire : erreur de compilation
- type incompatible : erreur de compilation
- toute valeur ignorée doit être supprimée explicitement avec `drop`

Exemple valide :

```sorte
: ok { -- x:Int }
  1
;
```

Exemple invalide :

```sorte
: bad { -- x:Int }
  1 2
;
```

Ce dernier exemple doit être rejeté, pas corrigé silencieusement en gardant seulement `2`.

Exemple de valeur ignorée explicitement :

```sorte
: ignore { n:Int -- }
  n drop
;
```

Appel conceptuel :

```sorte
100 3 4 compute
```

Avec :

```sorte
: compute { a:Int b:Int -- result:Int }
  a b + 2 *
;
```

Après appel :

```text
pile appelante avant : [100, 3, 4]
arguments consommés  : 3, 4
frame locale         : a=3, b=4, pile=[]
résultat             : 14
pile appelante après : [100, 14]
```

Le mot `compute` ne peut pas accéder au `100`.

---

# 6. Sous-mots

Un mot peut contenir des sous-mots.

Les sous-mots sont privés par défaut.

Ils peuvent être appelés par nom court depuis leur parent, mais ne sont pas visibles depuis l’extérieur en v1.

Le compilateur peut utiliser un nom qualifié interne comme `invoice.subtotal`, mais ce nom n’implique pas une API publique.

Exemple :

```sorte
: invoice { price:Int qty:Int -- total:Int }

  : subtotal { price:Int qty:Int -- amount:Int }
    price qty *
  ;

  : vat { amount:Int -- tax:Int }
    amount 20 * 100 div
  ;

  price qty subtotal
  dup vat
  +
;
```

Le parent reste un mot exécutable.

Le sous-mot `subtotal` est appelable depuis `invoice` par son nom court, mais `invoice.subtotal` ne fait pas partie de l’API publique v1.

---

# 7. Appel des sous-mots

Depuis l’intérieur du parent, les sous-mots sont appelés par leur nom court.

```sorte
price qty subtotal
dup vat
```

Depuis l’extérieur, ils ne sont pas visibles comme API publique en v1.

Exemple non retenu comme API publique v1 :

```sorte
12 3 invoice.subtotal
```

Le compilateur peut néanmoins utiliser un nom qualifié interne à des fins de diagnostic ou d’organisation.

---

# 8. Pas de capture lexicale

Un sous-mot ne voit pas les variables du parent.

Interdit :

```sorte
: outer { a:Int -- result:Int }

  : add-a { x:Int -- y:Int }
    x a +      # erreur : a n’existe pas dans add-a
  ;

  10 add-a
;
```

Chaque mot, parent ou enfant, possède sa propre frame isolée.

---

# 9. Surcharge statique

Plusieurs mots peuvent avoir le même nom si leurs signatures d’entrée sont différentes.

```sorte
: id { x:Int -- y:Int }
  x
;

: id { x:String -- y:String }
  x
;
```

La résolution se fait par :

```text
nom + nombre d’arguments + types d’entrée
```

La sortie ne participe pas à la résolution.

Interdit :

```sorte
: foo { x:Int -- y:Int }
  x
;

: foo { x:Int -- y:String }
  "bad"
;
```

Car l’appel suivant serait ambigu :

```sorte
12 foo
```

---

# 10. Point d’entrée hôte

En mode embarqué, l’hôte choisit quel mot exporté sert de point d’entrée.

Exemple de convention d’intégration :

```sorte
export : entry { args:List<String> -- code:Int }
  0
;
```

`args` contient les données d’entrée fournies par l’hôte.

`code` est la valeur de retour transmise par l’hôte.

Le langage ne définit pas d’exécution autonome hors hôte.

Si l’hôte expose une interface textuelle de lancement, elle n’est qu’un profil d’intégration au-dessus du moteur embarqué.

Convention d’hôte :

```text
0 = succès
non-zéro = erreur
```

`entry` n’est qu’un exemple de mot exporté.
Le langage n’impose aucun nom spécial comme point d’entrée.
L’hôte peut choisir n’importe quel mot exporté compatible avec sa convention d’intégration.

---

# 11. Mots fournis par l’hôte

Deux directions coexistent :

- `export` : mot défini par le programme, appelable par l’hôte
- `host.*` : mot fourni par l’hôte, appelable par le programme

Tout mot dont le nom commence par `host.` est réservé à l’hôte.

```sorte
host.log { msg:String -- }
host.time { -- seconds:Float }
```

Ces mots ne sont pas définis dans le code source du programme.

Le langage connaît leur signature via le contrat d’intégration de l’hôte.

Leur corps est fourni par l’hôte, hors du langage source.

Règles :

- un programme utilisateur ne peut pas définir un mot `host.*`
- un mot `host.*` absent de l’environnement d’exécution produit une erreur d’intégration
- la résolution statique traite `host.*` comme des mots du même espace nominal, avec signatures connues

Exemple conceptuel futur :

```sorte
# extension future possible
# host.file.open { path:String -- r:Result<Handle<File>,HostError> }
```

POINT OUVERT : `host.file.open` suppose encore des types hôte futurs comme `Handle<T>`, `HostError` et un type hôte `File`.

---

# 12. `if`

`if` consomme un `Bool` au sommet de la pile locale.

Syntaxe retenue :

```sorte
condition if
  ...
else
  ...
end
```

Règle de typage :

- les deux branches doivent transformer la pile de la même manière

En notation de pile :

```text
avant if : S Bool
then     : S produit S'
else     : S produit S'
après if : S'
```

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

---

# 13. `case`

`case` consomme la valeur à matcher depuis le sommet de la pile locale.

Syntaxe retenue :

```sorte
value case
  pattern => expression
  pattern => expression
  _       => expression
end
```

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

Toutes les branches doivent produire le même nombre de valeurs et les mêmes types.

Patterns v1 :

```text
littéraux Int
littéraux String
littéraux Bool
Ok(v)
Err(e)
MissingKey
OutOfBounds
_
```

Le pattern matching avancé est hors v1.

---

# 14. Récursion

La récursion est autorisée.

```sorte
: fact { n:Int -- result:Int }
  n case
    0 => 1
    _ => n n 1 - fact *
  end
;
```

La récursion mutuelle est possible si les signatures sont connues avant analyse.

La profondeur d’appel doit pouvoir être bornée par l’environnement d’exécution, mais ce point relève de l’intégration hôte, pas de la syntaxe.

---

# 15. Types v1

Types du langage v1 :

```text
Int
Float
Bool
String
List<T>
Map<K,V>
ListError
MapError
Result<V,E>
Quote<{ captures | inputs -- outputs }>
Unit
```

Dans `Quote<{ captures | inputs -- outputs }>`, les mots `captures`, `inputs` et `outputs` sont des placeholders descriptifs. Les types concrets doivent utiliser des entrées et sorties nommées, par exemple `Quote<{ | x:Int -- y:Int }>` ou `Quote<{ a:Int | x:Int -- y:Int }>` .

Extensions possibles plus tard :

```text
Bytes
Handle<T>
HostError
File
```

Ne pas introduire de `Table` en v1.

Le type `Quote` doit toujours être écrit avec une forme typée et nommée.  
La barre `|` est obligatoire dans la forme canonique.
Les formes anonymes de quotations ne sont pas canoniques en v1.

Exemples canoniques :

```text
Quote<{ | x:Int -- y:Int }>
Quote<{ a:Int | x:Int -- y:Int }>
Quote<{ | acc:Acc x:T -- out:Acc }>
```

---

# 16. `Unit` et absence de sortie

`{ -- }` signifie qu’aucune valeur n’est produite.

`Unit` est une vraie valeur du langage.

Ces deux notions ne doivent pas être confondues.

Exemples :

```sorte
: log-only { msg:String -- }
  msg host.log
;
```

`log-only` ne produit aucune valeur.

Si le littéral ou mot `unit` est retenu, il produirait une valeur de type `Unit`.

POINT OUVERT : le littéral `unit` n’est pas encore définitivement fixé en v1.

---

# 17. Primitives de pile

Primitives prévues :

```text
dup
drop
swap
over
rot
```

Elles opèrent sur la pile locale du mot courant.

Exemple :

```sorte
: between { x:Int min:Int max:Int -- ok:Bool }
  x min >=
  x max <=
  and
;
```

`drop` est la primitive à utiliser quand une valeur doit être explicitement ignorée avant le retour.

---

# 18. Arithmétique, comparaison, booléens

Opérations arithmétiques et booléennes prévues :

```text
+   # addition
-   # soustraction
*   # multiplication
div # division entière
/   # division flottante
mod # modulo entier
<
<=
>
>=
=
!=
and
or
not
```

Règles :

- `div` produit une division entière
- `/` produit une division flottante
- les comparateurs produisent un `Bool`

Exemples :

```sorte
7 2 div
```

produit `3`.

```sorte
7.0 2.0 /
```

produit `3.5`.

Exemple de TVA :

```sorte
: vat { amount:Int -- tax:Int }
  amount 20 * 100 div
;
```

---

# 19. Collections v1

Les listes sont immuables.

`[]` est polymorphe.
Son type `List<T>` doit être déduit depuis un contexte explicite.

Littéraux de liste :

```sorte
[]
[1]
[1, 2, 3]
["a", "b"]
[1, [2, 3]]
```

Règles :

- `[]` désigne la liste vide
- les listes sont typées par contexte
- la notation `,` sépare les éléments dans un littéral
- les listes peuvent être imbriquées

Exemples valides :

```sorte
: empty-names { -- xs:List<String> }
  []
;
```

```sorte
: empty-ints { -- xs:List<Int> }
  []
;
```

Exemple ambigu à rejeter :

```sorte
: ambiguous-empty { -- }
  []
;
```

car la liste vide reste sur la pile alors que la signature ne déclare aucune sortie.

Opérations canoniques v1 :

```text
list.len
list.get
list.set
list.concat
list.map
list.fold
list.reduce
```

Notes :

- `++` peut rester comme sucre futur, mais n’est pas la forme canonique v1
- les signatures ci-dessous sont écrites dans l’ordre d’appel naturel du langage, avec la valeur principale avant l’opérateur

Signatures conceptuelles :

```text
list.len    { xs:List<T> -- n:Int }
list.get    { xs:List<T> index:Int -- r:Result<T,ListError> }
list.set    { xs:List<T> index:Int value:T -- r:Result<List<T>,ListError> }
list.concat { xs:List<T> ys:List<T> -- zs:List<T> }
list.map    { xs:List<T> q:Quote<{ | x:T -- y:U }> -- ys:List<U> }
list.fold   { xs:List<T> init:Acc q:Quote<{ | acc:Acc x:T -- out:Acc }> -- out:Acc }
list.reduce { xs:List<T> q:Quote<{ | a:T b:T -- c:T }> -- out:T }
```

Exemples :

```sorte
: first { xs:List<String> -- s:String }
  xs 0 list.get case
    Ok(v) => v
    Err(OutOfBounds) => ""
  end
;
```

```sorte
: replace-first { xs:List<Int> -- ys:List<Int> }
  xs 0 42 list.set case
    Ok(v) => v
    Err(OutOfBounds) => xs
  end
;
```

```sorte
: concat-singletons { -- xs:List<Int> }
  [2] [4] list.concat
;
```

```sorte
: inc-all { xs:List<Int> -- ys:List<Int> }
  xs :[ | x:Int -- y:Int | x 1 + ] list.map
;
```

```sorte
: sum { xs:List<Int> -- total:Int }
  xs 0 :[ | acc:Int x:Int -- out:Int | acc x + ] list.fold
;
```

```sorte
: sum-nonempty { xs:List<Int> -- total:Int }
  xs :[ | a:Int b:Int -- c:Int | a b + ] list.reduce
;
```

`list.reduce` est uniquement défini pour une liste non vide.

Une liste vide doit être rejetée statiquement lorsqu’elle est prouvable, sinon elle constitue une erreur d’utilisation à l’exécution.

---

# 20. ListError v1

`ListError` est le type d’erreur dédié aux opérations sur les listes.

Variantes v1 :

```text
OutOfBounds
```

Règles :

- `OutOfBounds` représente un index hors limites pour `list.get` ou `list.set`
- `ListError` est un type somme fermé en v1
- `list.get` et `list.set` renvoient un `Result<...,ListError>`
- `case` peut matcher `Err(OutOfBounds)` directement

Exemple :

```sorte
: first-or-empty { xs:List<String> -- s:String }
  xs 0 list.get case
    Ok(v) => v
    Err(OutOfBounds) => ""
  end
;
```

---

# 21. Maps v1

`Map<K,V>` est une collection associative immuable.

`map.empty` est polymorphe.
Son type `Map<K,V>` doit être déduit depuis un contexte explicite.

Règles :

- les clés v1 sont `Int`, `String` ou `Bool`
- `Float` n’est pas autorisé comme clé en v1
- `Handle<T>` peut être ajouté plus tard si l’égalité par identité est retenue
- les valeurs peuvent être de n’importe quel type supporté, y compris `Quote`, `List<T>` et `Map<K,V>`
- toute opération de mise à jour retourne une nouvelle map

Opérations prévues :

```text
map.empty
map.get
map.contains
map.set
map.remove
map.len
map.keys
map.values
```

Signatures conceptuelles :

```text
map.empty   { -- m:Map<K,V> }
map.get     { m:Map<K,V> k:K -- r:Result<V,MapError> }
map.contains{ m:Map<K,V> k:K -- ok:Bool }
map.set     { m:Map<K,V> k:K v:V -- m2:Map<K,V> }
map.remove  { m:Map<K,V> k:K -- m2:Map<K,V> }
map.len     { m:Map<K,V> -- n:Int }
map.keys    { m:Map<K,V> -- ks:List<K> }
map.values  { m:Map<K,V> -- vs:List<V> }
```

Sémantique attendue :

- `map.empty` construit une map vide
- `m k map.get` lit la valeur associée à `k` et renvoie un `Result<V,MapError>`
- `m k map.contains` teste la présence d’une clé
- `m k v map.set` renvoie une nouvelle map avec association mise à jour
- `m k map.remove` renvoie une nouvelle map sans la clé ; si la clé est absente, la map est renvoyée inchangée
- `m map.len` renvoie le nombre d’entrées
- `m map.keys` renvoie la liste des clés
- `m map.values` renvoie la liste des valeurs

Exemples :

```sorte
: empty-cfg { -- cfg:Map<String,Int> }
  map.empty
;
```

```sorte
: cfg-with-timeout { -- cfg:Map<String,Int> }
  map.empty
  "timeout" 30 map.set
;
```

```sorte
: timeout { cfg:Map<String,Int> -- n:Int }
  cfg "timeout" map.get case
    Ok(v) => v
    Err(MissingKey) => 0
  end
;
```

```sorte
: has-timeout { cfg:Map<String,Int> -- ok:Bool }
  cfg "timeout" map.contains
;
```

```sorte
: store-action { -- actions:Map<String,Quote<{ | x:Int -- y:Int }>> }
  map.empty
  "inc" :[ | x:Int -- y:Int | x 1 + ] map.set
;
```

`map.get` doit renvoyer un `Result<V,MapError>`. L’absence de clé est représentée par `Err(MissingKey)` plutôt que par une valeur implicite cachée.

---

# 22. MapError v1

`MapError` est le type d’erreur dédié aux opérations sur `Map<K,V>`.

Variantes v1 :

```text
MissingKey
```

Règles :

- `MissingKey` représente une clé absente dans une map
- `MapError` est un type somme fermé en v1
- `map.get` renvoie `Result<V,MapError>`
- `case` peut matcher `Err(MissingKey)` directement

Exemple :

```sorte
: timeout { cfg:Map<String,Int> -- n:Int }
  cfg "timeout" map.get case
    Ok(v) => v
    Err(MissingKey) => 0
  end
;
```

Cas d’usage recommandé :

- absence de clé dans `Map.get`
- signaux d’erreur explicites et attendus, sans exception implicite

---

# 23. Result v1

`Result<V,E>` est un type somme immuable destiné à représenter une réussite ou un échec explicite.

Variantes :

```text
Ok(V)
Err(E)
```

Règles :

- `Ok(v)` représente un succès avec une valeur de type `V`
- `Err(e)` représente un échec avec une valeur de type `E`
- `Result` ne remplace pas `Unit`, il sert aux opérations qui peuvent échouer de façon normale
- `case` doit pouvoir matcher `Ok(v)` et `Err(e)` directement

Exemples :

```sorte
: parse-timeout { cfg:Map<String,Int> -- r:Result<Int,MapError> }
  cfg "timeout" map.get
;
```

```sorte
: timeout-or-default { cfg:Map<String,Int> -- n:Int }
  cfg "timeout" map.get case
    Ok(v) => v
    Err(MissingKey) => 30
  end
;
```

---

# 24. Quotations et fonctions comme valeurs

Une quotation est une valeur exécutable de première classe.

Type canonique :

```text
Quote<{ captures | inputs -- outputs }>
```

Exemples :

```text
Quote<{ | -- }>
Quote<{ | x:Int -- y:Int }>
Quote<{ a:Int | x:Int -- y:Int }>
Quote<{ | acc:Acc x:T -- out:Acc }>
```

Règles :

- en v1, les types de quotations doivent conserver la barre `|`
- les zones non vides doivent nommer explicitement leurs entrées et sorties
- les captures sont optionnelles
- les inputs et outputs décrivent l’effet de pile de l’exécution future
- les types sont obligatoires
- les noms sont documentaires
- les captures font partie de la valeur de quotation, pas de la pile appelante
- les formes anonymes de quotations ne sont pas canoniques en v1

## Syntaxe

La quotation est terminée par `]`.

Le mot `;` termine un mot.

La forme canonique est :

```sorte
:[ captures | inputs -- outputs | body ]
```

Exemples :

```sorte
:[ | -- | ]
```

```sorte
:[ | x:Int -- y:Int | x 1 + ]
```

```sorte
:[ a:Int | x:Int -- y:Int | x a + ]
```

La forme explicite est la seule forme canonique en v1.

Exemples explicites liés à l’hôte :

```sorte
:[ | msg:String -- | msg host.log ]
```

```sorte
"hello" :[ msg:String | -- | msg host.log ]
```

## Sémantique de construction

Quand une quotation est construite :

- les valeurs de capture sont prises sur la pile courante
- elles sont figées par valeur
- elles deviennent des données internes à la quotation
- le corps n’est pas exécuté à la construction
- la quotation construite est poussée sur la pile

L’ordre des captures suit la même convention que les arguments de mots :

- le premier capture déclarée correspond à la valeur la plus profonde parmi les captures
- la dernière capture déclarée correspond à la valeur au sommet du groupe capturé

Exemple :

```sorte
2 3 :[ x:Int y:Int | -- r:Int | x y + ]
```

signifie :

- `x = 2`
- `y = 3`

## Sémantique de `call`

Convention de pile :

```text
[... input1, input2, quote] call
```

`call` consomme d’abord la quotation au sommet de pile, puis consomme les inputs attendus par cette quotation sous elle, puis pousse les outputs.

Exemple sans capture :

```sorte
3 :[ | x:Int -- y:Int | x 1 + ] call
```

Résultat :

```sorte
4
```

Exemple avec capture :

```sorte
3 4 :[ a:Int | x:Int -- y:Int | x a + ] call
```

Résultat :

```sorte
7
```

Dans cet exemple :

- `a=4` est capturé à la construction
- `x=3` est consommé au moment de `call`

`call` :

- consomme une quotation sur la pile
- exécute son corps
- utilise les captures figées stockées dans la quotation
- consomme les inputs attendus sur la pile courante
- pousse les outputs déclarés sur la pile courante

## Portée

Dans le corps d’une quotation :

- les captures sont visibles comme des variables locales en lecture seule
- les inputs du `call` sont visibles comme des variables locales en lecture seule
- aucune capture par référence implicite n’est autorisée
- aucune mutation des captures n’est autorisée

## Intégration avec `list.map`

Une quotation de transformation pour `list.map` a une forme du genre :

```text
Quote<{ | x:T -- y:U }>
```

Exemple :

```sorte
[1, 2, 3] :[ | x:Int -- y:Int | x 1 + ] list.map
```

Résultat attendu :

```sorte
[2, 3, 4]
```

## Intégration avec `list.fold`

La quotation de `list.fold` a typiquement une forme du genre :

```text
Quote<{ | acc:Acc x:T -- out:Acc }>
```

Exemple conceptuel :

```sorte
[1, 2, 3] 0 :[ | acc:Int x:Int -- out:Int | acc x + ] list.fold
```

## Intégration avec `list.reduce`

La quotation de `list.reduce` a typiquement une forme du genre :

```text
Quote<{ | a:T b:T -- c:T }>
```

Exemple conceptuel :

```sorte
[1, 2, 3] :[ | a:Int b:Int -- c:Int | a b + ] list.reduce
```

## Retour et pile résiduelle

La règle de frame s’applique aussi aux quotations :

- la pile locale d’une quotation doit contenir exactement les sorties déclarées, dans le bon ordre et avec les bons types
- valeur manquante : erreur
- valeur supplémentaire : erreur
- type incompatible : erreur
- toute valeur ignorée doit être supprimée explicitement avec `drop`

Les quotations doivent suivre la même discipline de pile que les mots normaux.

## Exemples invalides

Capture non typée :

```sorte
:[ a | -- r:Int | a 1 + ]
```

Ici, `a` est placé dans la zone des captures, mais aucun type n’est fourni.

Erreur attendue :

- les captures doivent être typées

Valeur de capture incompatible :

```sorte
"hello" :[ a:Int | -- r:Int | a 1 + ] call
```

Erreur attendue :

- la capture attend `Int`
- la pile fournit `String`

## Formulation courte

```text
Une quotation est une valeur de type Quote<{ captures | inputs -- outputs }>.
La barre est obligatoire, même lorsque la zone captures est vide.
Les captures, inputs et outputs sont typés dans la syntaxe de référence.
call consomme une quotation, exécute son corps et applique son effet de pile.
Les captures sont figées par valeur et ne capturent jamais par référence.
```

---

# 25. Boucles

Le langage ne réserve pas de mot-clé unique pour les boucles.

Les boucles éventuelles sont documentées comme des formes de bibliothèque ou des constructions d’intégration.

Tant qu’aucune sémantique canonique n’est fixée, il ne faut pas présenter de syntaxe de boucle comme normative.

---

# 26. Commentaires

Les commentaires de ligne utilisent `#`.

```sorte
: square { x:Int -- y:Int }
  x x *   # pousse x deux fois, puis multiplie
;
```

Les commentaires de bloc ne sont pas définis en v1.

---

# 27. Syntaxe à ne pas utiliser

Ne pas proposer cette syntaxe :

```sorte
pub word add : Int Int -> Int
  +
;
```

Ni :

```sorte
pub const pi : Float = 3.14159
```

Ni :

```sorte
let name = "Ada"
```

Ni une syntaxe basée sur `->` pour les signatures.

La syntaxe canonique provisoire est :

```sorte
: word-name { arg1:Type arg2:Type -- out1:Type }
  arg1 arg2 some-word
;
```

Les variantes de visibilité sont :

```sorte
: private-word { x:Int -- y:Int }
  x
;

pub : internal-word { x:Int -- y:Int }
  x
;

export : app.event { payload:String -- }
  payload host.log
;
```

---

# 28. Exemple complet valide

```sorte
# Contrat hôte supposé :
# host.log { msg:String -- }

: square { x:Int -- y:Int }
  x x *
;

: PI { -- value:Float }
  3.14159
;

: circle-area { r:Float -- area:Float }
  r r * PI *
;

pub : helper { n:Int -- m:Int }
  n 1 +
;

export : app.on-message { msg:String -- }
  msg host.log
;

export : entry { args:List<String> -- code:Int }
  12 square drop
  0
;
```

---

# 29. Résumé de la syntaxe

Mot privé :

```sorte
: private-name { x:Int -- y:Int }
  x 1 +
;
```

Mot public interne :

```sorte
pub : shared-name { x:Int -- y:Int }
  x 1 +
;
```

Mot exporté à l’hôte :

```sorte
export : app.event { payload:String -- }
  payload host.log
;
```

Sous-mot :

```sorte
: parent { x:Int -- y:Int }

  : child { z:Int -- r:Int }
    z z *
  ;

  x child
;
```

Conditionnel :

```sorte
condition if
  ...
else
  ...
end
```

Pattern matching :

```sorte
value case
  pattern => expression
  _ => expression
end
```

Quotation :

```sorte
:[ a:Int | x:Int -- y:Int | x a + ]
```

Appel d’une quotation :

```sorte
[... input, quote] call
```

Listes :

```sorte
xs 0 list.get
xs 0 42 list.set
xs ys list.concat
xs quote list.map
```

Maps :

```sorte
m k map.get
m k v map.set
```

Le langage doit rester explicite, concaténatif, typé, et proche de la syntaxe ci-dessus.

---

# Séparation future des documents

Cette syntaxe de surface gagnera probablement à être séparée plus tard en trois documents :

- `SYNTAXE.md` : syntaxe de surface
- `SEMANTIQUE.md` : typage, piles, frames, `call`, `case`, `if`, quotations
- `HOST_ABI.md` : intégration hôte, `host.*`, événements, exports

Pour l’instant, les informations restent regroupées ici.

# Points ouverts pour la v1

- le littéral concret de `Unit` : `unit` n’est pas encore définitivement fixé
- POINT OUVERT : surcharge des sous-mots locaux, à préciser probablement selon les mêmes règles que les mots normaux
- POINT OUVERT : système de modules, visibilité inter-modules, collisions de noms, imports et résolution restent à spécifier
