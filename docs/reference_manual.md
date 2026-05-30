# Manuel de référence Nicole

Ce document est un manuel utilisateur explicatif. Il aide a apprendre Nicole, a relire rapidement une regle et a structurer du code idiomatique, sans remplacer la specification normative.

> Note : en cas de divergence, `SYNTAXE.md`, `SEMANTIQUE.md` et `HOST_ABI.md` font toujours autorite.

Pour les conseils de conception, d'organisation et de style, voir aussi le [Guide du developpeur Nicole](developer_guide.md).

Si vous decouvrez Nicole, lisez d'abord [2. Comment penser en Nicole](#2-comment-penser-en-nicole) puis [3. Prendre Nicole en main en 15 minutes](#3-prendre-nicole-en-main-en-15-minutes). Les sections suivantes servent ensuite de reference thematique.

## Table des matieres

- [1. Vue d'ensemble](#1-vue-densemble)
- [2. Comment penser en Nicole](#2-comment-penser-en-nicole)
- [3. Prendre Nicole en main en 15 minutes](#3-prendre-nicole-en-main-en-15-minutes)
- [4. Structure d'un programme](#4-structure-dun-programme)
- [5. Mots, signatures et pile locale](#5-mots-signatures-et-pile-locale)
- [6. Resolution des noms et imports](#6-resolution-des-noms-et-imports)
- [7. Types](#7-types)
- [8. Effets pure / dirty](#8-effets-pure--dirty)
- [9. Controle de flux](#9-controle-de-flux)
- [10. Collections](#10-collections)
- [11. Result et propagation](#11-result-et-propagation)
- [12. Quotations](#12-quotations)
- [13. Sous-mots](#13-sous-mots)
- [14. Recursion](#14-recursion)
- [15. ABI hote](#15-abi-hote)
- [16. Export vers l'hote](#16-export-vers-lhote)
- [17. Idiomes et styles recommandes](#17-idiomes-et-styles-recommandes)
- [18. Erreurs](#18-erreurs)
- [19. Exemples guides et exemples complets](#19-exemples-guides-et-exemples-complets)
- [20. Reference rapide](#20-reference-rapide)
- [21. Annexes](#21-annexes)

## 1. Vue d'ensemble

Nicole est un langage concaténatif, typé, modulaire et embarqué. Un programme y est écrit comme une suite de mots qui consomment des valeurs en entree, produisent des valeurs en sortie, et s'integrent a un hote via un contrat ABI explicite.

Ce qui le caracterise le plus vite :

- les mots ont toujours une signature ;
- les entrees de signature deviennent des variables locales immuables ;
- chaque mot s'execute dans sa propre frame ;
- les effets de bord hote sont visibles via `dirty` ;
- les echecs normaux passent par `Result`, pas par des exceptions implicites ;
- les quotations permettent de manipuler du comportement comme une valeur.

Exemple minimal :

```nicole
module @manual.overview
  : add-one { x:Int -- y:Int }
    x 1 +
  ;
end-module
```

Ce petit exemple concentre deja les idees de base :

- `add-one` est un mot ;
- `x` est un local immuable cree par la signature ;
- `1` et `+` forment le corps concaténatif ;
- le mot promet exactement une sortie `Int`.

## 2. Comment penser en Nicole

Avant la syntaxe, il est utile d'avoir un modele mental stable. Nicole devient beaucoup plus simple des qu'on le lit comme un langage de contrats locaux plutot que comme une variante libre de Forth.

### Le corps d'un mot est une suite d'actions

Le corps d'un mot se lit de gauche a droite. Chaque nom local pousse une valeur, chaque builtin transforme la pile locale, chaque appel de mot applique sa propre signature.

Exemple :

```nicole
module @mental.concat
  : square { x:Int -- y:Int }
    x x *
  ;
end-module
```

Ici, on ne "mutate" rien :

- `x` pousse la valeur locale `x` ;
- `x` la pousse une deuxieme fois ;
- `*` consomme deux `Int` et produit un `Int`.

### La pile locale n'est pas la pile Forth classique

Le point clef est la separation entre pile appelante et pile locale. Dans un Forth classique, on raisonne souvent sur une pile de donnees partagee par les mots. En Nicole, l'appel d'un mot retire ses arguments de la pile appelante, les range dans des locals, puis execute le corps sur une pile locale qui commence vide.

Consequence pratique :

- un mot ne voit pas les valeurs residuelles de son appelant ;
- seules ses entrees nommees sont visibles ;
- son retour doit reconstruire exactement les sorties promises.

Exemple conceptuel :

```nicole
module @mental.frames
  : compute { a:Int b:Int -- result:Int }
    a b + 2 *
  ;
end-module
```

Si l'appelant avait d'autres valeurs sous `a` et `b`, `compute` n'y a pas acces.

### Pourquoi les entrees deviennent des variables locales

Nicole choisit des signatures nommees plutot qu'une discipline de pile purement anonyme. Cela rend le code plus relisible sans renoncer au modele concaténatif.

Exemple :

```nicole
module @mental.locals
  : add-five { x:Int -- y:Int }
    x 5 +
  ;
end-module
```

Lire `x` est plus stable que raisonner sur "la valeur qui se trouve a telle profondeur de pile". Le langage garde donc le raisonnement par pile, mais il expose les entrees sous forme de noms.

### Pourquoi les variables sont immuables

L'immuabilite supprime une grosse source d'ambiguite :

- un nom local designe toujours la meme valeur ;
- il n'existe pas de syntaxe d'assignation ;
- un sous-mot ou une quotation ne peut pas modifier un local externe.

Cela renforce le principe "une signature = un contrat local lisible". Quand vous relisez un mot, `x` signifie toujours "l'entree `x`", jamais "la derniere version de `x` apres mutation".

### Pourquoi les effets pure / dirty existent

Nicole est pense pour l'embarque. Il faut donc distinguer le calcul pur des interactions avec l'hote. `dirty` sert a rendre ces effets de bord visibles dans la signature operative du code.

En pratique :

- un mot pur peut etre deplace ou reutilise plus facilement ;
- un mot dirty marque explicitement une dependance a l'hote ou a un autre mot dirty ;
- l'analyse d'effet est statique, pas conventionnelle.

Cette separation aide a revoir un module rapidement : la partie pure calcule, la partie dirty connecte.

### Pourquoi Result est privilegie aux exceptions

Nicole traite les echecs normaux comme des valeurs. Un acces a une cle absente, un index hors limites ou une verification metier attendue doivent passer par `Result`, pas par un mecanisme cache.

Cela a trois effets utiles :

- l'echec est visible dans la signature ;
- l'appelant choisit comment inspecter ou propager l'erreur ;
- le flux de controle reste local et lisible.

`?` existe justement pour garder une ecriture lineaire sans reintroduire d'exception implicite. Voir [11. Result et propagation](#11-result-et-propagation).

### Pourquoi les quotations existent

Une quotation est une valeur executable de premiere classe. Elle sert a retarder une execution, a capturer explicitement quelques valeurs, ou a passer un comportement a `list.map`, `list.filter`, `list.fold` ou `list.reduce`.

Elle n'est pas :

- une macro ;
- une fermeture implicite sur tout l'environnement ;
- un mecanisme d'ABI hote.

Au lieu de "faire de la magie", Nicole dit clairement :

- quelles captures existent ;
- quels inputs seront consommes plus tard ;
- quelles sorties seront produites.

### Comment raisonner sur les signatures

Une signature se lit comme un contrat de frame :

```text
{ entrees -- sorties }
```

Exemple :

```text
{ cfg:Map<String,Int> -- r:Result<Int,MapError> }
```

Cela signifie :

- l'appelant fournit une `Map<String,Int>` ;
- le mot recupere cette valeur sous le nom local `cfg` ;
- sa pile locale commence vide ;
- au retour, il doit produire exactement une sortie ;
- cette sortie est un `Result<Int,MapError>`.

Quand vous lisez Nicole, partez toujours de la signature. Le corps n'est qu'une justification executable de ce contrat.

## 3. Prendre Nicole en main en 15 minutes

Cette section est volontairement progressive. Chaque etape ajoute une idee sans quitter la forme deja vue a l'etape precedente.

### 1. Creer un mot simple

Commencez par un mot qui ne prend rien et renvoie une valeur.

```nicole
module @quick.start
  : zero { -- n:Int }
    0
  ;
end-module
```

Ce qu'il faut retenir :

- un mot commence par `:` et se termine par `;` ;
- la signature est obligatoire ;
- `{ -- n:Int }` signifie "aucune entree, une sortie `Int`".

### 2. Utiliser des parametres

Ajoutez ensuite une entree nommee.

```nicole
module @quick.start
  : add-one { x:Int -- y:Int }
    x 1 +
  ;
end-module
```

Ici, `x` est un local immuable cree par la signature. Lire `x` pousse sa valeur sur la pile locale.

### 3. Retourner plusieurs valeurs

Un mot peut produire plusieurs sorties, dans l'ordre de la signature.

```nicole
module @quick.start
  : duplicate-pair { x:Int -- a:Int b:Int }
    x x
  ;
end-module
```

Ce qu'il faut retenir :

- Nicole autorise plusieurs sorties ;
- le corps doit laisser exactement ces deux valeurs ;
- les labels `a` et `b` sont documentaires, pas mutables.

### 4. Utiliser une liste

Passez ensuite a une structure simple.

```nicole
module @quick.start
  : singleton { x:Int -- xs:List<Int> }
    []:List<Int>
    x list.append
  ;
end-module
```

Ce mot montre deux decisions importantes de Nicole :

- la liste vide doit etre annotee explicitement ;
- `list.append` retourne une nouvelle liste.

### 5. Utiliser un Result

Quand une operation peut echouer normalement, la signature le montre.

```nicole
module @quick.start
  : first-or-zero { xs:List<Int> -- n:Int }
    xs list.first case
      Ok(v) => v
      Err(OutOfBounds) => 0
    end
  ;
end-module
```

Ce mot introduit trois idees d'un coup :

- `list.first` retourne `Result<Int,ListError>` ;
- `case` est la forme d'inspection detaillee ;
- l'appelant peut transformer l'echec en valeur de repli.

### 6. Utiliser une quotation

Une quotation permet de passer un comportement a un builtin d'ordre superieur.

```nicole
module @quick.start
  : inc-all { xs:List<Int> -- ys:List<Int> }
    xs :[ | x:Int -- y:Int | x 1 + ;] list.map
  ;
end-module
```

Ce qu'il faut retenir :

- `:[ ... ;]` construit une quotation ;
- la partie appelable ici est `x:Int -- y:Int` ;
- `list.map` applique cette quotation a chaque element.

### 7. Appeler une capacite hote

L'etape finale relie le langage a l'hote.

```nicole
module @host
  require console.log { msg:String -- } dirty
end-module

module @quick.start
  import @host.console.log as console.log

  dirty : log-first-state { xs:List<Int> -- }
    xs list.first case
      Ok(v) => "list has a first value" console.log
      Err(OutOfBounds) => "list is empty" console.log
    end
  ;
end-module
```

Ce mot assemble les idees precedentes :

- une operation de liste retourne `Result` ;
- `case` choisit une branche ;
- `console.log` vient de l'hote ;
- le mot devient `dirty`.

En sept etapes, vous avez deja vu :

- un mot pur ;
- des parametres ;
- des sorties multiples ;
- une collection ;
- un `Result` ;
- une quotation ;
- une capacite hote.

La suite du manuel revient sur chaque idee de facon plus precise.

## 4. Structure d'un programme

Un programme Nicole est organise en modules. Cette structure n'est pas un detail de packaging : elle participe a la resolution statique des noms, a la visibilite, aux imports et a l'ABI hote.

Forme minimale :

```nicole
module @manual.structure
  : greet { excited:Bool -- msg:String }
    excited case
      true => "hello"
      false => "hi"
    end
  ;
end-module
```

Rappels utiles :

- les mots definis par l'utilisateur vivent dans `module @... end-module` ;
- une definition top-level utilisateur est invalide ;
- `module @host` est reserve au contrat ABI ;
- les imports sont module-locaux ;
- les imports apparaissent avant les definitions de mots ;
- les commentaires de ligne utilisent `#`.

Exemple de commentaire :

```nicole
module @manual.comments
  : square { x:Int -- y:Int }
    x x *   # multiplie x par lui-meme
  ;
end-module
```

> Attention : cette forme est invalide en v1, parce qu'un mot utilisateur ne peut pas etre top-level.
>
> ```nicole
> : bad-top-level {
>   --
> }
> ;
> ```

> TODO(spec) : la forme `include "path.nic"` existe en syntaxe, mais sa semantique detaillee de mapping fichiers/chemins reste differee. Le manuel n'attribue donc pas de comportement plus precis a `include`.

## 5. Mots, signatures et pile locale

Le coeur du langage est ici : un mot est un contrat de frame. Sa signature indique ce qu'il prend, ce qu'il rend, et le corps doit respecter exactement ce contrat.

Forme canonique :

```nicole
: word-name { arg1:Type arg2:Type -- out1:Type }
  ...
;
```

Exemple simple :

```nicole
module @manual.words
  : pair { -- a:Int b:String }
    1 "ok"
  ;
end-module
```

Points essentiels :

- les entrees creent des variables locales immuables ;
- les noms de sortie sont documentaires ;
- la pile locale d'un mot commence vide ;
- au retour, il doit rester exactement les sorties declarees ;
- toute valeur ignoree doit etre supprimee explicitement avec `drop`.

Exemple de lecture locale :

```nicole
module @manual.locals
  : double { x:Int -- y:Int }
    x x +
  ;
end-module
```

Exemple d'ignorance explicite :

```nicole
module @manual.drop
  : ignore { n:Int -- }
    n drop
  ;
end-module
```

Exemple invalide :

```nicole
module @invalid.demo
  : bad-return { -- n:Int }
    1 "ok"
  ;
end-module
```

Pourquoi il est invalide :

- la signature promet une seule sortie `Int` ;
- le corps laisse deux valeurs ;
- Nicole ne corrige jamais cela silencieusement.

> Note : `{ -- }` signifie "aucune sortie". Ce n'est pas la meme chose que `{ -- u:Unit }`.

## 6. Resolution des noms et imports

Nicole fait de la resolution statique. Un appel ne depend ni de la pile residuelle, ni d'un namespace dynamique, ni d'un lookup tardif.

Ordre de resolution dans un module :

1. noms locaux du scope courant ;
2. mots du meme module par nom court ;
3. alias d'import visibles ;
4. noms qualifies explicites autorises ;
5. builtins et espaces reserves (`list.*`, `map.*`, `result.*`).

Exemples d'import :

```nicole
module @app
  import @text
  import @text.split as split
  import @host.console.log as console.log
end-module
```

Ce que signifient ces formes :

- `import @text` autorise l'usage qualifie `@text.word` ;
- `import @text as t` cree un alias local `t.word` ;
- `import @text.split` n'expose pas `split` en nom court ;
- `import @text.split as split` expose `split` ;
- `import @host.console.log as console.log` cree un alias qualifie local ;
- un alias reste strictement local au module importateur.

Les imports groupes existent aussi :

```nicole
module @app
  import @math.ops.{ add sub } as ops
  import @host.console.{ log read-line } as *
end-module
```

Ils restent un sucre de surface :

- `as *` n'est pas un wildcard import ;
- seuls les symboles explicitement enumeres sont importes ;
- les collisions d'alias restent des erreurs ;
- les regles de visibilite ne changent pas.

Exemples invalides utiles a memoriser :

```nicole
module @demo
  import @text.split

  : run { input:String -- out:List<String> }
    input split
  ;
end-module
```

Ici, `split` n'est pas expose en nom court.

```nicole
module @demo
  import @text.*
end-module
```

Les wildcard imports n'existent pas en v1.

> Note : `pub` n'injecte pas de nom court global. Il rend un chemin qualifie importable ou appelable explicitement selon les regles de resolution.

## 7. Types

Nicole v1 fixe une surface de types volontairement petite. Le manuel la presente comme un jeu de briques simples plutot que comme un systeme ouvert par inference.

Types standards confirmes :

- `Int`
- `Float`
- `Bool`
- `String`
- `List<T>`
- `Map<K,V>`
- `ListError`
- `MapError`
- `Result<V,E>`
- `Quote<{ captures | inputs -- outputs }>`
- `DirtyQuote<{ captures | inputs -- outputs }>`
- `Unit`
- `@host.*` pour les types opaques hote declares

Exemple avec conteneur :

```nicole
module @manual.types
  : cfg-with-timeout { -- cfg:Map<String,Int> }
    map.empty:Map<String,Int>
    "timeout" 30 map.set
  ;
end-module
```

Regles a retenir :

- `[]:List<T>` est la forme canonique d'une liste vide ;
- `map.empty:Map<K,V>` est la forme canonique d'une map vide ;
- `[]` et `map.empty` sans annotation sont invalides ;
- les cles de `Map<K,V>` sont limitees a `Int`, `String` et `Bool` ;
- un type opaque hote peut etre une valeur de map, jamais une cle ;
- `Quote` et `DirtyQuote` sont de vrais types, pas de simples notations de surface.

Exemple avec type opaque hote importe :

```nicole
module @manual.opaque
  import @host.io.FileHandle as io.FileHandle

  : keep-open { file:io.FileHandle -- file2:io.FileHandle }
    file
  ;
end-module
```

Exemple invalide :

```nicole
module @invalid.demo
  : bad-map { -- m:Map<List<Int>,String> }
    map.empty:Map<List<Int>,String>
  ;
end-module
```

La cle `List<Int>` n'est pas autorisee en v1.

> TODO(spec) : `Unit` est confirme comme type distinct de l'absence de sortie, mais le litteral concret eventuel pour produire une valeur `Unit` n'est pas encore fixe.

## 8. Effets pure / dirty

Nicole est pur par defaut. L'effet `dirty` sert a rendre visibles les interactions avec l'hote ou avec d'autres mots deja dirty.

Exemple pur :

```nicole
module @manual.effects
  : add-one { x:Int -- y:Int }
    x 1 +
  ;
end-module
```

Exemple dirty :

```nicole
module @host
  require console.log { msg:String -- } dirty
end-module

module @manual.effects
  import @host.console.log as console.log

  dirty : log-message { msg:String -- }
    msg console.log
  ;
end-module
```

Ce qu'il faut retenir :

- `pure` n'est pas un modificateur general de mot ;
- `pure` n'existe en source que dans `require` ;
- un mot pur ne peut pas appeler du code dirty ;
- un mot exporte suit les memes regles d'effet qu'un mot normal ;
- `call`, `list.map`, `list.filter`, `list.fold` et `list.reduce` deviennent dirty si la quotation fournie est un `DirtyQuote`.

Exemple invalide :

```nicole
module @host
  require console.log { msg:String -- } dirty
end-module

module @invalid.demo
  import @host.console.log as console.log

  : bad-pure-host-call { -- }
    "hello" console.log
  ;
end-module
```

Le mot est infere dirty mais non annote.

Pour l'usage pratique, retenez surtout ceci :

- calculez en pur le plus longtemps possible ;
- connectez a l'hote dans de petits mots dirty ;
- gardez les frontieres dirty faciles a reperer.

Voir aussi [12. Quotations](#12-quotations), [15. ABI hote](#15-abi-hote) et [17. Idiomes et styles recommandes](#17-idiomes-et-styles-recommandes).

## 9. Controle de flux

Nicole v1 retient principalement `if` et `case`. Dans les deux cas, les branches doivent produire le meme effet de pile.

### `if`

`if` consomme un `Bool` :

```nicole
module @manual.if
  : abs { x:Int -- y:Int }
    x 0 < if
      0 x -
    else
      x
    end
  ;
end-module
```

Ce qu'il faut retenir :

- la condition est consommee ;
- la branche choisie s'execute dans la meme frame ;
- les deux branches doivent laisser la meme forme de pile.
- un negatif calcule comme `0 x -` reste une expression ordinaire ; ce n'est pas la meme chose qu'un litteral lexical comme `-5`.

### `case`

`case` consomme un scrutinee puis selectionne la premiere branche compatible.

Exemple :

```nicole
module @manual.case
  : timeout-or-default { cfg:Map<String,Int> -- n:Int }
    cfg "timeout" map.get case
      Ok(v) => v
      Err(MissingKey) => 30
    end
  ;
end-module
```

Patterns confirmes en v1 :

- litteraux `Int`, `String`, `Bool`
- `Ok(v)`
- `Err(e)`
- `MissingKey`
- `OutOfBounds`
- `_`

Les patterns `Int` incluent les entiers negatifs lexicalement valides, par exemple `-1`.

Les guards sont autorises :

```nicole
module @manual.case
  : classify-result { r:Result<Int,MapError> -- text:String }
    r case
      Ok(v) when v 0 > => "positive"
      Ok(v) => "non-positive"
      Err(MissingKey) => "missing"
    end
  ;
end-module
```

Regles utiles pour les guards :

- le guard doit etre pur ;
- son effet de pile doit etre exactement `-- Bool` ;
- il ne doit pas consommer la pile preexistante ;
- `?` y est interdit.

Exemple invalide :

```nicole
module @host
  require console.log { msg:String -- } dirty
end-module

module @invalid.demo
  import @host.console.log as console.log

  : bad-case-guard { r:Result<Int,MapError> -- text:String }
    r case
      Ok(v) when "trace" console.log true => "ok"
      Err(MissingKey) => "missing"
    end
  ;
end-module
```

Le guard appelle du code dirty, ce qui est interdit.

> TODO(spec) : `SEMANTIQUE.md` laisse entendre qu'un `case` non exhaustif sur `Bool` peut parfois rester une erreur de contrat d'execution, alors que `INVALID_EXAMPLES.md` et les tests de checker le traitent comme une erreur statique. Le manuel n'arbitre pas au-dela de ce constat.

## 10. Collections

Les collections v1 sont immuables. Elles restent simples a lire si vous separez bien les operations structurelles, les erreurs normales et les builtins d'ordre superieur.

### Listes

Exemple de lecture :

```nicole
module @manual.list
  : first { xs:List<Int> -- n:Int }
    xs 0 list.get case
      Ok(v) => v
      Err(OutOfBounds) => 0
    end
  ;
end-module
```

Operations confirmees :

- `list.len`
- `list.is-empty`
- `list.get`
- `list.first`
- `list.last`
- `list.set`
- `list.append`
- `list.concat`
- `list.reverse`
- `list.map`
- `list.filter`
- `list.fold`
- `list.reduce`

Points pratiques :

- `list.first` et `list.last` retournent `Result<T,ListError>` ;
- `list.get` et `list.set` utilisent `Err(OutOfBounds)` ;
- `list.fold` retourne l'accumulateur initial sur liste vide ;
- `list.reduce` exige une liste non vide ;
- `list.zip` n'est pas defini en v1.

### Maps

Exemple de construction :

```nicole
module @manual.map
  : cfg-with-timeout { -- cfg:Map<String,Int> }
    map.empty:Map<String,Int>
    "timeout" 30 map.set
  ;
end-module
```

Operations confirmees :

- `map.get`
- `map.contains`
- `map.set`
- `map.remove`
- `map.len`
- `map.is-empty`
- `map.keys`
- `map.values`

Points pratiques :

- `map.get` retourne `Result<V,MapError>` ;
- `map.remove` retourne `Result<Map<K,V>,MapError>` ;
- `map.set` retourne une nouvelle map ;
- l'ordre d'insertion est observable via `map.keys` et `map.values` ;
- une mise a jour ne deplace pas une cle existante ;
- une suppression suivie d'une reinsertion replace la cle en fin d'ordre.

Exemple d'ordre observable :

```nicole
module @manual.map
  : user-keys { -- xs:List<String> }
    map.empty:Map<String,Int>
    "alice" 1 map.set
    "bob" 2 map.set
    map.keys
  ;
end-module
```

Exemple invalide :

```nicole
module @invalid.demo
  : bad-remove-return { users:Map<String,Int> -- out:Map<String,Int> }
    users "alice" map.remove
  ;
end-module
```

`map.remove` ne retourne pas une map simple.

### Builtins d'ordre superieur

`list.map`, `list.filter`, `list.fold` et `list.reduce` consomment une quotation deja construite. Pour les lire correctement :

- regardez d'abord la partie appelable de la quotation ;
- verifiez ensuite si la quotation est pure ou dirty ;
- rappelez-vous qu'aucun de ces builtins ne transforme implicitement un `List<Result<...>>` en `Result<List<...>>`.

Voir [11. Result et propagation](#11-result-et-propagation) et [12. Quotations](#12-quotations).

## 11. Result et propagation

`Result<V,E>` represente un succes ou un echec normal et explicite. Nicole distingue soigneusement la construction, l'inspection et la propagation locale.

Construction :

- `Ok!` construit une valeur `Ok(...)` ;
- `Err!` construit une valeur `Err(...)`.

Inspection :

- `case` reste la forme officielle pour l'inspection detaillee ;
- `result.is-ok`, `result.is-err` et `result.unwrap-or` sont des helpers ergonomiques.

Exemple :

```nicole
module @manual.result
  : timeout-or-30 { cfg:Map<String,Int> -- n:Int }
    cfg "timeout" map.get 30 result.unwrap-or
  ;
end-module
```

### L'operateur `?`

`?` agit sur un `Result<V,E>` et ne propage que dans la frame courante.

Exemple valide :

```nicole
module @manual.result
  : require-timeout-flag { cfg:Map<String,Int> -- r:Result<Int,MapError> }
    cfg "timeout" map.get ?
    drop
    1 Ok!
  ;
end-module
```

Regles strictes :

- `?` est autorise seulement si la frame retourne exactement une seule valeur `Result<T,E>` ;
- le type d'erreur doit correspondre exactement ;
- dans une quotation, `?` quitte la quotation et non le mot parent ;
- `?` n'introduit aucun court-circuit implicite dans `list.map`, `list.filter`, `list.fold` ou `list.reduce`.

Exemple invalide :

```nicole
module @invalid.demo
  : bad-ok-expression { -- r:Result<Int,String> }
    Ok(1)
  ;
end-module
```

`Ok(v)` est un motif de `case`, pas une forme de construction par expression.

Point de lecture important :

- `Ok(v)` et `Err(e)` appartiennent a la syntaxe de pattern ;
- `Ok!` et `Err!` appartiennent a la construction de valeurs.

Voir aussi [9. Controle de flux](#9-controle-de-flux) et [17. Idiomes et styles recommandes](#17-idiomes-et-styles-recommandes).

## 12. Quotations

Une quotation est une valeur executable de premiere classe. Elle a sa propre frame, ses propres locals et ses propres regles de retour.

Forme canonique :

```nicole
:[ captures | inputs -- outputs | body ;]
```

Exemple simple :

```nicole
module @manual.quotes
  : plus-one { x:Int -- y:Int }
    x :[ | n:Int -- m:Int | n 1 + ;] call
  ;
end-module
```

Exemple avec capture :

```nicole
module @manual.quotes
  : add-captured { x:Int y:Int -- z:Int }
    x y :[ a:Int | n:Int -- m:Int | n a + ;] call
  ;
end-module
```

Ce qu'il faut retenir :

- la quotation est fermee par `;]` ;
- les captures sont prises a la construction, par valeur ;
- `call` consomme d'abord la quotation au sommet de pile, puis ses inputs ;
- les inputs sont consommes dans l'ordre de la signature ;
- les noms de captures et d'inputs doivent etre uniques dans la frame de la quotation ;
- `DirtyQuote` suit les memes regles structurelles que `Quote`, avec un effet different.

Exemple d'ordre des inputs :

```nicole
module @manual.quotes
  : call-order { -- n:Int }
    2 3 :[ | x:Int y:Int -- r:Int | x y - ;] call
  ;
end-module
```

Ici :

- `x=2`
- `y=3`
- la quotation est au sommet juste avant `call`

Exemple invalide :

```nicole
:[ | x:Int -- y:Int | x 1 + ]
```

`"]"` seul ne suffit pas : une quotation de valeur se ferme par `;]`.

Point de lecture utile :

- lisez d'abord les captures ;
- lisez ensuite la partie appelable ;
- traitez enfin le corps comme un petit mot anonyme.

Pour les interactions avec `Result`, voir [11. Result et propagation](#11-result-et-propagation). Pour les effets, voir [8. Effets pure / dirty](#8-effets-pure--dirty).

## 13. Sous-mots

Un mot peut contenir des sous-mots prives. Ils sont visibles depuis leur parent, mais ne font pas partie de l'API publique du module en v1.

Exemple :

```nicole
module @manual.subwords
  : invoice { price:Int qty:Int -- total:Int }

    : subtotal { price:Int qty:Int -- amount:Int }
      price qty *
    ;

    price qty subtotal
  ;
end-module
```

Regles utiles :

- un sous-mot est appele par son nom court depuis le parent ;
- deux sous-mots freres ne peuvent pas partager le meme nom ;
- un sous-mot ne capture pas implicitement les locals du parent ;
- le compilateur peut utiliser des noms internes qualifies, mais ils ne constituent pas une API publique.

Exemple invalide :

```nicole
module @invalid.demo
  : outer { a:Int -- result:Int }

    : add-a { x:Int -- y:Int }
      x a +
    ;

    10 add-a
  ;
end-module
```

Le sous-mot tente de lire un local du parent, ce qui est interdit.

## 14. Recursion

La recursion est autorisee en v1. La v0.16 ajoute une garantie specifique pour la recursion directe en position terminale.

Exemple de recursion terminale directe :

```nicole
module @manual.recursion
  : sum-down-acc { n:Int acc:Int -- result:Int }
    n 0 = if
      acc
    else
      n 1 - acc n + sum-down-acc
    end
  ;
end-module
```

Exemple de recursion non terminale :

```nicole
module @manual.recursion
  : fact { n:Int -- result:Int }
    n case
      0 => 1
      _ => n n 1 - fact *
    end
  ;
end-module
```

Exemple de recursion mutuelle :

```nicole
module @manual.recursion
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

Resume pratique :

- recursion directe en position terminale : garantie de pile d'appels Nicole constante ;
- recursion non terminale : valide, sans cette garantie ;
- recursion mutuelle : valide, sans cette garantie ;
- quotations : aucune garantie specifique de pile constante.

## 15. ABI hote

L'ABI hote decrit ce que le programme Nicole requiert de l'hote. Cette surface passe par `module @host`, `require`, `opaque` et des imports explicites depuis `@host`.

Exemple de contrat :

```nicole
module @host
  opaque io.FileHandle
  require console.log { msg:String -- } dirty
  require io.open-file { path:String mode:String -- r:Result<@host.io.FileHandle,String> } dirty
end-module
```

Dans un module applicatif :

```nicole
module @app
  import @host.console.log as console.log
  import @host.io.FileHandle as io.FileHandle
  import @host.io.open-file as io.open-file
end-module
```

Ce qu'il faut retenir :

- `module @host` n'est pas un module utilisateur normal ;
- son contenu est limite a `require` et `opaque` ;
- chaque `require` declare un chemin, une signature et un effet ABI explicite ;
- chaque `opaque` declare un type opaque nominal sous `@host.*` ;
- les fragments `module @host` se consolident en un contrat unique ;
- les imports groupes sur `@host` se desucrent en imports explicites ;
- les quotations ne franchissent pas l'ABI en v1.

Exemple invalide :

```nicole
module @invalid.demo
  : show-config { key:String -- value:String }
    key host.read-config
  ;
end-module
```

Une capacite hote ne s'appelle pas directement en `host.*`.

Autre point important :

- un type opaque importe est un nom de type ;
- ce n'est ni un constructeur, ni un mot appelable.

## 16. Export vers l'hote

`export : word` expose un mot Nicole a l'hote. C'est une declaration, pas une nouvelle definition.

Exemple :

```nicole
module @app
  : run { input:String -- output:String }
    input
  ;
  export : run
end-module
```

Regles pratiques :

- l'export doit etre dans le module qui definit le mot ;
- il ne depend ni des imports ni des alias ;
- le nom canonique cote hote est `@module.word` ;
- la signature exportee fait partie du contrat ABI visible ;
- un export peut utiliser un type opaque hote declare ;
- les quotations ne franchissent pas l'ABI en entree ni en sortie ;
- `export` ne change ni le typage ni l'effet du mot.

Exemple avec export dirty :

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

Si vous lisez une API exportee, regardez dans cet ordre :

1. la signature ;
2. si le mot est pur ou dirty ;
3. s'il transporte des types ABI visibles ;
4. s'il delegue a des helpers internes ou a des capacites hote.

## 17. Idiomes et styles recommandes

Cette section ne cree pas de nouvelles regles. Elle decrit simplement les pratiques qui tombent naturellement de la specification et des exemples valides du depot.

### Quand utiliser `case` plutot que `result.unwrap-or`

Utilisez `case` quand :

- vous devez distinguer plusieurs variantes ;
- vous avez besoin du binding `Ok(v)` ou `Err(e)` ;
- vous voulez traiter explicitement une erreur fermee comme `MissingKey` ou `OutOfBounds`.

Utilisez `result.unwrap-or` quand :

- vous voulez seulement fournir une valeur de repli ;
- vous ne faites rien d'autre avec l'erreur ;
- la lecture gagne vraiment en concision.

Exemple court :

```nicole
cfg "timeout" map.get case
  Ok(v) => v
  Err(MissingKey) => 30
end
```

est plus expressif que `result.unwrap-or` des que vous commencez a raisonner sur la variante elle-meme.

### Quand utiliser `?`

Utilisez `?` quand la frame courante retourne deja exactement un `Result<T,E>` compatible et que vous voulez garder un chemin nominal lineaire.

Exemple typique :

```nicole
module @manual.styles
  : require-timeout-flag { cfg:Map<String,Int> -- r:Result<Int,MapError> }
    cfg "timeout" map.get ?
    drop
    1 Ok!
  ;
end-module
```

Evitez `?` quand :

- vous avez besoin de transformer l'erreur avant de la rendre ;
- vous etes dans une frame qui ne retourne pas un `Result` compatible ;
- vous etes dans un guard de `case`.

### Quand preferer une quotation

Preferez une quotation quand vous avez besoin :

- de passer un comportement a `list.map`, `list.filter`, `list.fold` ou `list.reduce` ;
- de retarder une execution ;
- de capturer explicitement quelques valeurs par copie.

N'utilisez pas une quotation pour :

- contourner les regles de visibilite ;
- simuler un callback hote a travers l'ABI ;
- remplacer un mot nomme quand un helper stable serait plus lisible.

### Comment structurer un module

Une structure lisible ressemble souvent a ceci :

1. imports ;
2. helpers prives ;
3. mots `pub` si le module expose une API Nicole ;
4. mots `export` si le module expose une API hote.

Pour un module qui parle a l'hote :

- gardez les imports `@host` en tete ;
- isolez les petits helpers purs ;
- placez les points d'entree dirty en bas.

### Comment nommer les mots

Nicole interdit deja la surcharge visible. Un bon nom doit donc porter son intention sans compter sur la pile pour lever l'ambiguite.

Styles utiles observes dans le depot :

- `timeout-or-default`
- `require-timeout-flag`
- `inc-all`
- `keep-open`

Tendances utiles :

- utilisez des verbes pour les actions ;
- utilisez `-or-default` pour une valeur de repli ;
- utilisez `-all` pour un traitement element par element ;
- gardez un nom distinct par comportement visible.

### Comment separer code pur et code dirty

Une bonne organisation est souvent :

- des mots purs qui lisent, transforment et valident des donnees ;
- des mots dirty minces qui importent des capacites hote, appellent les helpers purs, puis publient un resultat.

Exemple de separation :

```nicole
module @host
  require console.log { msg:String -- } dirty
end-module

module @manual.styles
  import @host.console.log as console.log

  : banner { -- msg:String }
    "ready"
  ;

  dirty : announce { -- }
    banner console.log
  ;
end-module
```

### Comment construire une API exportee

Une API exportee claire :

- expose peu de mots ;
- donne des signatures faciles a lire ;
- evite les quotations a la frontiere ;
- utilise `Result` seulement si ce choix fait vraiment partie du contrat ;
- garde les details de journalisation ou de capacites dans des helpers internes.

Autrement dit : l'export doit ressembler a une petite facade stable, pas a tout le module.

## 18. Erreurs

Nicole distingue plusieurs categories d'erreur. Cette separation vous dit ou chercher le probleme : dans le code source, dans un `Result`, dans l'environnement d'execution ou a la frontiere d'integration.

### 1. Rejet statique

Relèvent du rejet statique quand c'est prouvable :

- collision de noms visibles ;
- import invalide ou manquant ;
- retour incompatible avec la signature ;
- branches `if` ou `case` incompatibles ;
- liste ou map vide non annotee ;
- usage illegal de `?` ;
- mauvais usage d'un type opaque hote ;
- incoherence interne du contrat ABI declare.

### 2. Erreur normale

Une erreur normale est modélisée par `Result`.

Exemples :

- `map.get` sur cle absente ;
- `map.remove` sur cle absente ;
- `list.get` hors limites.

### 3. Erreur de contrat d'execution

Elle correspond a une violation observee au runtime d'un contrat pourtant valide statiquement.

Exemples confirmes :

- `list.reduce` sur liste vide si ce vide n'etait pas prouvable statiquement ;
- capacite hote declaree mais non satisfaisable au moment de l'appel.

### 4. Erreur d'integration

Elle concerne specifiquement la frontiere avec l'hote.

Exemples :

- `require` divergents pour le meme chemin ;
- export demande par l'hote mais absent ;
- capacite declaree mais fournie avec une signature incompatible.

> Note : une erreur d'integration n'est pas un `Result`, sauf si la capacite hote elle-meme choisit explicitement de retourner un `Result`.

## 19. Exemples guides et exemples complets

Cette section rassemble trois exemples plus longs que les micro-exemples precedents. Ils ne remplacent pas la spec : ils montrent comment plusieurs pieces du langage se combinent dans un module plausible.

### Exemple 1 : mini bibliotheque utilitaire

Cet exemple montre :

- plusieurs mots ;
- un import depuis un autre module utilisateur ;
- `Result` avec `ListError` ;
- des traitements sur listes.

```nicole
module @util.defaults
  pub : missing-number { -- n:Int }
    0
  ;
end-module

module @util.list-tools
  import @util.defaults.missing-number as missing-number

  : first-or-default { xs:List<Int> -- n:Int }
    xs list.first case
      Ok(v) => v
      Err(OutOfBounds) => missing-number
    end
  ;

  : inc-all { xs:List<Int> -- ys:List<Int> }
    xs :[ | x:Int -- y:Int | x 1 + ;] list.map
  ;

  : firsts { xss:List<List<Int>> -- ys:List<Result<Int,ListError>> }
    xss :[ | xs:List<Int> -- r:Result<Int,ListError> |
      xs list.first
    ;] list.map
  ;

  : keep-non-empty { xss:List<List<Int>> -- ys:List<List<Int>> }
    xss :[ | xs:List<Int> -- keep:Bool |
      xs list.is-empty not
    ;] list.filter
  ;
end-module
```

Lecture conseillee :

- `missing-number` est `pub`, donc importable ;
- `first-or-default` choisit entre inspection detaillee et valeur de repli ;
- `firsts` montre que `list.map` retourne ici `List<Result<...>>` ;
- `keep-non-empty` montre une quotation booleenne pour `list.filter`.

### Exemple 2 : module de configuration

Cet exemple montre :

- lecture de parametres dans une `Map<String,Int>` ;
- valeurs par defaut explicites ;
- mise a jour et synthese de configuration.

```nicole
module @app.config
  : defaults { -- cfg:Map<String,Int> }
    map.empty:Map<String,Int>
    "timeout" 30 map.set
    "retries" 3 map.set
    "port" 8080 map.set
  ;

  : timeout-or-default { cfg:Map<String,Int> -- n:Int }
    cfg "timeout" map.get case
      Ok(v) => v
      Err(MissingKey) => 30
    end
  ;

  : retries-or-default { cfg:Map<String,Int> -- n:Int }
    cfg "retries" map.get case
      Ok(v) => v
      Err(MissingKey) => 3
    end
  ;

  : port-or-default { cfg:Map<String,Int> -- n:Int }
    cfg "port" map.get case
      Ok(v) => v
      Err(MissingKey) => 8080
    end
  ;

  : remember-timeout { cfg:Map<String,Int> timeout:Int -- cfg2:Map<String,Int> }
    cfg "timeout" timeout map.set
  ;

  : summary { cfg:Map<String,Int> -- values:List<Int> }
    []:List<Int>
    cfg timeout-or-default list.append
    cfg retries-or-default list.append
    cfg port-or-default list.append
  ;
end-module
```

Lecture conseillee :

- `defaults` construit une map immutable par mises a jour successives ;
- chaque helper `*-or-default` garde une politique locale lisible ;
- `summary` montre une maniere simple d'agreger plusieurs lectures dans une liste.

### Exemple 3 : module connecte a l'hote

Cet exemple montre :

- le contrat ABI dans `module @host` ;
- l'import de capacites hote ;
- une lecture pure de configuration hote ;
- du logging dirty ;
- deux exports.

```nicole
module @host
  require console.log { msg:String -- } dirty
  require config.get { key:String -- r:Result<String,MapError> } pure
end-module

module @app.service
  import @host.console.log as console.log
  import @host.config.get as config.get

  : app-name { -- name:String }
    "app-name" config.get case
      Ok(v) => v
      Err(MissingKey) => "nicole-app"
    end
  ;

  : prefix { -- msg:String }
    "[service]"
  ;

  dirty : boot { -- code:Int }
    prefix console.log
    app-name console.log
    0
  ;
  export : boot

  dirty : on-message { msg:String -- }
    prefix console.log
    app-name console.log
    msg console.log
  ;
  export : on-message
end-module
```

Lecture conseillee :

- `config.get` est pure, donc `app-name` reste pur ;
- `console.log` est dirty, donc `boot` et `on-message` sont dirty ;
- les exports restent de petites facades sur des helpers internes.

## 20. Reference rapide

Cette section sert d'aide-memoire compacte. Pour le detail normatif et les cas limites, revenez aux sections thematiques et a la spec.

### Formes de definition

| Usage | Forme |
| --- | --- |
| mot prive | `: word { ... } ... ;` |
| mot dirty prive | `dirty : word { ... } ... ;` |
| mot visible par chemin qualifie | `pub : word { ... } ... ;` |
| mot visible par chemin qualifie et dirty | `pub dirty : word { ... } ... ;` |
| export vers l'hote | `export : word` |

### Modules et imports

| Usage | Forme |
| --- | --- |
| module utilisateur | `module @app ... end-module` |
| contrat hote | `module @host ... end-module` |
| import qualifie | `import @text` |
| import alias simple | `import @text.split as split` |
| import alias prefixe | `import @host.console.log as console.log` |
| import groupe prefixe | `import @host.io.{ open-file FileHandle } as io` |
| import groupe selectionne | `import @host.console.{ log read-line } as *` |

### Mots reserves et formes reservees

| Famille | Elements |
| --- | --- |
| mots-cles et formes speciales | `if`, `else`, `end`, `case`, `when`, `pub`, `export`, `module`, `end-module`, `import`, `include`, `require`, `opaque`, `dirty`, `pure`, `call`, `?` |
| constructeurs postfixes reserves | `Ok!`, `Err!` |
| variantes reservees | `MissingKey`, `OutOfBounds` |
| racines reservees | `host`, `list`, `map`, `result` |

### Builtins principaux

| Famille | Surface |
| --- | --- |
| pile | `dup`, `drop`, `swap`, `over`, `rot` |
| arithmetique `Int` | `+`, `-`, `*`, `div`, `mod` |
| arithmetique `Float` | `+.`, `-.`, `*.`, `/.` |
| comparaisons | `<`, `<=`, `>`, `>=`, `=`, `!=` |
| booleens | `and`, `or`, `not` |
| listes | `list.len`, `list.is-empty`, `list.get`, `list.first`, `list.last`, `list.set`, `list.append`, `list.concat`, `list.reverse`, `list.map`, `list.filter`, `list.fold`, `list.reduce` |
| maps | `map.empty:Map<K,V>`, `map.get`, `map.contains`, `map.set`, `map.remove`, `map.len`, `map.is-empty`, `map.keys`, `map.values` |
| result | `Ok!`, `Err!`, `result.is-ok`, `result.is-err`, `result.unwrap-or` |

### Structures de controle

| Usage | Forme |
| --- | --- |
| conditionnel | `cond if ... else ... end` |
| matching | `value case ... end` |
| branche gardee | `pattern when guard => ...` |

### Patterns disponibles dans `case`

| Famille | Patterns |
| --- | --- |
| litteraux | `Int` dont `-1`, `String`, `Bool` |
| `Result` | `Ok(v)`, `Err(e)` |
| erreurs fermees | `MissingKey`, `OutOfBounds`, `Err(MissingKey)`, `Err(OutOfBounds)` |
| joker | `_` |

### Rappels lexicaux utiles

| Forme | Statut v1 |
| --- | --- |
| `-5` | littéral `Int` valide |
| `-3.5` | littéral `Float` valide |
| `- 5` | deux tokens separes, pas un littéral signe |
| `+5` | invalide |
| `-.5` | invalide |
| `5.` | invalide |
| `-` | operateur binaire de soustraction |
| `-.` | operateur binaire de soustraction flottante |

### Types standards

| Famille | Types |
| --- | --- |
| scalaires | `Int`, `Float`, `Bool`, `String`, `Unit` |
| collections | `List<T>`, `Map<K,V>` |
| erreurs | `ListError`, `MapError` |
| composition | `Result<V,E>` |
| comportement | `Quote<{ captures | inputs -- outputs }>`, `DirtyQuote<{ captures | inputs -- outputs }>` |
| ABI hote | `@host.*` |

### Erreurs standards

| Type | Variantes v1 |
| --- | --- |
| `ListError` | `OutOfBounds` |
| `MapError` | `MissingKey` |

### Regles essentielles de `?`

| Regle | Resume |
| --- | --- |
| portee | `?` est frame-local |
| sortie requise | la frame doit retourner exactement une seule valeur `Result<T,E>` |
| type d'erreur | le type d'erreur doit correspondre exactement |
| guards | `?` est interdit dans un guard de `case` |
| collections | `?` ne cree aucun court-circuit implicite a travers `list.map`, `list.filter`, `list.fold`, `list.reduce` |
| quotations | dans une quotation, `?` quitte la quotation et non le mot parent |

### Regles de base a ne pas oublier

| Sujet | Resume |
| --- | --- |
| listes vides | `[]` seul est invalide ; utiliser `[]:List<T>` |
| maps vides | `map.empty` seul est invalide ; utiliser `map.empty:Map<K,V>` |
| cles de map | uniquement `Int`, `String`, `Bool` |
| imports | pas de wildcard imports |
| ABI hote | pas d'appel direct `host.*` |
| exports | pas de quotations a la frontiere ABI |

## 21. Annexes

### A. Sources du manuel

Sources normatives :

- `SYNTAXE.md`
- `SEMANTIQUE.md`
- `HOST_ABI.md`

Documents derives consultes :

- `README.md`
- `EXAMPLES.md`
- `INVALID_EXAMPLES.md`
- `DESIGN_NOTES.md`

Tests consultes pour confirmer des comportements deja presents dans la spec :

- `../nicole_python_implementation/tests/test_parser.py`
- `../nicole_python_implementation/tests/test_resolver.py`
- `../nicole_python_implementation/tests/test_checker.py`
- `../nicole_python_implementation/tests/test_runtime.py`
- `../nicole_python_implementation/tests/test_host_abi.py`
- `../nicole_python_implementation/tests/test_standard_symbols.py`

### B. TODO(spec) releves dans le manuel

1. `include` existe en syntaxe, mais sa semantique detaillee reste differee.
2. Le litteral concret eventuel de `Unit` n'est pas definitivement fixe.
3. La couverture non exhaustive de `case` sur `Bool` est formulee differemment selon `SEMANTIQUE.md` d'un cote, et `INVALID_EXAMPLES.md` plus les tests de checker de l'autre.

### C. Portee du document

Ce manuel reste volontairement non normatif. Son but est :

- d'aider a apprendre le langage ;
- de faciliter la relecture des regles ;
- de montrer des formes idiomatiques deja confirmees ;
- de signaler les zones ouvertes sans les refermer editorialement.

Quand une decision de syntaxe, de semantique ou d'ABI vous semble douteuse, revenez toujours a la specification normative.
