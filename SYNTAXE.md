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

```nicole
: add { a:Int b:Int -- result:Int }
  a b +
;
```

La signature est toujours écrite entre `{` et `}`.

La séparation entre entrées et sorties est toujours `--`.

Les noms d’entrée créent des variables locales immuables.

Les noms de sortie sont documentaires : ils décrivent les valeurs produites, mais ne créent pas de variables.

## Lexique minimal v1

Identifiants :

- un identifiant commence par une lettre ASCII (`a-z`, `A-Z`) ou `_`
- après le premier caractère, il peut contenir des lettres, des chiffres, `_` et `-`
- `-` peut apparaître dans un identifiant comme `add-one`
- `-` seul reste l’opérateur arithmétique de soustraction
- `.` est un séparateur structurel dans les noms qualifiés, pas un caractère normal d’identifiant
- `.` n’est pas un opérateur autonome en v1
- `@` introduit une référence de module dans les formes grammaticales de modules/imports

Formes lexicales introduites :

- `identifier` : `[a-zA-Z_][a-zA-Z0-9_-]*`
- `qualified_name` : `identifier ("." identifier)*`
- `module_ref` : `@identifier`
- `module_qualified_name` : `@identifier ("." identifier)+`

Chaînes :

- une chaîne est délimitée par `"`
- la chaîne vide `""` est autorisée
- les retours à la ligne bruts dans une chaîne ne sont pas autorisés en v1
- les échappements supportés en v1 sont `\"`, `\\`, `\n` et `\t`

## Formes réservées v1

Les formes suivantes sont réservées par le langage et ne peuvent pas être définies comme mots utilisateur :

- `if`
- `else`
- `end`
- `case`
- `when`
- `pub`
- `export`
- `module`
- `end-module`
- `import`
- `include`
- `dirty`
- `call`
- `?`
- `Ok!`
- `Err!`

Dans `case`, les motifs `Ok(v)` et `Err(e)` sont des formes de pattern de `Result`, pas des noms de mots définissables par l’utilisateur.

Les variantes fermées `MissingKey` et `OutOfBounds` sont réservées en v1 comme variantes d’erreur du langage et ne peuvent pas être redéfinies comme mots utilisateur.

Les racines de namespace suivantes sont réservées, à la fois comme racines et comme formes namespace :

- `host`, `host.*`
- `list`, `list.*`
- `map`, `map.*`
- `result`, `result.*`

Les builtins du langage font partie de l’espace de résolution visible.

Un mot défini par l’utilisateur ne peut donc ni redéfinir ni masquer un nom builtin.

Toute collision entre une définition utilisateur et une forme réservée, une variante réservée ou un nom builtin est une erreur de compilation.

Règles associées :

- un module utilisateur ne peut pas s’appeler `@host`, `@list`, `@map` ou `@result`
- un alias d’import ne peut pas s’appeler `host`, `list`, `map` ou `result`
- un nom utilisateur ne peut pas occuper une racine réservée
- les formes qualifiées builtin existantes (`host.*`, `list.*`, `map.*`, `result.*`) restent valides

`dirty` est réservé comme identifiant exact en v1.

Cette réservation s’applique à :

- noms de mots top-level
- noms de sous-mots
- noms de variables locales d’entrée
- noms de captures de quotations
- labels de sortie de signature

Exemples invalides :

```nicole
: dirty { -- }
  0 drop
;
```

```nicole
: foo { dirty:Int -- x:Int }
  dirty
;
```

```nicole
:[ dirty:Int | x:Int -- y:Int | x ;]
```

Seul l’identifiant exact `dirty` est réservé.

Les identifiants suivants restent autorisés :

- `dirty-int`
- `dirty_log`
- `is-dirty`
- `dirtyvalue`

---

# 2. Visibilité interne, export et contrats hôte

Sans modificateur, un mot défini dans un module est privé à ce module.

Phase 2 établit le modèle obligatoire suivant :

- tous les mots définis par l’utilisateur sont contenus dans un bloc `module @... end-module`
- une définition utilisateur top-level est invalide
- dans un module, la définition d’un mot utilise la syntaxe normale `: word { ... }`
- dans un module, les appels courts vers des mots du même module sont autorisés
- hors module, une référence utilisateur externe exige la forme `@module.word` avec import correspondant
- dans `module @text`, la forme `@text.word` reste autorisée sans import, même si la forme courte locale est préférée

En v1, le programme reste analysé comme une seule unité de compilation.

Les formes `module`, `import` et `include` existent en syntaxe comme fondations grammaticales.
La phase 3 fixe la résolution statique, la visibilité des imports, les aliases, les collisions associées et l’acyclicité du graphe d’import.
La sémantique détaillée de `include` (mapping fichiers/paths) reste différée.

`pub` expose uniquement des chemins qualifiés ; il n’injecte pas de nom court hors du module.

`dirty` est l’annotation d’effet explicite de v1.

Pour les définitions de mots, l’ordre des modificateurs est normatif :

```text
visibilité d’abord, dirty ensuite, définition ensuite
```

Formes valides pour des définitions utilisateur à l’intérieur d’un module :

```nicole
module @demo
  : foo { -- }
  ;
  dirty : foo-dirty { -- }
  ;
  pub : foo-public { -- }
  ;
  pub dirty : foo-public-dirty { -- }
  ;
end-module
```

Déclaration d’export (phase 4) :

```nicole
module @demo
  : run { -- code:Int }
    0
  ;
  export : run
end-module
```

Règles normatives d’export :

- `export : word` est une déclaration uniquement
- `export : word` apparaît dans le module qui définit `word`
- `word` doit déjà exister dans ce même module
- `export` ne définit pas de nouveau mot
- `export` ne crée pas d’alias visible dans le programme
- `export` n’utilise pas les aliases d’import
- `export` ne modifie ni signature, ni pureté, ni récursion, ni typage du mot référencé
- `export` hors module est invalide
- `export` sur un sous-mot exécutable reste invalide en v1

Relation `pub` / `export` :

- `pub` contrôle la visibilité Nicole via chemins qualifiés
- `export` contrôle la visibilité côté hôte
- `export` n’implique jamais de visibilité par nom court
- `export` ne dépend ni des imports, ni des aliases

Noms visibles côté hôte :

- le nom canonique visible hôte est `@module.word`
- le `@` initial est conservé
- le nom est dérivé du module définissant et du mot référencé par `export`
- les aliases d’import n’affectent jamais ce nom canonique
- les noms canoniques visibles hôte doivent être uniques dans le programme
- une duplication de déclaration menant au même nom canonique est invalide

Formes invalides :

```text
dirty pub : foo
dirty export : foo
export dirty : foo
: dirty foo
export : foo { ... }
```

`pub` et `export` ne créent pas d’espace nominal séparé.
Un nom visible doit rester unique dans son espace de résolution.

Règle :

```text
sans modificateur = privé au module
pub = visibilité interne selon les règles de résolution en vigueur
export = déclaration de visibilité hôte du mot du module
```

Exemples :

```nicole
module @demo

  : helper { x:Int -- y:Int }
    x 1 +
  ;

  pub : shared-helper { x:Int -- y:Int }
    x 1 +
  ;

  : caller { x:Int -- y:Int }
    x shared-helper
  ;

  : caller-qualified { x:Int -- y:Int }
    x @demo.shared-helper
  ;

end-module

@demo.shared-helper
```

## Fondations grammaticales modules/imports/includes (Phases 1-3)

Cette section fixe la grammaire minimale (phase 1) et les règles de résolution/imports (phase 3).

Reste différé :

- la sémantique détaillée de `include` (mapping fichiers/paths)
- les conventions de packaging

Forme `module` :

```nicole
module @name
  ...
end-module
```

Formes `import` :

```nicole
import @name
import @name as alias
import @name.word
import @name.word as alias
```

Forme `include` :

```nicole
include "path.nic"
```

Règles normatives d’import :

- les imports existent uniquement au top-level
- les imports n’injectent jamais de noms implicitement
- les wildcard imports n’existent pas en v1
- les aliases créent des noms visibles dans l’unité de compilation importatrice
- les aliases participent aux règles de collision de noms visibles
- la portée des aliases d’import est l’unité de compilation après inclusion textuelle
- un fragment inclus ne crée pas de scope alias séparé

Sémantique des formes d’import :

- `import @text` rend `@text.*` disponible en usage qualifié explicite uniquement pour les mots publics de `@text`
- `import @text as t` crée une racine alias `t`, utilisable sous la forme `t.word`
- `import @text.split` rend uniquement `@text.split` disponible explicitement
- `import @text.split as split` crée l’alias court `split`
- sans alias, `import @text.split` ne rend pas `split` visible
- sans import, une référence externe `@text.word` est invalide

Modèle de résolution statique (phase 3) :

Dans un module, la résolution se fait dans cet ordre :

1. noms locaux dans le scope courant (mot/sous-mot)
2. mots définis dans le même module via nom court
3. aliases d’import visibles
4. noms qualifiés explicites (`@module.word`) autorisés dans le module courant ou via import externe correspondant
5. namespaces réservés/builtins (`host.*`, `list.*`, `map.*`, `result.*`)

Hors module :

- les références utilisateur non qualifiées sont invalides
- une référence utilisateur exige `@module.word` avec import externe correspondant
- un alias ne peut être utilisé que s’il est introduit par un import

Exemple invalide (Phase 2) :

```nicole
: bad-top-level {
  --
}
;
```

Cette définition est invalide :

- les mots définis par l’utilisateur doivent être contenus dans `module @... end-module`
- un mot utilisateur top-level est rejeté en phase 2

Note de transition :

- certains exemples plus loin dans ce document utilisent encore une forme top-level legacy
- en cas de conflit, la règle normative de phase 2 prévaut : les définitions utilisateur sont module-contenues

Cycles d’import :

- les cycles d’import sont interdits
- forme diagnostique autorisée :

```text
cyclic import detected:
@a -> @b -> @a
```

---

# 3. Nature concaténative

Le langage est concaténatif dans les corps, mais les entrées de signature deviennent des variables locales immuables.

Lire une variable locale pousse sa valeur sur la pile locale courante.

Exemple :

```nicole
: square { x:Int -- y:Int }
  x x *
;
```

Ici, `x` ne désigne pas une variable mutable.  
`x` lit la valeur locale `x` et la pousse sur la pile locale.

---

# 4. Variables locales immuables

Les arguments d’entrée deviennent des variables locales.

```nicole
: square { x:Int -- y:Int }
  x x *
;
```

Les variables locales :

- sont immuables
- sont en lecture seule
- n’existent que dans le mot courant
- ne sont pas visibles dans les sous-mots

Les noms locaux doivent être uniques dans une même frame.

Dans un mot donné, deux inputs de signature ne peuvent pas partager le même nom local.

En revanche, des frames différentes peuvent réutiliser le même nom local sans ambiguïté.

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

```nicole
: ok { -- x:Int }
  1
;
```

Exemple invalide :

```nicole
: bad { -- x:Int }
  1 2
;
```

Ce dernier exemple doit être rejeté, pas corrigé silencieusement en gardant seulement `2`.

Exemple de valeur ignorée explicitement :

```nicole
: ignore { n:Int -- }
  n drop
;
```

Appel conceptuel :

```nicole
100 3 4 compute
```

Avec :

```nicole
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

Dans un même parent, deux sous-mots ne peuvent pas avoir le même nom.

Le cas legacy « sous-mot vs mot utilisateur top-level » est obsolète en phase 2, car les définitions utilisateur top-level sont invalides.

Exemple :

```nicole
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

Exemple invalide :

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

Ces deux sous-mots sont interdits :

- ils appartiennent au même parent
- `child` est un seul nom visible dans ce scope local

Alternative valide :

```nicole
: parent { -- }

  : child-int { -- n:Int }
    1
  ;

  : child-string { -- text:String }
    "x"
  ;

  child-int drop
  child-string drop
;
```

---

# 7. Appel des sous-mots

Depuis l’intérieur du parent, les sous-mots sont appelés par leur nom court.

```nicole
price qty subtotal
dup vat
```

Depuis l’extérieur, ils ne sont pas visibles comme API publique en v1.

Exemple non retenu comme API publique v1 :

```nicole
12 3 invoice.subtotal
```

Le compilateur peut néanmoins utiliser un nom qualifié interne à des fins de diagnostic ou d’organisation.

---

# 8. Pas de capture lexicale

Un sous-mot ne voit pas les variables du parent.

Interdit :

```nicole
: outer { a:Int -- result:Int }

  : add-a { x:Int -- y:Int }
    x a +      # erreur : a n’existe pas dans add-a
  ;

  10 add-a
;
```

Chaque mot, parent ou enfant, possède sa propre frame isolée.

Des frames différentes peuvent réutiliser les mêmes noms locaux.

Exemple valide :

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

Ici :

- `foo.x` et `bar.x` sont deux variables locales distinctes
- `bar` ne lit jamais implicitement `foo.x`
- `x` dans `bar` désigne l’input local de `bar`
- `x` dans le corps de `foo` désigne l’input local de `foo`

---

# 9. Unicité des noms visibles

Dans un même espace de visibilité / résolution, deux mots ne peuvent pas avoir le même nom.

La résolution statique se fait par le nom dans l’espace donné.

Ce nom doit désigner une seule définition visible.

Toute collision visible est une erreur de compilation.

Les signatures de sortie ne servent jamais à distinguer deux mots, car deux définitions de même nom sont interdites quelles que soient leurs signatures.

Exemple invalide :

```nicole
: id { x:Int -- y:Int }
  x
;

: id { x:String -- y:String }
  x
;
```

Ces deux définitions sont interdites, même si leurs types d’entrée diffèrent.

Exemple invalide :

```nicole
: foo { a:Int b:Int -- r:Int }
  a b +
;

: foo { a:Int b:Int c:Int -- r:Int }
  a b + c +
;
```

Ces deux définitions sont interdites, même si leurs arités diffèrent.

Formes recommandées :

```nicole
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
```

---

# 10. Point d’entrée hôte

En mode embarqué, l’hôte choisit le nom canonique d’un mot exporté comme point d’entrée.

Exemple de convention d’intégration :

```nicole
module @app
  : run { args:List<String> -- code:Int }
    0
  ;
  export : run
end-module
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

Le point d’entrée exposé ici est `@app.run`.
Le langage n’impose aucun nom spécial.
L’hôte peut choisir n’importe quel mot exporté compatible avec sa convention d’intégration.
Mais deux mots exportés ne peuvent jamais partager le même nom canonique visible hôte.

---

# 11. Mots fournis par l’hôte

Deux directions coexistent :

- `export` : déclaration module-locale qui expose un mot Nicole vers l’hôte
- `host.*` : mot fourni par l’hôte, appelable par le programme

Tout mot dont le nom commence par `host.` est réservé à l’hôte.

Exemple abrégé de noms hôte :

```text
host.log
host.time
```

Ces noms abrégés ne constituent pas le format canonique du contrat.
Le format canonique `signature` / `availability` / `effect` est défini dans `HOST_ABI.md`.

Ces mots ne sont pas définis dans le code source du programme.

Le langage connaît leur signature via le contrat d’intégration de l’hôte.

Leur corps est fourni par l’hôte, hors du langage source.

L’effet (`pure` ou `dirty`) d’un mot `host.*` appartient au contrat hôte (`HOST_ABI.md`), pas à la syntaxe source Nicole.

La v1 n’introduit pas de forme source du type `dirty host.foo { ... }`.

Règles :

- un programme utilisateur ne peut pas définir un mot `host.*`
- tout mot `host.*` appelé directement par le programme est requis pour ce programme en v1
- si un mot `host.*` appelé directement est absent du contrat d’intégration, cela constitue une erreur d’intégration statique avant exécution lorsque le contrat est connu
- si l’environnement hôte est dynamique et que cette liaison requise n’est pas disponible au moment de l’appel, cela constitue une erreur d’intégration à l’exécution
- la résolution statique traite `host.*` comme des mots connus du même espace nominal ; chaque nom visible doit désigner une seule définition fournie par le contrat hôte

En v1, il n’existe aucun mécanisme standard de test de présence, de fallback ou d’appel conditionnel pour un mot `host.*` optionnel.

Par conséquent, un programme ne peut pas appeler directement un mot `host.*` comme s’il était requis tout en admettant qu’il pourrait être absent.

Exemple invalide :

```nicole
: show-config { key:String -- value:String }
  key host.read-config
;
```

Ce programme est invalide si le contrat hôte ne déclare pas `host.read-config`.

Exemple conceptuel futur :

```nicole
# extension future possible
# host.file.open { path:String -- r:Result<Handle<File>,HostError> }
```

POINT OUVERT : `host.file.open` suppose encore des types hôte futurs comme `Handle<T>`, `HostError` et un type hôte `File`.

---

# 12. `if`

`if` consomme un `Bool` au sommet de la pile locale.

Syntaxe retenue :

```nicole
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

```nicole
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

```nicole
value case
  pattern => expression
  pattern when guard => expression
  pattern => expression
  _       => expression
end
```

Exemple :

```nicole
: sign-label { n:Int -- text:String }
  n case
    0 => "zero"
    1 => "one"
    _ => "many"
  end
;
```

Exemple de branche gardée :

```nicole
: classify-result { r:Result<Int,MapError> -- text:String }
  r case
    Ok(v) when v 0 > => "positive"
    Ok(v) => "non-positive"
    Err(MissingKey) => "missing"
  end
;
```

Toutes les branches doivent produire le même nombre de valeurs, les mêmes types et le même effet de pile.
Cette égalité doit pouvoir être vérifiée statiquement.

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

Règles de liaison :

- `Ok(v)` crée un binding local `v`
- `Err(e)` crée un binding local `e`
- `Err(MissingKey)` ne crée aucun binding local
- `Err(OutOfBounds)` ne crée aucun binding local
- `MissingKey` et `OutOfBounds` seuls ne créent aucun binding local
- `_` ne crée aucun binding local
- les bindings créés par le pattern sont visibles dans le guard éventuel, puis dans le corps de branche sélectionné

Exemple de branche liant :

```nicole
: unwrap-result { r:Result<Int,MapError> -- n:Int }
  r case
    Ok(v) => v
    Err(e) => 0
  end
;
```

Le pattern matching avancé reste hors v1.

---

# 14. Récursion

La récursion est autorisée.

En v0.16, la récursion directe en position terminale reçoit une garantie de pile constante sur la pile d'appels Nicole.

Exemple de récursion directe en position terminale :

```nicole
: sum-down-acc { n:Int acc:Int -- result:Int }
  n 0 = if
    acc
  else
    n 1 - acc n + sum-down-acc
  end
;
```

Cet exemple est valide et bénéficie de la garantie de pile constante pour ses appels récursifs directs en position terminale.

La récursion non terminale reste valide, sans garantie de pile constante.

Exemple de récursion non terminale :

```nicole
: fact { n:Int -- r:Int }
  n case
    0 => 1
    _ => n n 1 - fact *
  end
;
```

La récursion mutuelle reste possible si les signatures sont connues avant analyse.
Elle reste valide en v0.16, mais sans garantie de pile constante.

La collecte préalable des signatures reste nécessaire pour :

- connaître tous les mots avant analyse des corps
- permettre la récursion mutuelle
- détecter tôt les collisions de noms visibles

Exemple de récursion mutuelle valide :

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

Cet exemple reste valide avec des noms visibles uniques :

- `even` et `odd` ont chacun un nom distinct
- la collecte préalable des signatures suffit à permettre leurs appels réciproques

Les garanties de croissance de pile diffèrent donc selon la forme de récursion :

- récursif direct en position terminale : garantie de pile constante
- récursion non terminale : valide, sans garantie de pile constante
- récursion mutuelle : valide, sans garantie de pile constante

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
DirtyQuote<{ captures | inputs -- outputs }>
Unit
```

Dans `Quote<{ captures | inputs -- outputs }>`, les mots `captures`, `inputs` et `outputs` sont des placeholders descriptifs. Les types concrets doivent utiliser des entrées et sorties nommées, par exemple `Quote<{ | x:Int -- y:Int }>` ou `Quote<{ a:Int | x:Int -- y:Int }>` .

Dans `DirtyQuote<{ captures | inputs -- outputs }>`, la structure de signature est identique.
Seule l’information d’effet diffère.

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

```nicole
: consume-only { msg:String -- }
  msg drop
;
```

`consume-only` ne produit aucune valeur.

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

```nicole
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
mod # modulo entier
+.
-.
*.
/.
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

- `+`, `-` et `*` sont définis uniquement pour `Int Int -> Int`
- `div` et `mod` sont définis uniquement pour `Int Int -> Int`
- `+.`, `-.`, `*.` et `/.` sont définis uniquement pour `Float Float -> Float`
- `/` nu n’est pas un opérateur arithmétique v1
- aucune coercion implicite entre `Int` et `Float` n’est autorisée
- `<`, `<=`, `>`, `>=` sont définis pour `Int Int -> Bool` et `Float Float -> Bool`
- ces comparaisons ne sont pas définies pour des types mélangés
- `=` et `!=` sont définis pour deux valeurs de même type exact `A A -> Bool`
- les opérateurs booléens produisent un `Bool`

Exemples :

```nicole
7 2 div
```

produit `3`.

```nicole
7.0 2.0 /.
```

produit `3.5`.

```nicole
1.5 2.0 +.
```

produit `3.5`.

Exemple de TVA :

```nicole
: vat { amount:Int -- tax:Int }
  amount 20 * 100 div
;
```

Exemple Float :

```nicole
: circle-area { r:Float -- area:Float }
  r r *. 3.14159 *.
;
```

---

# 19. Collections v1

Les listes sont immuables.

Les listes non vides peuvent être typées depuis leurs éléments.

La liste vide doit être annotée explicitement :

```nicole
[]:List<Int>
[]:List<String>
[]:List<Map<String,Int>>
```

`[]:List<T>` est une liste vide typée explicitement.

`[]` non annoté est invalide en v1.

Littéraux de liste :

```nicole
[]:List<Int>
[1]
[1, 2, 3]
["a", "b"]
[1, [2, 3]]
```

Règles :

- `[]:List<T>` désigne une liste vide de type `List<T>`
- `[]` non annoté est invalide, même si un contexte voisin pourrait suggérer un type
- les listes non vides sont typées depuis leurs éléments
- la notation `,` sépare les éléments dans un littéral
- les listes peuvent être imbriquées

Note syntaxique :

- dans une expression, `:` peut servir à annoter explicitement une construction vide
- en v1, cette annotation est introduite uniquement pour `[]:List<T>` et `map.empty:Map<K,V>`
- cette annotation est distincte du `:` qui ouvre une définition de mot

Exemples valides :

```nicole
: empty-names { -- xs:List<String> }
  []:List<String>
;
```

```nicole
: empty-ints { -- xs:List<Int> }
  []:List<Int>
;
```

Exemple invalide :

```nicole
: bad-empty-list { -- xs:List<Int> }
  []
;
```

Car l’annotation de type de la liste vide est manquante.

Opérations canoniques v1 :

```text
list.len
list.is-empty
list.get
list.first
list.last
list.set
list.append
list.concat
list.reverse
list.map
list.filter
list.fold
list.reduce
```

Notes :

- `++` peut rester comme sucre futur, mais n’est pas la forme canonique v1
- les signatures ci-dessous sont écrites dans l’ordre d’appel naturel du langage, avec la valeur principale avant l’opérateur

Signatures conceptuelles :

```text
list.len      { xs:List<T> -- n:Int }
list.is-empty { xs:List<T> -- b:Bool }
list.get      { xs:List<T> index:Int -- r:Result<T,ListError> }
list.first    { xs:List<T> -- r:Result<T,ListError> }
list.last     { xs:List<T> -- r:Result<T,ListError> }
list.set      { xs:List<T> index:Int value:T -- r:Result<List<T>,ListError> }
list.append   { xs:List<T> value:T -- ys:List<T> }
list.concat   { xs:List<T> ys:List<T> -- zs:List<T> }
list.reverse  { xs:List<T> -- ys:List<T> }
list.map      { xs:List<T> q:(Quote<{ | x:T -- y:U }> | DirtyQuote<{ | x:T -- y:U }>) -- ys:List<U> }
list.filter   { xs:List<T> q:(Quote<{ | x:T -- keep:Bool }> | DirtyQuote<{ | x:T -- keep:Bool }>) -- ys:List<T> }
list.fold     { xs:List<T> init:Acc q:(Quote<{ | acc:Acc x:T -- out:Acc }> | DirtyQuote<{ | acc:Acc x:T -- out:Acc }>) -- out:Acc }
list.reduce   { xs:List<T> q:(Quote<{ | a:T b:T -- c:T }> | DirtyQuote<{ | a:T b:T -- c:T }>) -- out:T }
```

Ces signatures décrivent la partie appelable exigée par chaque builtin higher-order.
Le choix `Quote` ou `DirtyQuote` est ensuite contraint par les règles d’effet de `SEMANTIQUE.md`.

Le `|` vide dans `Quote<{ | ... }>` ou `DirtyQuote<{ | ... }>` signifie que l’appel de `list.map`, `list.filter`, `list.fold` ou `list.reduce` ne fournit aucune capture supplémentaire au moment du builtin.

Il ne signifie pas que la quotation passée doit avoir été construite sans captures internes.

Ces builtins consomment une quotation déjà construite.

La compatibilité est vérifiée sur la partie appelable `inputs -- outputs`.

Exemples :

```nicole
: first { xs:List<String> -- s:String }
  xs 0 list.get case
    Ok(v) => v
    Err(OutOfBounds) => ""
  end
;
```

```nicole
: replace-first { xs:List<Int> -- ys:List<Int> }
  xs 0 42 list.set case
    Ok(v) => v
    Err(OutOfBounds) => xs
  end
;
```

```nicole
: concat-singletons { -- xs:List<Int> }
  [2] [4] list.concat
;
```

```nicole
: inc-all { xs:List<Int> -- ys:List<Int> }
  xs :[ | x:Int -- y:Int | x 1 + ;] list.map
;
```

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

```nicole
: keep-positive { xs:List<Int> -- ys:List<Int> }
  xs :[ | x:Int -- keep:Bool | x 0 > ;] list.filter
;
```

```nicole
: sum { xs:List<Int> -- total:Int }
  xs 0 :[ | acc:Int x:Int -- out:Int | acc x + ;] list.fold
;
```

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

```nicole
: sum-nonempty { xs:List<Int> -- total:Int }
  xs :[ | a:Int b:Int -- c:Int | a b + ;] list.reduce
;
```

`list.reduce` est uniquement défini pour une liste non vide.

Une liste vide doit être rejetée statiquement lorsqu’elle est prouvable, sinon elle constitue une erreur d’utilisation à l’exécution.

Règles supplémentaires :

- `list.first` renvoie `Ok(value)` pour le premier élément et `Err(OutOfBounds)` sur liste vide
- `list.last` renvoie `Ok(value)` pour le dernier élément et `Err(OutOfBounds)` sur liste vide
- `list.get` et `list.set` considèrent un index négatif comme hors limites et renvoient `Err(OutOfBounds)`
- `list.append` renvoie une nouvelle liste avec l’élément ajouté en fin
- `list.reverse` renvoie une nouvelle liste avec l’ordre inversé
- ces opérations de liste n’exécutent aucune quotation
- `list.zip` reste différé et n’est pas défini en v1

---

# 20. ListError v1

`ListError` est le type d’erreur dédié aux opérations sur les listes.

Variantes v1 :

```text
OutOfBounds
```

Règles :

- `OutOfBounds` représente un index hors limites pour `list.get` ou `list.set`
- un index négatif pour `list.get` ou `list.set` est hors limites
- `list.first` et `list.last` sur une liste vide renvoient `Err(OutOfBounds)`
- `ListError` est un type somme fermé en v1
- `list.get`, `list.set`, `list.first` et `list.last` renvoient un `Result<...,ListError>`
- `case` peut matcher `Err(OutOfBounds)` directement

Exemple :

```nicole
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

La map vide doit être annotée explicitement :

```nicole
map.empty:Map<String,Int>
map.empty:Map<Int,String>
```

`map.empty:Map<K,V>` est une construction vide typée explicitement.

`map.empty` non annoté est invalide en v1.

Règles :

- les clés v1 sont `Int`, `String` ou `Bool`
- `Float` n’est pas autorisé comme clé en v1
- les types de clé définis par l’utilisateur ne sont pas supportés en v1
- l’extensibilité future des clés est différée
- cette extensibilité future peut inclure des handles hôte ou des valeurs de type identité, mais v1 ne définit aucun tel mécanisme
- les valeurs peuvent être de n’importe quel type supporté, y compris `Quote`, `List<T>` et `Map<K,V>`
- toute opération de mise à jour retourne une nouvelle map
- `map.empty:Map<K,V>` construit une map vide de type `Map<K,V>`
- `map.empty` non annoté est invalide, même si un contexte voisin pourrait suggérer un type
- les maps préservent l’ordre d’insertion des clés
- `map.keys` expose les clés dans cet ordre d’insertion
- `map.values` expose les valeurs dans le même ordre que `map.keys`
- `map.set` sur une clé existante met à jour la valeur sans déplacer la clé
- `map.remove` retire aussi la clé de cet ordre
- un `map.set` effectué après suppression réinsère la clé en fin d’ordre

Opérations prévues :

```text
map.empty
map.get
map.contains
map.set
map.remove
map.len
map.is-empty
map.keys
map.values
```

Ici, `map.empty` désigne le nom canonique de l'opération.
Dans le code source v1, la construction vide doit être écrite avec annotation explicite : `map.empty:Map<K,V>`.
La forme nue `map.empty` est invalide en expression.

Signatures conceptuelles :

```text
map.empty:Map<K,V> { -- m:Map<K,V> }
map.get     { m:Map<K,V> k:K -- r:Result<V,MapError> }
map.contains{ m:Map<K,V> k:K -- ok:Bool }
map.set     { m:Map<K,V> k:K v:V -- m2:Map<K,V> }
map.remove  { m:Map<K,V> k:K -- r:Result<Map<K,V>,MapError> }
map.len     { m:Map<K,V> -- n:Int }
map.is-empty{ m:Map<K,V> -- ok:Bool }
map.keys    { m:Map<K,V> -- xs:List<K> }
map.values  { m:Map<K,V> -- xs:List<V> }
```

Sémantique attendue :

- `map.empty:Map<K,V>` construit une map vide
- `m k map.get` lit la valeur associée à `k` et renvoie `Ok(value)` si la clé existe, sinon `Err(MissingKey)`
- `m k map.contains` teste la présence d’une clé et renvoie `true` si elle existe, sinon `false`
- `m k v map.set` renvoie une nouvelle map avec association mise à jour
- `map.set` ne mute jamais la map d’entrée sur place
- `m k map.remove` renvoie `Ok(newMap)` si la clé existe et `Err(MissingKey)` sinon
- `map.remove` ne mute jamais la map d’entrée sur place
- `m map.len` renvoie le nombre d’entrées
- `m map.is-empty` renvoie `true` si la map est vide, sinon `false`
- `m map.keys` renvoie les clés dans l’ordre d’insertion
- `m map.values` renvoie les valeurs dans le même ordre que `map.keys`
- `map.set` sur une clé existante conserve la position originale de cette clé
- `map.remove` retire la clé de l’ordre d’insertion
- si une clé supprimée est réinsérée via `map.set`, elle est placée en fin d’ordre
- ces opérations de map n’exécutent aucune quotation

Éléments explicitement différés :

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

Exemples :

```nicole
: empty-cfg { -- cfg:Map<String,Int> }
  map.empty:Map<String,Int>
;
```

```nicole
: cfg-with-timeout { -- cfg:Map<String,Int> }
  map.empty:Map<String,Int>
  "timeout" 30 map.set
;
```

```nicole
: timeout { cfg:Map<String,Int> -- n:Int }
  cfg "timeout" map.get case
    Ok(v) => v
    Err(MissingKey) => 0
  end
;
```

```nicole
: has-timeout { cfg:Map<String,Int> -- ok:Bool }
  cfg "timeout" map.contains
;
```

```nicole
: store-action { -- actions:Map<String,Quote<{ | x:Int -- y:Int }>> }
  map.empty:Map<String,Quote<{ | x:Int -- y:Int }>>
  "inc" :[ | x:Int -- y:Int | x 1 + ;] map.set
;
```

`map.get` doit renvoyer un `Result<V,MapError>`. L’absence de clé est représentée par `Err(MissingKey)` plutôt que par une valeur implicite cachée.

`map.remove` doit renvoyer un `Result<Map<K,V>,MapError>`. L’absence de clé est représentée par `Err(MissingKey)` plutôt que par une suppression silencieuse.

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

```nicole
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

Formes explicites :

- dans `case`, les motifs de `Result` s’écrivent `Ok(v)` et `Err(e)`
- hors `case`, la construction d’une valeur `Result` utilise les mots postfixes `Ok!` et `Err!`

Constructeurs postfixes :

```text
Ok!  { value:T -- r:Result<T,E> }
Err! { error:E -- r:Result<T,E> }
```

Sémantique :

- `Ok!` consomme la valeur au sommet de pile et produit `Ok(value)`
- `Err!` consomme la valeur d’erreur au sommet de pile et produit `Err(error)`
- `Ok(v)` et `Err(e)` ne sont pas des formes de construction par expression en v1

Helpers retenus en v1 :

```text
result.is-ok     { r:Result<T,E> -- b:Bool }
result.is-err    { r:Result<T,E> -- b:Bool }
result.unwrap-or { r:Result<T,E> fallback:T -- value:T }
```

Ces helpers sont ergonomiques.

`case` reste le mécanisme officiel d’inspection structurée d’un `Result`.

## Propagation avec `?`

L’opérateur `?` est autorisé sur une valeur de type `Result<V,E>`.

Sémantique :

```text
Ok(v)  ? -> pousse v et continue
Err(e) ? -> retourne immédiatement Err(e) depuis la frame courante
```

Règles :

- `?` propage uniquement depuis la frame d’exécution courante
- dans un mot, `?` quitte ce mot
- dans une quotation, `?` quitte cette quotation
- `?` ne saute jamais directement hors d’un mot appelant, d’un mot exporté appelant, d’une quotation extérieure, ni d’un builtin de collection
- en v1, `?` est autorisé seulement dans une frame dont la signature de sortie complète est exactement une seule valeur de type `Result<T,E>`
- le type d’erreur produit par `?` doit correspondre exactement au type d’erreur `E` de cette sortie
- aucune conversion implicite ni élargissement de type d’erreur n’existe en v1

Exemple valide :

```nicole
: require-timeout-flag { cfg:Map<String,Int> -- r:Result<Int,MapError> }
  cfg "timeout" map.get ?
  drop
  1 Ok!
;
```

Exemple invalide :

```nicole
: bad-timeout { cfg:Map<String,Int> -- n:Int }
  cfg "timeout" map.get ?
;
```

Le second exemple est invalide parce que `?` peut produire `Err(MissingKey)` alors que le mot promet une sortie simple `Int`.

## Différé

Les éléments suivants restent hors de cette phase :

```text
result.unwrap
result.map
result.map-err
result.and-then
result.match
list.try-map
list.try-filter
list.try-fold
```

Exemples :

```nicole
: parse-timeout { cfg:Map<String,Int> -- r:Result<Int,MapError> }
  cfg "timeout" map.get
;
```

```nicole
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
Elle se comporte comme un mot anonyme : elle a sa propre frame, une pile locale vide au départ, des variables locales immuables, et un retour exact conforme à sa signature.

Type canonique :

```text
Quote<{ captures | inputs -- outputs }>
DirtyQuote<{ captures | inputs -- outputs }>
```

Exemples :

```text
Quote<{ | -- }>
Quote<{ | x:Int -- y:Int }>
Quote<{ a:Int | x:Int -- y:Int }>
Quote<{ | acc:Acc x:T -- out:Acc }>
DirtyQuote<{ | x:Int -- y:Int }>
DirtyQuote<{ a:Int | x:Int -- y:Int }>
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
- `Quote<{ ... }>` désigne une quotation pure
- `DirtyQuote<{ ... }>` désigne une quotation dirty

## Syntaxe

La quotation est fermée par `;]`.

Le `;` termine le corps concaténatif de la quotation.

Le `]` ferme la structure de quotation.

Le mot `;` continue par ailleurs à terminer un mot.

La forme canonique est :

```nicole
:[ captures | inputs -- outputs | body ;]
```

Exemples :

```nicole
:[ | -- | ;]
```

```nicole
:[ | x:Int -- y:Int | x 1 + ;]
```

```nicole
:[ a:Int | x:Int -- y:Int | x a + ;]
```

La forme explicite est la seule forme canonique en v1.

Exemples explicites liés à l’hôte :

```nicole
:[ | msg:String -- | msg host.log ;]
```

```nicole
"hello" :[ msg:String | -- | msg host.log ;]
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

```nicole
2 3 :[ x:Int y:Int | -- r:Int | x y + ;]
```

signifie :

- `x = 2`
- `y = 3`
- `x` est la valeur la plus profonde du groupe capturé
- `y` est la valeur la plus proche du sommet au moment de la construction

## Sémantique de `call`

Convention de pile :

```text
[... input1, input2, quote] call
```

`call` consomme d’abord la quotation au sommet de pile, puis consomme les inputs attendus par cette quotation sous elle, puis pousse les outputs.
`call` ne donne pas à la quotation un accès direct à la pile courante.
La quotation consomme uniquement les inputs déclarés par son type, situés sous la quotation sur la pile appelante.
Ces inputs deviennent des variables locales immuables dans la frame propre de la quotation.
La pile locale de la quotation commence vide.

Exemple sans capture :

```nicole
3 :[ | x:Int -- y:Int | x 1 + ;] call
```

Résultat :

```nicole
4
```

Exemple avec capture :

```nicole
3 4 :[ a:Int | x:Int -- y:Int | x a + ;] call
```

Résultat :

```nicole
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
- ne réutilise jamais la pile du caller comme pile locale de la quotation

## Portée

Dans le corps d’une quotation :

- les captures sont visibles comme des variables locales en lecture seule
- les inputs du `call` sont visibles comme des variables locales en lecture seule
- aucune capture par référence implicite n’est autorisée
- aucune mutation des captures n’est autorisée
- si `?` apparaît dans le corps, la quotation doit elle-même déclarer exactement une seule sortie de type `Result<T,E>`
- dans une quotation, `?` quitte uniquement cette quotation

Les noms locaux doivent être uniques dans la frame de la quotation.

Une capture et un input de `call` ne peuvent donc pas partager le même nom dans une même quotation.

En revanche, une quotation peut réutiliser le nom d’un local du mot qui la construit, car il s’agit d’une autre frame.

Cette réutilisation est valide mais un nom distinct reste souvent plus lisible.

## Intégration avec `list.map`

Une quotation de transformation pour `list.map` a une forme du genre :

```text
Quote<{ | x:T -- y:U }>
ou DirtyQuote<{ | x:T -- y:U }>
```

Ici, le `|` vide décrit la partie appelable requise par `list.map`.

Il n’interdit pas qu’une quotation déjà construite contienne des captures internes.

`list.map` consomme une quotation déjà construite et vérifie la compatibilité sur `x:T -- y:U`.

`list.map` préserve l’ordre des éléments.

Le parcours conceptuel est de gauche à droite.

Sur une liste vide, `list.map` retourne une liste vide.

Si la quotation renvoie `Result<U,E>`, alors `list.map` renvoie `List<Result<U,E>>`.

Il ne renvoie pas implicitement `Result<List<U>,E>`.

`list.map` n’introduit aucun court-circuit implicite.

## Intégration avec `list.filter`

Une quotation de prédicat pour `list.filter` a une forme du genre :

```text
Quote<{ | x:T -- keep:Bool }>
ou DirtyQuote<{ | x:T -- keep:Bool }>
```

Cette écriture décrit la partie appelable exigée par `list.filter`.

Une quotation capturante déjà construite reste valide si sa partie appelable correspond à `x:T -- keep:Bool`.

`list.filter` consomme une quotation déjà construite et vérifie la compatibilité sur `x:T -- keep:Bool`.

`list.filter` préserve l’ordre relatif des éléments retenus.

Le parcours conceptuel est de gauche à droite.

Sur une liste vide, `list.filter` retourne une liste vide.

La quotation doit retourner `Bool`.

`list.filter` n’introduit aucun court-circuit implicite sur `Result`.

Exemple :

```nicole
[1, 2, 3, 4] :[ | x:Int -- keep:Bool | x 2 % 0 = ;] list.filter
```

Exemple :

```nicole
[1, 2, 3] :[ | x:Int -- y:Int | x 1 + ;] list.map
```

```nicole
[1, 2, 3] 10 :[ offset:Int | x:Int -- y:Int | x offset + ;] list.map
```

Résultat attendu :

```nicole
[2, 3, 4]
```

## Intégration avec `list.fold`

La quotation de `list.fold` a typiquement une forme du genre :

```text
Quote<{ | acc:Acc x:T -- out:Acc }>
ou DirtyQuote<{ | acc:Acc x:T -- out:Acc }>
```

Là encore, cette écriture décrit la partie appelable exigée par `list.fold`.

Une quotation capturante déjà construite reste valide si sa partie appelable correspond à `acc:Acc x:T -- out:Acc`.

`list.fold` consomme lui aussi une quotation déjà construite.

L’accumulateur est le premier input de la quotation et l’élément courant le second.

Le parcours conceptuel est de gauche à droite.

Sur une liste vide, `list.fold` retourne l’accumulateur initial.

Il n’introduit aucun mécanisme spécial de propagation hors de la frame de cette quotation.

Exemple conceptuel :

```nicole
[1, 2, 3] 0 :[ | acc:Int x:Int -- out:Int | acc x + ;] list.fold
```

## Intégration avec `list.reduce`

La quotation de `list.reduce` a typiquement une forme du genre :

```text
Quote<{ | a:T b:T -- c:T }>
ou DirtyQuote<{ | a:T b:T -- c:T }>
```

Cette forme décrit la partie appelable exigée par `list.reduce`.

Une quotation capturante déjà construite peut être utilisée si sa partie appelable reste `a:T b:T -- c:T`.

`list.reduce` consomme lui aussi une quotation déjà construite.

Le premier élément de la liste sert d’accumulateur implicite initial.

Le parcours conceptuel est de gauche à droite.

La liste doit être non vide.

Il n’introduit aucun mécanisme spécial de propagation hors de la frame de cette quotation.

Exemple conceptuel :

```nicole
[1, 2, 3] :[ | a:Int b:Int -- c:Int | a b + ;] list.reduce
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

```nicole
:[ a | -- r:Int | a 1 + ;]
```

Ici, `a` est placé dans la zone des captures, mais aucun type n’est fourni.

Erreur attendue :

- les captures doivent être typées

Valeur de capture incompatible :

```nicole
"hello" :[ a:Int | -- r:Int | a 1 + ;] call
```

Erreur attendue :

- la capture attend `Int`
- la pile fournit `String`

## Formulation courte

```text
Une quotation est une valeur de type `Quote<{ captures | inputs -- outputs }>` ou `DirtyQuote<{ captures | inputs -- outputs }>`.
La barre est obligatoire, même lorsque la zone captures est vide.
Les captures, inputs et outputs sont typés dans la syntaxe de référence.
`call` consomme une quotation, exécute son corps et applique son effet de pile.
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

```nicole
: square { x:Int -- y:Int }
  x x *   # pousse x deux fois, puis multiplie
;
```

Les commentaires de bloc ne sont pas définis en v1.

---

# 27. Syntaxe à ne pas utiliser

Ne pas proposer cette syntaxe :

```nicole
pub word add : Int Int -> Int
  +
;
```

Ni :

```nicole
pub const pi : Float = 3.14159
```

Ni :

```nicole
let name = "Ada"
```

Ni :

```nicole
value case
  pattern if condition => expression
end
```

Ni :

```nicole
value case
  pattern => when condition expression
end
```

Ni une syntaxe basée sur `->` pour les signatures.

La syntaxe canonique provisoire est :

```nicole
: word-name { arg1:Type arg2:Type -- out1:Type }
  arg1 arg2 some-word
;
```

Les variantes de visibilité sont :

```nicole
module @demo
  : private-word { x:Int -- y:Int }
    x
  ;

  dirty : internal-dirty { x:Int -- y:Int }
    x
  ;

  pub : internal-word { x:Int -- y:Int }
    x
  ;

  pub dirty : internal-dirty-shared { x:Int -- y:Int }
    x
  ;

  : event { payload:String -- }
    payload drop
  ;
  export : event

  dirty : run { -- code:Int }
    "start" host.log
    0
  ;
  export : run
end-module
```

---

# 28. Exemple complet valide

```nicole
# Contrat hôte supposé :
# host.log
# signature:
# { msg:String -- }
# availability:
# required
# effect:
# dirty

: square { x:Int -- y:Int }
  x x *
;

: PI { -- value:Float }
  3.14159
;

: circle-area { r:Float -- area:Float }
  r r *. PI *.
;

pub : helper { n:Int -- m:Int }
  n 1 +
;

module @app
  dirty : on-message { msg:String -- }
    msg host.log
  ;
  export : on-message

  : run { args:List<String> -- code:Int }
    0
  ;
  export : run
end-module
```

---

# 29. Résumé de la syntaxe

Mot privé :

```nicole
: private-name { x:Int -- y:Int }
  x 1 +
;
```

Mot public interne :

```nicole
pub : shared-name { x:Int -- y:Int }
  x 1 +
;
```

Mot dirty privé :

```nicole
dirty : private-dirty { x:Int -- y:Int }
  x 1 +
;
```

Mot public interne dirty :

```nicole
pub dirty : shared-dirty { x:Int -- y:Int }
  x 1 +
;
```

Mot exporté à l’hôte :

```nicole
module @app
  : event { payload:String -- }
    payload drop
  ;
  export : event
end-module
```

Mot exporté dirty :

```nicole
module @app
  dirty : run { -- code:Int }
    "start" host.log
    0
  ;
  export : run
end-module
```

Sous-mot :

```nicole
: parent { x:Int -- y:Int }

  : child { z:Int -- r:Int }
    z z *
  ;

  x child
;
```

Conditionnel :

```nicole
condition if
  ...
else
  ...
end
```

Pattern matching :

```nicole
value case
  pattern => expression
  pattern when guard => expression
  _ => expression
end
```

Quotation :

```nicole
:[ a:Int | x:Int -- y:Int | x a + ;]
```

Appel d’une quotation :

```nicole
[... input, quote] call
```

Listes :

```nicole
[]:List<Int>
xs list.is-empty
xs 0 list.get
xs list.first
xs list.last
xs 0 42 list.set
xs 42 list.append
xs ys list.concat
xs list.reverse
xs quote list.map
```

Maps :

```nicole
map.empty:Map<String,Int>
m map.is-empty
m k map.get
m k v map.set
m map.keys
m map.values
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
