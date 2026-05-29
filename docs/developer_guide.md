# Guide du developpeur Nicole

Ce document complete le manuel de reference. Il ne remplace ni le manuel ni la specification normative.

Le manuel de reference repond principalement a deux questions :

- que permet le langage ;
- quelle est la regle exacte.

Ce guide repond a d'autres questions :

- comment penser en Nicole ;
- comment structurer du code lisible ;
- comment reconnaitre les patterns qui s'accordent bien avec le langage ;
- quels pieges de conception reduisent la lisibilite ;
- quelles decisions de conception paraissent motivantes au vu de la surface actuelle du langage.

> Note editoriale : les recommandations qui suivent sont des conseils de lecture, d'organisation et de style. Elles ne sont pas des obligations du langage.

> Note : en cas de divergence, `SYNTAXE.md`, `SEMANTIQUE.md` et `HOST_ABI.md` restent l'autorite finale.

## Table des matieres

- [1. Pourquoi Nicole existe](#1-pourquoi-nicole-existe)
- [2. Comment penser en Nicole](#2-comment-penser-en-nicole)
- [3. Nicole compare a d'autres familles de langages](#3-nicole-compare-a-dautres-familles-de-langages)
- [4. Lire du code Nicole](#4-lire-du-code-nicole)
- [5. Ecrire du code Nicole](#5-ecrire-du-code-nicole)
- [6. Patterns recommandes](#6-patterns-recommandes)
- [7. Anti-patterns](#7-anti-patterns)
- [8. Organisation d'un projet](#8-organisation-dun-projet)
- [9. Etude de cas complete](#9-etude-de-cas-complete)
- [10. Questions frequentes](#10-questions-frequentes)
- [11. Limites connues et points ouverts](#11-limites-connues-et-points-ouverts)

## 1. Pourquoi Nicole existe

Cette section ne pretent pas retrouver une "intention officielle" cachee. Elle decrit seulement ce qui est observable dans la conception actuelle du langage.

### Un langage de contrats explicites

Nicole rend les contrats visibles tres tot :

- signatures obligatoires ;
- retours exacts ;
- effets visibles ;
- ABI hote declaree explicitement.

Cela suggere une priorite forte : rendre la lecture statique du programme fiable sans dependre d'un contexte d'execution implicite.

Le signal le plus net est la place de la signature. Un mot Nicole n'est pas seulement un corps concaténatif ; c'est un contrat nomme qui expose ses entrees, ses sorties et parfois son effet.

### Un langage qui prefere le raisonnement local

La separation entre pile appelante et pile locale, l'absence de mutation des locals, l'interdiction de capture lexicale implicite et le caractere frame-local de `?` vont toutes dans la meme direction : limiter ce qu'un lecteur doit garder en tete pour comprendre une partie de code.

Autrement dit, Nicole semble privilegier :

- le raisonnement par frame ;
- les dependances explicites ;
- les effets visibles ;
- l'absence de flux caches entre scopes.

### Un langage embarque avec frontiere hote explicite

Le depot insiste fortement sur `module @host`, `require`, `opaque` et `export`. Cela montre que Nicole n'est pas pense comme un langage autonome de ligne de commande ou comme une plateforme generaliste avec IO implicite. Il est pense comme un langage embarque dont la frontiere vers l'hote doit etre decrite proprement.

L'ABI explicite joue plusieurs roles observables :

- nommer les capacites externes requises ;
- typer les echanges avec l'hote ;
- distinguer les erreurs normales du domaine des erreurs d'integration ;
- interdire les appels `host.*` directs au profit d'un contrat consolide.

### Un langage qui se mefie du comportement implicite

Plusieurs choix vont dans le meme sens :

- pas de wildcard imports ;
- pas d'inference de type contextuelle pour `[]` ou `map.empty` ;
- pas de capture implicite des quotations ;
- pas de propagation implicite a travers `list.map` ;
- pas de quotations a la frontiere ABI ;
- pas de surcharge visible par le nom.

Ce n'est pas une promesse de simplicite absolue. C'est plutot une preference nette pour les dependances explicites et les formes lisibles par inspection.

### Le role des signatures

Dans Nicole, la signature n'est pas un commentaire enrichi. Elle pilote la lecture du mot.

Elle dit :

- ce qui entre dans la frame ;
- ce qui doit en sortir ;
- quels noms sont disponibles en lecture ;
- quelle forme de `Result` ou de type opaque circule ;
- si l'appelant doit s'attendre a une sortie simple, multiple ou structuree.

Le reste du mot doit simplement realiser ce contrat.

### Le role des effets

L'effet `dirty` signale qu'une frame depend d'une interaction hote ou d'un autre code deja dirty. L'observable important n'est pas seulement la securite ; c'est la clarte de lecture.

Un lecteur peut reperer rapidement :

- le code purement calculatoire ;
- les points de contact avec l'exterieur ;
- la propagation transitive des effets.

### Le role des quotations

Les quotations montrent que Nicole veut manipuler du comportement comme une valeur, mais sans ouvrir la porte a une fermeture implicite generalisee.

Une quotation reste :

- typee ;
- fermee par une signature explicite ;
- isolee dans sa propre frame ;
- capturee par valeur ;
- compatible avec des builtins d'ordre superieur bien delimites.

### Le role de l'ABI explicite

L'ABI explicite fait partie de la conception, pas d'un sous-systeme annexe. Elle montre que Nicole veut distinguer nettement :

- le code Nicole lui-meme ;
- les capacites que le programme consomme ;
- les mots que le programme expose ;
- les types opaques que seul l'hote sait materialiser.

Pour un developpeur, cela implique qu'une grande partie de l'architecture se lit deja dans :

- les signatures ;
- les imports ;
- les mots `dirty` ;
- le module `@host` ;
- les declarations `export`.

## 2. Comment penser en Nicole

Le manuel de reference explique deja le modele mental de base. Cette section l'approfondit pour le travail quotidien : lecture, conception, refactorisation et decoupage.

### Raisonner par contrat

Un mot Nicole se lit d'abord comme un contrat :

```text
{ entrees -- sorties }
```

Exemple :

```text
{ cfg:Map<String,Int> -- r:Result<Int,MapError> }
```

Cette ligne vous dit deja :

- la frame recevra une map sous le nom `cfg` ;
- la pile locale commencera vide ;
- le corps devra finir avec une seule sortie ;
- cette sortie est un `Result<Int,MapError>`.

Un bon reflexe consiste a formuler le chemin nominal avant meme de lire le corps :

```text
si la cle existe -> on sort un Int
si la cle manque -> on sort un Err(MissingKey)
```

Le corps est ensuite une preuve executable de ce contrat.

### Raisonner par frame

Le point central de Nicole est ici : chaque mot et chaque quotation s'executent dans une frame isolee.

Schema ASCII :

```text
pile appelante : [..., a, b]
appel de word  : consomme a, b

frame de word
  locals : a=..., b=...
  pile   : []
  corps  : ...

retour
  pousse exactement les sorties declarees
```

Ce modele change la lecture du style concaténatif :

- la pile locale est importante ;
- mais les entrees sont stabilisees comme locals nommes ;
- le mot ne depend pas de "ce qui trainait dessous" dans l'appelant.

Cela permet de lire un mot comme une petite unite close, plutot que comme une transformation implicite d'une pile globale.

### Raisonner sur le flux de donnees

Le flux de donnees Nicole se lit souvent en trois couches :

1. les donnees entrent dans la frame par la signature ;
2. le corps combine locals, builtins et appels de mots ;
3. les sorties repartent selon la signature.

Schema ASCII :

```text
signature d'entree
  ->
locals immuables
  ->
operations concaténatives
  ->
sortie exacte
```

Ce flux est encore plus net avec `Result` :

```text
input
  ->
operation susceptible d'echouer
  ->
inspection `case` ou propagation `?`
  ->
sortie declaree
```

### L'absence de mutation n'est pas un detail

Dans Nicole, l'absence de mutation a plusieurs consequences concretes :

- un local garde toujours le meme sens ;
- une lecture tardive d'un local n'a pas besoin d'etre "remontee" a travers un historique de reassignment ;
- une quotation capturante reste lisible parce qu'elle capture des valeurs, pas des emplacements mutables ;
- un sous-mot ne peut pas modifier l'etat d'un parent.

Pour le developpeur, cela pousse naturellement vers :

- des mots plus courts ;
- des helpers purs ;
- des noms qui decrivent une valeur stable plutot qu'une variable d'etat.

### Separation calcul / integration

Une grande partie du style Nicole vient de la separation entre :

- calcul pur ;
- integration hote.

Schema ASCII :

```text
inputs hote
  ->
facade dirty
  ->
helpers purs
  ->
facade dirty
  ->
exports / appels hote
```

Cette separation n'est pas imposee comme architecture officielle, mais elle s'accorde tres bien avec :

- `dirty` explicite ;
- `require` dans `@host` ;
- `export` ;
- `Result` pour les echecs normaux ;
- l'absence de side effects caches dans les builtins structurels.

### Raisonner sur `Result`

Un `Result` Nicole n'est pas une astuce ergonomique secondaire. C'est souvent le moyen principal de rendre un echec normal lisible.

Pour le lire proprement :

1. identifiez le `Result<V,E>` ;
2. demandez-vous si le code inspecte ou propage ;
3. regardez si la frame courante retourne un `Result` compatible ;
4. verifiez si le code traite l'erreur localement ou la laisse remonter.

`case` et `?` ne sont pas concurrents. Ils repondent a deux besoins differents :

- `case` inspecte ;
- `?` laisse filer localement un contrat deja compatible.

### Raisonner sur les quotations

Une quotation se lit comme un petit mot anonyme.

Ordre de lecture recommande :

1. ses captures ;
2. sa partie appelable ;
3. son corps ;
4. son effet `Quote` ou `DirtyQuote` ;
5. l'endroit ou elle est construite puis appelee ou transmise.

Schema ASCII :

```text
construction
  capture de valeurs
  -> produit une quotation

appel ou builtin d'ordre superieur
  consomme la quotation
  + consomme les inputs declares
  -> produit les outputs declares
```

La consequence pratique est simple : une quotation ne "voit" que ce qu'elle declare.

## 3. Nicole compare a d'autres familles de langages

Cette section ne cherche pas a designer un gagnant. Elle aide seulement a calibrer les attentes d'un lecteur venant d'ailleurs.

### Forth

Ce qui ressemble :

- style concaténatif ;
- operations lues de gauche a droite ;
- primitives de pile explicites ;
- gout pour des mots petits et composables.

Ce qui differe :

- les mots Nicole ont des signatures obligatoires ;
- les entrees deviennent des locals nommes ;
- la frame locale commence vide ;
- la pile appelante n'est pas partagee comme un espace de travail commun ;
- l'ABI hote est explicite et separee.

Ce que cela implique pour le developpeur :

- il faut moins raisonner sur une pile globale persistante ;
- il faut davantage lire les contrats de frame ;
- les signatures et la resolution statique remplacent une partie de la souplesse historique de Forth.

### Factor

Ce qui ressemble :

- quotations comme valeurs de premiere classe ;
- builtins d'ordre superieur ;
- style concaténatif plus discipline que Forth classique ;
- importance de la composition.

Ce qui differe :

- Nicole expose des locals de signature comme mecanisme central ;
- les captures de quotations sont explicites ;
- `DirtyQuote` et l'effet `dirty` structurent la lecture des integrations ;
- l'ABI hote explicite occupe une place plus visible.

Ce que cela implique pour le developpeur :

- les quotations Nicole sont puissantes mais plus cadrees ;
- la lisibilite depend beaucoup des signatures et des captures ;
- on ecrit souvent des quotations plus courtes et plus locales.

### Langages fonctionnels types

Ce qui ressemble :

- immuabilite des valeurs locales ;
- gout pour le calcul pur ;
- erreurs normales modelisees explicitement via `Result` ;
- importance des signatures et du typage.

Ce qui differe :

- Nicole reste concaténatif, pas expressionnel ;
- la lecture se fait par flux de pile et contrats de frame ;
- les builtins et quotations remplacent certaines constructions expressionnelles habituelles ;
- l'integration hote passe par `module @host` et `export`, pas par un simple module de fonctions.

Ce que cela implique pour le developpeur :

- il faut penser en sequence d'operations, pas en arbre d'expressions ;
- `case` et `?` structurent souvent le traitement d'erreur ;
- on garde un style de fonctions pures, mais dans une syntaxe de composition concaténative.

### Langages orientes objets classiques

Ce qui ressemble :

- structuration par modules ;
- possibilite d'exposer une petite surface publique ;
- importance d'une interface claire vers l'exterieur.

Ce qui differe :

- pas d'objets ni de mutation de champs documentes en v1 ;
- pas de methodes attachees a des instances ;
- les types opaques hote ne sont pas des objets Nicole inspectables ;
- le comportement s'organise autour de mots, de signatures et de modules, pas autour d'instances.

Ce que cela implique pour le developpeur :

- l'organisation se fait par fonctions, modules et frontieres d'integration ;
- la lisibilite vient des contrats visibles plutot que d'une hierarchie de classes ;
- un type opaque hote transporte une identite nominale, pas une API objet Nicole.

## 4. Lire du code Nicole

Une bonne methode de lecture evite de se perdre dans les details de surface. La plus robuste est la suivante :

1. lire la signature ;
2. identifier les effets ;
3. reperer les `Result` ;
4. reperer les quotations ;
5. reperer les frontieres ABI.

### Exemple annote

```nicole
module @host
  require console.log { msg:String -- } dirty
  require config.get-int { key:String -- r:Result<Int,MapError> } pure
end-module

module @reader.demo
  import @host.console.log as console.log
  import @host.config.get-int as config.get-int

  : threshold-or-default { -- n:Int }
    "threshold" config.get-int 10 result.unwrap-or
  ;

  dirty : announce-threshold { -- }
    threshold-or-default
    drop
    "threshold loaded" console.log
  ;
end-module
```

### 1. Lire la signature

Commencez par :

```text
: threshold-or-default { -- n:Int }
dirty : announce-threshold { -- }
```

Vous savez deja :

- `threshold-or-default` est pur si son corps le reste ;
- il renvoie un `Int` simple ;
- `announce-threshold` est dirty et ne renvoie rien.

> Exemple de lisibilite : les deux mots suivants sont valides. Le contraste porte seulement sur la vitesse de comprehension.

**Mauvais exemple**

```nicole
module @reading.signature.bad
  : run { x:Map<String,Int> -- y:Int }
    x "timeout" map.get 30 result.unwrap-or
  ;
end-module
```

**Pourquoi c'est problematique**

Le lecteur comprend le type, mais pas le role. Il doit ouvrir le corps pour deviner que `x` contient une configuration et que `y` represente un delai.

**Meilleur exemple**

```nicole
module @reading.signature.good
  : timeout-or-default { cfg:Map<String,Int> -- timeout:Int }
    cfg "timeout" map.get 30 result.unwrap-or
  ;
end-module
```

**Pourquoi c'est preferable**

On sait ou regarder en premier : la signature dit deja ce qui entre, ce qui sort et quelle politique generale le mot applique.

### 2. Identifier les effets

Reperez ensuite les imports hote et les mots dirty :

- `console.log` vient de `@host` et est dirty ;
- `config.get-int` vient de `@host` et est pure ;
- `announce-threshold` appelle `console.log`, donc son annotation dirty est attendue.

> Exemple de lisibilite : dans les deux cas, le comportement global reste simple. La difference est surtout dans la lecture du flux.

**Mauvais exemple**

```nicole
module @host
  require console.log { msg:String -- } dirty
end-module

module @reading.effects.bad
  import @host.console.log as console.log

  dirty : run { cfg:Map<String,Int> -- threshold:Int }
    cfg "threshold" map.get 10 result.unwrap-or
    "threshold loaded" console.log
  ;
end-module
```

**Pourquoi c'est problematique**

La logique de calcul et l'integration hote sont melangees dans le meme mot. Quand on lit `run`, on doit suivre a la fois la transformation de donnees et la presence de `dirty`.

**Meilleur exemple**

```nicole
module @host
  require console.log { msg:String -- } dirty
end-module

module @reading.effects.good
  import @host.console.log as console.log

  : threshold-or-default { cfg:Map<String,Int> -- threshold:Int }
    cfg "threshold" map.get 10 result.unwrap-or
  ;

  dirty : run { cfg:Map<String,Int> -- threshold:Int }
    cfg threshold-or-default
    "threshold loaded" console.log
  ;
end-module
```

**Pourquoi c'est preferable**

Le lecteur peut separer les questions : `threshold-or-default` explique le calcul, `run` montre seulement ou l'effet commence. L'annotation dirty aide alors reellement au lieu d'alourdir tout le raisonnement.

### 3. Reperer les `Result`

`config.get-int` retourne `Result<Int,MapError>`. Le mot `threshold-or-default` ne retourne pas un `Result` ; il consomme donc ce resultat localement via `result.unwrap-or`.

Un lecteur peut formuler le chemin nominal en une phrase :

```text
si la configuration contient "threshold", on prend sa valeur ;
sinon, on prend 10.
```

> Exemple de lisibilite : les trois formes ci-dessous sont valides. Elles ne racontent pas la meme chose au lecteur.

**Mauvais exemple**

```nicole
module @reading.result.bad
  : load-number { cfg:Map<String,Int> -- n:Int }
    cfg "timeout" map.get 30 result.unwrap-or
  ;
end-module
```

**Pourquoi c'est problematique**

La lecture reste possible, mais la signature ne dit plus qu'un `Result` etait en jeu. Si l'absence de cle a une importance semantique, la forme compacte la rend facile a manquer.

**Meilleur exemple**

```nicole
module @reading.result.good
  : timeout-or-default { cfg:Map<String,Int> -- timeout:Int }
    cfg "timeout" map.get case
      Ok(v) => v
      Err(MissingKey) => 30
    end
  ;

  : require-timeout { cfg:Map<String,Int> -- r:Result<Int,MapError> }
    cfg "timeout" map.get ?
    Ok!
  ;
end-module
```

**Pourquoi c'est preferable**

Le lecteur repere tout de suite deux intentions differentes. `timeout-or-default` inspecte localement le `Result` avec une politique visible. `require-timeout` annonce au contraire que l'absence de valeur doit remonter au caller.

### 4. Reperer les quotations

Ici, il n'y en a pas. C'est une information utile, pas un manque. L'absence de quotation signifie que le flux du code est purement lineaire.

> Exemple de lisibilite : une quotation valide peut tout de meme etre difficile a lire si elle concentre trop de logique.

**Mauvais exemple**

```nicole
module @reading.quotes.bad
  : normalize-reportable { xs:List<Int> threshold:Int -- ys:List<Int> }
    xs
    threshold
    :[ threshold:Int | x:Int -- y:Int |
      x 1 +
      threshold >
      if
        x 1 +
      else
        0
      end
    ;]
    list.map
  ;
end-module
```

**Pourquoi c'est problematique**

Le lecteur doit comprendre en meme temps la capture, le contrat `x:Int -- y:Int` et toute la logique de transformation. La quotation devient un petit bloc a deplier mentalement avant de poursuivre.

**Meilleur exemple**

```nicole
module @reading.quotes.good
  : adjust-or-zero { x:Int threshold:Int -- y:Int }
    x 1 + threshold >
    if
      x 1 +
    else
      0
    end
  ;

  : normalize-reportable { xs:List<Int> threshold:Int -- ys:List<Int> }
    xs
    threshold
    :[ threshold:Int | x:Int -- y:Int |
      x threshold adjust-or-zero
    ;]
    list.map
  ;
end-module
```

**Pourquoi c'est preferable**

On lit d'abord le contrat de `adjust-or-zero`, puis la quotation devient une simple colle locale entre `list.map` et un helper nomme. La methode de lecture reste stable.

### 5. Reperer la frontiere ABI

La frontiere ABI est visible en tete :

- `module @host` declare les capacites ;
- `import @host...` montre ou elles entrent dans le module ;
- `announce-threshold` est le mot qui consomme effectivement une capacite dirty.

> Exemple de lisibilite : la meme capacite hote peut etre plus ou moins facile a situer selon l'endroit ou elle apparait.

**Mauvais exemple**

```nicole
module @host
  require console.log { msg:String -- } dirty
  require config.get-int { key:String -- r:Result<Int,MapError> } pure
end-module

module @reading.abi.bad
  import @host.console.log as console.log
  import @host.config.get-int as config.get-int

  dirty : run { -- threshold:Int }
    "threshold" config.get-int 10 result.unwrap-or
    "threshold loaded" console.log
  ;
end-module
```

**Pourquoi c'est problematique**

La frontiere ABI est bien presente, mais le lecteur ne voit pas clairement quelle partie du mot releve du calcul et quelle partie releve de l'integration.

**Meilleur exemple**

```nicole
module @host
  require console.log { msg:String -- } dirty
  require config.get-int { key:String -- r:Result<Int,MapError> } pure
end-module

module @reading.abi.good
  import @host.console.log as console.log
  import @host.config.get-int as config.get-int

  : threshold-or-default { -- threshold:Int }
    "threshold" config.get-int 10 result.unwrap-or
  ;

  dirty : run { -- threshold:Int }
    threshold-or-default
    "threshold loaded" console.log
  ;
end-module
```

**Pourquoi c'est preferable**

La frontiere ABI est plus nette. Le lecteur peut suivre la logique pure sans se demander en permanence si une capacite hote intervient deja.

### Resume de la methode

Quand vous ouvrez un module inconnu, demandez-vous dans cet ordre :

1. quelles sont les signatures importantes ;
2. quels mots sont dirty ;
3. quels chemins passent par `Result` ;
4. ou sont les quotations ;
5. ou commence l'ABI hote.

## 5. Ecrire du code Nicole

Un workflow d'ecriture efficace en Nicole consiste a partir du contrat puis a faire apparaitre la complexite seulement lorsqu'elle devient necessaire.

### Commencer par la signature

Commencez par ecrire le mot comme si son comportement etait deja compris.

> Fragment illustratif : l'esquisse suivante sert de point de depart de conception. Elle n'est pas encore un mot Nicole valide tant que le corps n'est pas ecrit.

Exemple :

```nicole
module @writer.demo
  : timeout-or-default { cfg:Map<String,Int> -- n:Int }
  ;
end-module
```

Cette premiere etape force deja des decisions utiles :

- faut-il un `Result` ou une valeur simple ;
- faut-il plusieurs sorties ;
- le mot sera-t-il pur ou dirty ;
- quels noms rendent le contrat lisible.

> Note editoriale : les deux signatures suivantes sont legalement possibles. Elles n'offrent pas la meme aide au moment d'ecrire ni au moment de relire.

**Mauvais exemple**

```nicole
module @writing.signature.bad
  : run { x:Int -- y:Int }
    x
  ;
end-module
```

**Pourquoi c'est problematique**

La signature reste correcte, mais elle reporte presque toute l'intention dans le corps et dans le contexte externe. En pratique, elle aide peu le lecteur suivant.

**Meilleur exemple**

```nicole
module @writing.signature.good
  : timeout-or-default { cfg:Map<String,Int> -- timeout:Int }
    cfg "timeout" map.get 30 result.unwrap-or
  ;
end-module
```

**Pourquoi c'est preferable**

La signature sert deja de contrat narratif. On sait quel type de valeur entre, quelle valeur sort et quelle politique generale est mise en oeuvre.

### Ecrire le chemin nominal

Ensuite, ecrivez le cas normal le plus simple.

```nicole
module @writer.demo
  : timeout-or-default { cfg:Map<String,Int> -- n:Int }
    cfg "timeout" map.get case
      Ok(v) => v
      Err(MissingKey) => 30
    end
  ;
end-module
```

Le chemin nominal n'est pas ici "le succes seulement". C'est la forme la plus simple du comportement complet attendu.

> Note editoriale : un chemin nominal lisible ne signifie pas "ignorer les erreurs". Il signifie "ecrire d'abord la forme la plus directe du comportement voulu".

**Mauvais exemple**

```nicole
module @writing.nominal.bad
  : run { cfg:Map<String,Int> -- timeout:Int }
    cfg "timeout" map.get case
      Ok(v) => v
      Err(MissingKey) => 30
    end
  ;
end-module
```

**Pourquoi c'est problematique**

Le code est valide, mais `run` dit peu de chose. Le lecteur comprend le mecanisme avant de comprendre l'intention.

**Meilleur exemple**

```nicole
module @writing.nominal.good
  : timeout-or-default { cfg:Map<String,Int> -- timeout:Int }
    cfg "timeout" map.get case
      Ok(v) => v
      Err(MissingKey) => 30
    end
  ;
end-module
```

**Pourquoi c'est preferable**

Le chemin nominal et le nom se renforcent mutuellement. La relecture devient plus rapide parce que l'intention est visible avant meme le detail de `case`.

### Traiter les `Result`

Quand une operation retourne `Result`, choisissez deliberement :

- inspection locale avec `case` ;
- valeur de repli avec `result.unwrap-or` ;
- propagation locale avec `?`.

Exemple avec propagation :

```nicole
module @writer.demo
  : require-timeout { cfg:Map<String,Int> -- r:Result<Int,MapError> }
    cfg "timeout" map.get ?
    Ok!
  ;
end-module
```

Ici, le mot promet deja un `Result`, donc `?` garde une ecriture lineaire.

> Note editoriale : la spec v1 documente `result.unwrap-or`, pas `result.unwrap`. Le contraste utile porte donc sur l'usage systematique de la forme compacte disponible.

**Mauvais exemple**

```nicole
module @writing.result.bad
  : timeout-or-default { cfg:Map<String,Int> -- timeout:Int }
    cfg "timeout" map.get 30 result.unwrap-or
  ;

  : retries-or-default { cfg:Map<String,Int> -- retries:Int }
    cfg "retries" map.get 3 result.unwrap-or
  ;
end-module
```

**Pourquoi c'est problematique**

Tout resultat est aplati de la meme maniere. Le lecteur ne voit plus si l'absence d'une valeur est une commodite locale, une vraie erreur ou une decision qui devrait rester visible plus haut.

**Meilleur exemple**

```nicole
module @writing.result.good
  : timeout-or-default { cfg:Map<String,Int> -- timeout:Int }
    cfg "timeout" map.get 30 result.unwrap-or
  ;

  : retries-or-default { cfg:Map<String,Int> -- retries:Int }
    cfg "retries" map.get case
      Ok(v) => v
      Err(MissingKey) => 3
    end
  ;

  : require-threshold { cfg:Map<String,Int> -- r:Result<Int,MapError> }
    cfg "threshold" map.get ?
    Ok!
  ;
end-module
```

**Pourquoi c'est preferable**

Le code rend visible trois lectures distinctes. `result.unwrap-or` convient a une valeur de repli triviale, `case` montre une politique locale explicite, et `?` signale que le caller doit encore prendre la decision.

### Isoler les effets

Quand un mot doit parler a l'hote, gardez si possible un helper pur pour la logique puis une petite facade dirty pour l'integration.

```nicole
module @host
  require console.log { msg:String -- } dirty
end-module

module @writer.demo
  import @host.console.log as console.log

  : banner { -- msg:String }
    "ready"
  ;

  dirty : announce { -- }
    banner console.log
  ;
end-module
```

Cette separation rend la relecture plus rapide :

- `banner` calcule ;
- `announce` integre.

> Note editoriale : les deux modules suivants fonctionnent. Leur cout de lecture n'est pas le meme.

**Mauvais exemple**

```nicole
module @host
  require console.log { msg:String -- } dirty
end-module

module @writing.effects.bad
  import @host.console.log as console.log

  dirty : banner { -- msg:String }
    "ready"
    "banner built" console.log
  ;

  dirty : announce { -- msg:String }
    banner
    "ready" console.log
  ;
end-module
```

**Pourquoi c'est problematique**

Le mot `banner` ne fait pourtant aucun effet observable, mais il devient dirty par contagion de style. Le lecteur ne peut plus distinguer rapidement ce qui releve du calcul et ce qui releve de l'integration.

**Meilleur exemple**

```nicole
module @host
  require console.log { msg:String -- } dirty
end-module

module @writing.effects.good
  import @host.console.log as console.log

  : banner { -- msg:String }
    "ready"
  ;

  dirty : announce { -- msg:String }
    banner
    "ready" console.log
  ;
end-module
```

**Pourquoi c'est preferable**

Le helper pur garde un contrat leger et reutilisable. Le mot dirty reste la facade qui signale explicitement ou l'hote intervient.

### Exporter ensuite

N'ouvrez une surface `export` qu'une fois le comportement interne stable.

```nicole
module @app
  : run { input:String -- output:String }
    input
  ;
  export : run
end-module
```

Un petit bon reflexe :

1. stabiliser les helpers internes ;
2. verifier la signature exportee ;
3. verifier si le mot doit etre dirty ;
4. verifier que rien d'interdit ne traverse l'ABI.

> Note editoriale : ce contraste ne dit pas qu'il faut toujours un seul export. Il montre pourquoi une facade reduite se relit plus facilement.

**Mauvais exemple**

```nicole
module @writing.exports.bad
  : timeout-or-default { cfg:Map<String,Int> -- timeout:Int }
    cfg "timeout" map.get 30 result.unwrap-or
  ;

  : timeout-ready { cfg:Map<String,Int> -- ok:Bool }
    cfg timeout-or-default 0 >
  ;

  : timeout-message { cfg:Map<String,Int> -- msg:String }
    cfg timeout-ready
    drop
    "timeout ready"
  ;

  export : timeout-or-default
  export : timeout-ready
  export : timeout-message
end-module
```

**Pourquoi c'est problematique**

La surface hote grossit vite, y compris avec des helpers qui existent surtout pour la composition interne. Le lecteur doit alors distinguer lui-meme ce qui est public par besoin reel et ce qui l'est par commodite.

**Meilleur exemple**

```nicole
module @writing.exports.good
  : timeout-or-default { cfg:Map<String,Int> -- timeout:Int }
    cfg "timeout" map.get 30 result.unwrap-or
  ;

  : timeout-ready { cfg:Map<String,Int> -- ok:Bool }
    cfg timeout-or-default 0 >
  ;

  : run { cfg:Map<String,Int> -- ok:Bool }
    cfg timeout-ready
  ;

  export : run
end-module
```

**Pourquoi c'est preferable**

La facade exportee donne un point d'entree clair. Les helpers restent lisibles dans le module sans devenir automatiquement des engagements ABI.

## 6. Patterns recommandes

Les patterns ci-dessous ne sont pas des conventions officielles. Ils collent simplement bien aux choix visibles du langage.

### Helper pur + facade dirty

Probleme :

le code d'integration peut rapidement melanger calcul, log, lecture de configuration et publication.

Solution :

ecrire la logique en pur, puis envelopper cette logique dans un petit mot dirty.

Exemple :

```nicole
module @host
  require console.log { msg:String -- } dirty
end-module

module @patterns.helper
  import @host.console.log as console.log

  : status-message { ok:Bool -- msg:String }
    ok if
      "ok"
    else
      "error"
    end
  ;

  dirty : log-status { ok:Bool -- }
    ok status-message console.log
  ;
end-module
```

Pourquoi cela fonctionne bien en Nicole :

- la logique pure reste simple a tester mentalement ;
- la propagation de `dirty` reste visible ;
- l'ABI hote reste concentree dans peu de mots.

> Note editoriale : ce pattern exploite surtout deux proprietes du langage. Les signatures restent stables d'un helper a l'autre, et `dirty` marque une vraie frontiere au lieu d'etre diffuse partout.

**Mauvais exemple**

```nicole
module @host
  require console.log { msg:String -- } dirty
end-module

module @patterns.helper.bad
  import @host.console.log as console.log

  dirty : status-message { ok:Bool -- msg:String }
    ok if
      "ok"
    else
      "error"
    end
    "status computed" console.log
  ;

  dirty : log-status { ok:Bool -- msg:String }
    ok status-message
    "status ready" console.log
  ;
end-module
```

**Pourquoi c'est problematique**

Le lecteur voit `dirty` deux fois alors qu'un seul mot parle reellement a l'hote. Le raisonnement local devient plus brouille que necessaire.

**Meilleur exemple**

```nicole
module @host
  require console.log { msg:String -- } dirty
end-module

module @patterns.helper.good
  import @host.console.log as console.log

  : status-message { ok:Bool -- msg:String }
    ok if
      "ok"
    else
      "error"
    end
  ;

  dirty : log-status { ok:Bool -- msg:String }
    ok status-message
    "status ready" console.log
  ;
end-module
```

**Pourquoi c'est preferable**

Le helper pur exploite l'immutabilite locale et la signature explicite pour rester autonome. La facade dirty devient le seul endroit a surveiller quand on suit la frontiere d'integration.

### Validation puis execution

Probleme :

quand un calcul depend d'une lecture qui peut echouer, il est facile de disperser la gestion d'erreur.

Solution :

valider ou extraire d'abord, executer ensuite.

Exemple :

```nicole
module @patterns.validation
  : require-timeout-flag { cfg:Map<String,Int> -- r:Result<Int,MapError> }
    cfg "timeout" map.get ?
    drop
    1 Ok!
  ;
end-module
```

Pourquoi cela fonctionne bien en Nicole :

- la signature annonce clairement l'echec possible ;
- `?` garde un chemin lineaire ;
- la frame reste localement lisible.

> Note editoriale : ce pattern exploite le fait que `?` suit la frame courante et que les signatures de `Result` rendent l'echec visible avant meme de lire le corps.

**Mauvais exemple**

```nicole
module @patterns.validation.bad
  : timeout-positive { cfg:Map<String,Int> -- r:Result<Bool,MapError> }
    cfg "timeout" map.get ?
    0 >
    Ok!
  ;
end-module
```

**Pourquoi c'est problematique**

Le mot reste correct, mais il melange extraction et validation dans le meme bloc. Le lecteur doit suivre deux decisions a la fois au lieu de lire une etape de validation puis une etape d'execution.

**Meilleur exemple**

```nicole
module @patterns.validation.good
  : require-timeout { cfg:Map<String,Int> -- r:Result<Int,MapError> }
    cfg "timeout" map.get ?
    Ok!
  ;

  : timeout-positive { cfg:Map<String,Int> -- r:Result<Bool,MapError> }
    cfg require-timeout ?
    0 >
    Ok!
  ;
end-module
```

**Pourquoi c'est preferable**

La validation s'appuie sur les proprietes de frame de `?`. Chaque mot gere une seule decision et la relecture suit un chemin plus court.

### Configuration avec valeurs par defaut

Probleme :

beaucoup de configurations sont optionnelles sans etre exceptionnelles.

Solution :

utiliser `case` ou `result.unwrap-or` pour transformer un `Result` en valeur simple a un point bien choisi.

Exemple :

```nicole
module @patterns.config
  : timeout-or-default { cfg:Map<String,Int> -- n:Int }
    cfg "timeout" map.get 30 result.unwrap-or
  ;
end-module
```

Pourquoi cela fonctionne bien en Nicole :

- la valeur de repli reste locale ;
- le reste du module peut ensuite travailler sur des valeurs simples ;
- le `Result` n'est pas force de se propager partout.

> Note editoriale : ce pattern exploite le fait qu'un `Result` peut etre converti en valeur simple a un point bien choisi, puis disparaitre du reste du flux.

**Mauvais exemple**

```nicole
module @patterns.config.bad
  : read-timeout { cfg:Map<String,Int> -- r:Result<Int,MapError> }
    cfg "timeout" map.get
  ;

  : timeout-or-default { r:Result<Int,MapError> -- timeout:Int }
    r 30 result.unwrap-or
  ;
end-module
```

**Pourquoi c'est problematique**

Le `Result` circule plus loin que necessaire. Le lecteur doit retenir un etat intermediaire alors que la politique de repli est pourtant purement locale.

**Meilleur exemple**

```nicole
module @patterns.config.good
  : timeout-or-default { cfg:Map<String,Int> -- timeout:Int }
    cfg "timeout" map.get 30 result.unwrap-or
  ;
end-module
```

**Pourquoi c'est preferable**

La normalisation se fait au point d'entree du besoin. Le reste du code exploite ensuite une valeur simple, plus facile a composer et a relire.

### Pipeline de transformations

Probleme :

les traitements de listes deviennent vite bruyants si on melange tout dans un seul mot.

Solution :

assembler un petit pipeline de mots purs et de quotations courtes.

Exemple :

```nicole
module @patterns.pipeline
  : inc-all { xs:List<Int> -- ys:List<Int> }
    xs :[ | x:Int -- y:Int | x 1 + ;] list.map
  ;

  : keep-positive { xs:List<Int> -- ys:List<Int> }
    xs :[ | x:Int -- keep:Bool | x 0 > ;] list.filter
  ;

  : process { xs:List<Int> -- ys:List<Int> }
    xs inc-all keep-positive
  ;
end-module
```

Pourquoi cela fonctionne bien en Nicole :

- chaque mot garde un contrat simple ;
- les quotations restent courtes ;
- la composition concaténative reste directe.

> Note editoriale : ce pattern exploite la composition concaténative et le fait que les builtins de collections lisent tres bien des quotations courtes reliees a des helpers nommes.

**Mauvais exemple**

```nicole
module @patterns.pipeline.bad
  : process { xs:List<Int> -- ys:List<Int> }
    xs :[ | x:Int -- y:Int |
      x 1 +
      0 >
      if
        x 1 +
      else
        0
      end
    ;] list.map
  ;
end-module
```

**Pourquoi c'est problematique**

La lecture doit reconstituer plusieurs intentions en une seule quotation. On perd le benefice d'un pipeline ou chaque etape porte un nom et un contrat.

**Meilleur exemple**

```nicole
module @patterns.pipeline.good
  : inc-all { xs:List<Int> -- ys:List<Int> }
    xs :[ | x:Int -- y:Int | x 1 + ;] list.map
  ;

  : keep-positive { xs:List<Int> -- ys:List<Int> }
    xs :[ | x:Int -- keep:Bool | x 0 > ;] list.filter
  ;

  : process { xs:List<Int> -- ys:List<Int> }
    xs inc-all keep-positive
  ;
end-module
```

**Pourquoi c'est preferable**

Chaque etape exploite une propriete claire du langage : une signature courte, une frame locale petite et une quotation specialisee pour un seul builtin de collection.

### Quotations locales courtes

Probleme :

une quotation trop riche devient difficile a lire et a typer.

Solution :

garder les quotations proches de leur usage et courtes en nombre d'operations.

Exemple :

```nicole
module @patterns.quotes
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

Pourquoi cela fonctionne bien en Nicole :

- les captures restent visibles ;
- la partie appelable reste evidente ;
- la logique ne fuit pas dans un mecanisme implicite.

> Note editoriale : ce pattern exploite la separation nette entre captures et inputs. Plus la quotation est courte, plus cette separation reste facile a verifier a l'oeil.

**Mauvais exemple**

```nicole
module @patterns.quotes.bad
  : normalize-reportable { xs:List<Int> threshold:Int -- ys:List<Int> }
    xs
    threshold
    :[ threshold:Int | x:Int -- y:Int |
      x 1 +
      threshold >
      if
        x 1 +
      else
        0
      end
    ;]
    list.map
  ;
end-module
```

**Pourquoi c'est problematique**

La capture et la logique de decision s'entassent dans le meme bloc. La quotation devient difficile a scanner sans relire plusieurs fois son contrat.

**Meilleur exemple**

```nicole
module @patterns.quotes.good
  : adjust-or-zero { x:Int threshold:Int -- y:Int }
    x 1 + threshold >
    if
      x 1 +
    else
      0
    end
  ;

  : normalize-reportable { xs:List<Int> threshold:Int -- ys:List<Int> }
    xs
    threshold
    :[ threshold:Int | x:Int -- y:Int |
      x threshold adjust-or-zero
    ;]
    list.map
  ;
end-module
```

**Pourquoi c'est preferable**

La quotation exploite exactement ce que Nicole rend explicite : une capture typée et un petit contrat appelable. Le raisonnement local redevient court.

### API exportee minimale

Probleme :

une surface exportee trop large devient difficile a stabiliser et a relire.

Solution :

exposer peu de mots, avec des signatures simples, et garder les details dans les helpers internes.

Exemple :

```nicole
module @app
  : run { input:String -- output:String }
    input
  ;
  export : run
end-module
```

Pourquoi cela fonctionne bien en Nicole :

- la frontiere hote reste lisible ;
- les types ABI visibles sont faciles a revoir ;
- les changements internes se diffusent moins loin.

> Note editoriale : ce pattern exploite la distinction explicite entre mots internes et surface `export`. Rien n'oblige a exposer les helpers juste parce qu'ils sont pratiques.

**Mauvais exemple**

```nicole
module @patterns.exports.bad
  : timeout-or-default { cfg:Map<String,Int> -- timeout:Int }
    cfg "timeout" map.get 30 result.unwrap-or
  ;

  : timeout-ready { cfg:Map<String,Int> -- ok:Bool }
    cfg timeout-or-default 0 >
  ;

  : run { cfg:Map<String,Int> -- ok:Bool }
    cfg timeout-ready
  ;

  export : timeout-or-default
  export : timeout-ready
  export : run
end-module
```

**Pourquoi c'est problematique**

Le lecteur ne sait plus quels mots font partie de l'API voulue et quels mots existent surtout pour la composition interne.

**Meilleur exemple**

```nicole
module @patterns.exports.good
  : timeout-or-default { cfg:Map<String,Int> -- timeout:Int }
    cfg "timeout" map.get 30 result.unwrap-or
  ;

  : timeout-ready { cfg:Map<String,Int> -- ok:Bool }
    cfg timeout-or-default 0 >
  ;

  : run { cfg:Map<String,Int> -- ok:Bool }
    cfg timeout-ready
  ;

  export : run
end-module
```

**Pourquoi c'est preferable**

L'API exportee reste minimale et la lecture du module suit mieux les responsabilites : helpers internes d'abord, point d'entree ensuite.

## 7. Anti-patterns

Les anti-patterns ci-dessous n'enfreignent pas tous une regle formelle. Ils nuisent surtout a la lisibilite et au raisonnement local.

### Quotations trop complexes

Pourquoi cela apparait :

les quotations sont pratiques, donc il est tentant d'y mettre toute une logique de traitement.

Pourquoi cela nuit :

- les captures, inputs et effets deviennent difficiles a suivre ;
- la quotation ressemble a un module miniature cache ;
- la lecture du code appelant se charge inutilement.

Alternative recommandee :

- extraire un helper nomme quand la logique devient longue ;
- garder la quotation comme colle locale entre le builtin et un petit calcul.

> Note editoriale : ce n'est pas une interdiction des quotations longues. C'est un contraste de maintenabilite.

**Mauvais exemple**

```nicole
module @anti.quotes.bad
  : normalize-reportable { xs:List<Int> threshold:Int -- ys:List<Int> }
    xs
    threshold
    :[ threshold:Int | x:Int -- y:Int |
      x 1 +
      threshold >
      if
        x 1 +
      else
        0
      end
    ;]
    list.map
  ;
end-module
```

**Pourquoi c'est problematique**

La quotation porte a elle seule presque toute la logique du mot. Toute modification future oblige a revalider la capture, la signature locale et le calcul dans un meme bloc.

**Meilleur exemple**

```nicole
module @anti.quotes.good
  : adjust-or-zero { x:Int threshold:Int -- y:Int }
    x 1 + threshold >
    if
      x 1 +
    else
      0
    end
  ;

  : normalize-reportable { xs:List<Int> threshold:Int -- ys:List<Int> }
    xs
    threshold
    :[ threshold:Int | x:Int -- y:Int |
      x threshold adjust-or-zero
    ;]
    list.map
  ;
end-module
```

**Pourquoi c'est preferable**

Le helper porte le calcul et la quotation redevient un simple adaptateur local. Le changement de seuil ou de formule devient plus localise.

### Propagation excessive de `dirty`

Pourquoi cela apparait :

une fois qu'un mot est dirty, il semble plus simple de laisser d'autres mots le devenir aussi.

Pourquoi cela nuit :

- la frontiere entre calcul et integration disparait ;
- la relecture du graphe d'effets devient plus lourde ;
- une grande partie du module devient dependante de l'hote.

Alternative recommandee :

- garder des helpers purs ;
- concentrer l'integration dans peu de facades dirty ;
- remonter l'effet seulement quand c'est necessaire.

> Note editoriale : ce contraste montre surtout comment `dirty` affecte la lecture du graphe de dependances.

**Mauvais exemple**

```nicole
module @host
  require console.log { msg:String -- } dirty
end-module

module @anti.dirty.bad
  import @host.console.log as console.log

  dirty : threshold-or-default { cfg:Map<String,Int> -- threshold:Int }
    cfg "threshold" map.get 10 result.unwrap-or
    "threshold computed" console.log
  ;

  dirty : announce-threshold { cfg:Map<String,Int> -- threshold:Int }
    cfg threshold-or-default
    "threshold ready" console.log
  ;
end-module
```

**Pourquoi c'est problematique**

Le helper `threshold-or-default` semble dependre de l'hote alors qu'il ne fait qu'un calcul local. Le lecteur surestime alors la zone a risque et perd le benefice de la separation pur / dirty.

**Meilleur exemple**

```nicole
module @host
  require console.log { msg:String -- } dirty
end-module

module @anti.dirty.good
  import @host.console.log as console.log

  : threshold-or-default { cfg:Map<String,Int> -- threshold:Int }
    cfg "threshold" map.get 10 result.unwrap-or
  ;

  dirty : announce-threshold { cfg:Map<String,Int> -- threshold:Int }
    cfg threshold-or-default
    "threshold ready" console.log
  ;
end-module
```

**Pourquoi c'est preferable**

La propagation de `dirty` s'arrete a la vraie frontiere d'integration. Le calcul pur reste reutilisable et plus simple a lire.

### Usage systematique de `result.unwrap-or`

Pourquoi cela apparait :

`result.unwrap-or` est concis et tentant.

Pourquoi cela nuit :

- on perd parfois la structure de l'erreur ;
- des decisions de repli differentes deviennent invisibles ;
- un `case` detaille serait plus honnête pour le lecteur.

Alternative recommandee :

- utiliser `case` quand la variante d'erreur a une importance semantique ;
- reserver `result.unwrap-or` aux vrais cas de valeur par defaut simple.

> Note editoriale : la question n'est pas de bannir `result.unwrap-or`, mais d'eviter qu'il devienne le reflexe unique.

**Mauvais exemple**

```nicole
module @anti.result.bad
  : timeout-or-default { cfg:Map<String,Int> -- timeout:Int }
    cfg "timeout" map.get 30 result.unwrap-or
  ;

  : threshold-or-default { cfg:Map<String,Int> -- threshold:Int }
    cfg "threshold" map.get 50 result.unwrap-or
  ;

  : retries-or-default { cfg:Map<String,Int> -- retries:Int }
    cfg "retries" map.get 3 result.unwrap-or
  ;
end-module
```

**Pourquoi c'est problematique**

Toutes les decisions d'erreur prennent la meme forme, qu'elles soient triviales ou non. Le lecteur ne voit plus quels defaults sont vraiment anodins et lesquels meriteraient une lecture explicite.

**Meilleur exemple**

```nicole
module @anti.result.good
  : timeout-or-default { cfg:Map<String,Int> -- timeout:Int }
    cfg "timeout" map.get 30 result.unwrap-or
  ;

  : threshold-or-default { cfg:Map<String,Int> -- threshold:Int }
    cfg "threshold" map.get case
      Ok(v) => v
      Err(MissingKey) => 50
    end
  ;

  : require-retries { cfg:Map<String,Int> -- r:Result<Int,MapError> }
    cfg "retries" map.get ?
    Ok!
  ;
end-module
```

**Pourquoi c'est preferable**

Le code distingue trois politiques : valeur de repli compacte, branchement explicite, et propagation au caller. Cette distinction aide le lecteur a comprendre l'intention de chaque mot.

### Exports trop nombreux

Pourquoi cela apparait :

il peut sembler naturel d'exporter tous les mots utiles a l'hote.

Pourquoi cela nuit :

- la frontiere ABI gonfle ;
- les contrats visibles cote hote deviennent plus difficiles a stabiliser ;
- le module ressemble moins a une facade qu'a une fuite d'implementation.

Alternative recommandee :

- exporter peu de points d'entree ;
- garder les helpers non exportes ;
- construire une petite API hote deliberate.

> Note editoriale : ce contraste parle de surface publique, pas de purete stylistique.

**Mauvais exemple**

```nicole
module @anti.exports.bad
  : timeout-or-default { cfg:Map<String,Int> -- timeout:Int }
    cfg "timeout" map.get 30 result.unwrap-or
  ;

  : timeout-ready { cfg:Map<String,Int> -- ok:Bool }
    cfg timeout-or-default 0 >
  ;

  : timeout-message { cfg:Map<String,Int> -- msg:String }
    cfg timeout-ready
    drop
    "timeout ready"
  ;

  : run { cfg:Map<String,Int> -- ok:Bool }
    cfg timeout-ready
  ;

  export : timeout-or-default
  export : timeout-ready
  export : timeout-message
  export : run
end-module
```

**Pourquoi c'est problematique**

Le module expose ses pieces internes presque telles quelles. Toute evolution des helpers risque alors de devenir une question ABI alors qu'elle devrait rester interne.

**Meilleur exemple**

```nicole
module @anti.exports.good
  : timeout-or-default { cfg:Map<String,Int> -- timeout:Int }
    cfg "timeout" map.get 30 result.unwrap-or
  ;

  : timeout-ready { cfg:Map<String,Int> -- ok:Bool }
    cfg timeout-or-default 0 >
  ;

  : run { cfg:Map<String,Int> -- ok:Bool }
    cfg timeout-ready
  ;

  export : run
end-module
```

**Pourquoi c'est preferable**

Le point d'entree public reste stable et lisible. Les helpers peuvent evoluer sans transformer chaque refactor en modification de surface exportee.

### Signatures peu informatives

Pourquoi cela apparait :

quand on ecrit vite, on peut garder des noms trop generiques dans les signatures.

Pourquoi cela nuit :

- le contrat se lit moins bien ;
- les locals n'aident plus a comprendre le flux ;
- l'intention du mot se deplace dans le corps au lieu d'apparaitre des la premiere ligne.

Alternative recommandee :

- nommer les entrees selon leur role ;
- utiliser des noms de sortie documentaires utiles ;
- preferer `timeout-or-default` a un nom abstrait du genre `run2`.

> Note editoriale : la difference ci-dessous est purement editoriale. Les deux signatures sont acceptables pour le langage.

**Mauvais exemple**

```nicole
module @anti.signatures.bad
  : run { x:Map<String,Int> -- y:Int }
    x "timeout" map.get 30 result.unwrap-or
  ;

  : process { data:List<Int> -- out:List<Int> }
    data :[ | x:Int -- y:Int | x 1 + ;] list.map
  ;
end-module
```

**Pourquoi c'est problematique**

Les noms generiques masquent le role des donnees. Le lecteur comprend la mecanique mais pas ce qui compte vraiment dans le module.

**Meilleur exemple**

```nicole
module @anti.signatures.good
  : timeout-or-default { cfg:Map<String,Int> -- timeout:Int }
    cfg "timeout" map.get 30 result.unwrap-or
  ;

  : increment-all { scores:List<Int> -- updated-scores:List<Int> }
    scores :[ | score:Int -- updated-score:Int | score 1 + ;] list.map
  ;
end-module
```

**Pourquoi c'est preferable**

Les noms servent directement de documentation locale. La signature devient un resume fiable au lieu d'un simple decor de types.

### Gros modules monolithiques

Pourquoi cela apparait :

Nicole permet d'enchainer beaucoup de logique dans un seul module.

Pourquoi cela nuit :

- imports, effets, helpers et exports se melangent ;
- la lecture du module devient plus lineaire que structuree ;
- la surface hote, le calcul pur et les transformations de collections se croisent trop.

Alternative recommandee :

- separer par responsabilite ;
- regrouper le calcul pur ;
- isoler les facades d'integration.

> Note editoriale : la spec ne fixe pas une taille officielle de module. Le contraste suivant montre seulement ce qui devient plus ou moins facile a maintenir.

**Mauvais exemple**

```nicole
module @host
  require console.log { msg:String -- } dirty
  require config.get-int { key:String -- r:Result<Int,MapError> } pure
end-module

module @anti.monolith.bad
  import @host.console.log as console.log
  import @host.config.get-int as config.get-int

  : timeout-or-default { -- timeout:Int }
    "timeout" config.get-int 30 result.unwrap-or
  ;

  : increment-all { xs:List<Int> -- ys:List<Int> }
    xs :[ | x:Int -- y:Int | x 1 + ;] list.map
  ;

  dirty : run { xs:List<Int> -- ys:List<Int> }
    "running" console.log
    xs increment-all
  ;

  export : timeout-or-default
  export : increment-all
  export : run
end-module
```

**Pourquoi c'est problematique**

Configuration, transformations de collections, integration hote et surface exportee se retrouvent dans le meme bloc. Le lecteur doit constamment changer de niveau de lecture.

**Meilleur exemple**

```nicole
module @host
  require console.log { msg:String -- } dirty
  require config.get-int { key:String -- r:Result<Int,MapError> } pure
end-module

module @anti.monolith.config
  import @host.config.get-int as config.get-int

  : timeout-or-default { -- timeout:Int }
    "timeout" config.get-int 30 result.unwrap-or
  ;
end-module

module @anti.monolith.transforms
  : increment-all { xs:List<Int> -- ys:List<Int> }
    xs :[ | x:Int -- y:Int | x 1 + ;] list.map
  ;
end-module

module @anti.monolith.app
  import @host.console.log as console.log
  import @anti.monolith.transforms.increment-all as increment-all

  dirty : run { xs:List<Int> -- ys:List<Int> }
    "running" console.log
    xs increment-all
  ;

  export : run
end-module
```

**Pourquoi c'est preferable**

Chaque module exploite mieux les proprietes visibles du langage : imports explicites, roles plus nets, et frontiere ABI plus facile a localiser.

## 8. Organisation d'un projet

La specification ne fixe pas de structure de depot officielle. Les organisations suivantes sont donc seulement des exemples plausibles.

> Note editoriale : choisissez une structure qui rend visibles les frontieres de votre projet. Nicole beneficie surtout d'un decoupage qui se lit bien par module, par effet et par frontiere hote.

### Organisation par couches fonctionnelles

```text
src/
  core/
  config/
  services/
  host/
```

Lecture possible :

- `core/` contient le calcul pur ;
- `config/` contient les lectures et normalisations de configuration ;
- `services/` contient les facades applicatives ;
- `host/` regroupe les modules lies aux points d'integration.

Cette organisation marche bien quand le projet oppose clairement domaine interne et adaptation hote.

### Organisation par architecture application / adapters

```text
src/
  domain/
  application/
  adapters/
```

Lecture possible :

- `domain/` garde les transformations pures et les types conceptuels ;
- `application/` compose les cas d'usage ;
- `adapters/` contient les facades qui parlent a l'hote.

Cette organisation marche bien quand le projet a plusieurs points d'entree ou plusieurs integrations.

### Organisation minimale pour petit projet

```text
src/
  config.nic
  transforms.nic
  service.nic
  host_contract.nic
```

Cette forme simple reste valable si :

- les modules sont peu nombreux ;
- la frontiere dirty reste courte ;
- la responsabilite de chaque fichier reste claire.

### Ce qu'il vaut mieux rendre visible

Quel que soit le decoupage, il est utile que le lecteur repere vite :

- ou vivent les declarations `module @host` ;
- quels modules sont surtout purs ;
- quels modules portent les exports ;
- ou passent les transformations de collections ;
- ou les `Result` sont inspectes ou propages.

## 9. Etude de cas complete

Cette etude de cas propose un petit service de traitement de scores.

Le but n'est pas de definir une architecture officielle, mais de montrer un assemblage realiste de pieces deja presentes dans la specification :

- plusieurs modules ;
- imports utilisateur et imports hote ;
- collections ;
- `Result` ;
- quotations ;
- ABI explicite ;
- exports ;
- map de statistiques en sortie.

> Note editoriale : le code ci-dessous sert d'exemple de pratique. Il n'ajoute aucune nouvelle regle au langage.

### Code complet

```nicole
module @host
  require console.log { msg:String -- } dirty
  require config.get-int { key:String -- r:Result<Int,MapError> } pure
  require scores.load { -- r:Result<List<Int>,String> } dirty
  require scores.store { xs:List<Int> -- } dirty
end-module

module @guide.case.config
  import @host.config.get-int as config.get-int

  pub : bonus-or-default { -- n:Int }
    "bonus" config.get-int 0 result.unwrap-or
  ;

  pub : threshold-or-default { -- n:Int }
    "threshold" config.get-int 50 result.unwrap-or
  ;

  pub : config-summary { -- cfg:Map<String,Int> }
    map.empty:Map<String,Int>
    "bonus" bonus-or-default map.set
    "threshold" threshold-or-default map.set
  ;
end-module

module @guide.case.scores
  import @guide.case.config.bonus-or-default as bonus-or-default
  import @guide.case.config.threshold-or-default as threshold-or-default

  pub : apply-bonus { xs:List<Int> -- ys:List<Int> }
    xs
    bonus-or-default
    :[ bonus:Int | x:Int -- y:Int |
      x bonus +
    ;]
    list.map
  ;

  pub : keep-reportable { xs:List<Int> -- ys:List<Int> }
    xs
    threshold-or-default
    :[ minimum:Int | x:Int -- keep:Bool |
      x minimum >=
    ;]
    list.filter
  ;

  pub : count-reportable { xs:List<Int> -- n:Int }
    xs
    0
    :[ | acc:Int x:Int -- out:Int |
      acc 1 +
    ;]
    list.fold
  ;

  pub : total { xs:List<Int> -- n:Int }
    xs
    0
    :[ | acc:Int x:Int -- out:Int |
      acc x +
    ;]
    list.fold
  ;

  pub : first-reportable { xs:List<Int> -- r:Result<Int,ListError> }
    xs keep-reportable list.first
  ;

  pub : prepare { xs:List<Int> -- ys:List<Int> }
    xs apply-bonus keep-reportable
  ;
end-module

module @guide.case.stats
  import @guide.case.config.config-summary as config-summary
  import @guide.case.scores.count-reportable as count-reportable
  import @guide.case.scores.total as total

  pub : summary { xs:List<Int> -- stats:Map<String,Int> }
    config-summary
    "count" xs count-reportable map.set
    "total" xs total map.set
  ;
end-module

module @guide.case.service
  import @host.console.log as console.log
  import @host.scores.load as scores.load
  import @host.scores.store as scores.store
  import @guide.case.scores.first-reportable as first-reportable
  import @guide.case.scores.prepare as prepare
  import @guide.case.stats.summary as summary

  dirty : refresh { -- r:Result<Map<String,Int>,String> }
    "loading scores" console.log
    scores.load ?
    prepare
    dup first-reportable case
      Ok(v) => "reportable score found" console.log
      Err(OutOfBounds) => "no reportable score" console.log
    end
    "storing scores" console.log
    dup scores.store
    summary Ok!
  ;
  export : refresh

  dirty : preview { -- r:Result<Map<String,Int>,String> }
    "loading scores" console.log
    scores.load ?
    prepare
    summary Ok!
  ;
  export : preview
end-module
```

### Lecture par sections

#### 1. `module @host`

Ce module declare clairement la frontiere externe :

- `console.log` est dirty ;
- `config.get-int` est pure ;
- `scores.load` retourne un `Result<List<Int>,String>` ;
- `scores.store` est un effet hote sans retour normal.

Le lecteur sait deja, avant de voir le reste, quels mots devront devenir dirty et ou les `Result` importants entreront.

#### 2. `@guide.case.config`

Ce module convertit une lecture de configuration hote en valeurs simples et reutilisables.

Points a remarquer :

- les mots sont `pub` parce qu'ils seront importes ailleurs ;
- `result.unwrap-or` suffit ici parce que le traitement ne depend pas du detail de l'erreur ;
- `config-summary` produit une `Map<String,Int>` purement Nicole, facile a reutiliser ailleurs.

#### 3. `@guide.case.scores`

Ce module concentre le calcul pur sur les listes.

Points a remarquer :

- `apply-bonus` et `keep-reportable` montrent deux quotations courtes, chacune capture une seule valeur ;
- `count-reportable` et `total` utilisent `list.fold` pour garder des transformations nommees et lisibles ;
- `first-reportable` reintroduit un `Result` local, ici base sur `ListError` ;
- `prepare` assemble le pipeline sans effet hote.

#### 4. `@guide.case.stats`

Ce module montre comment construire une petite sortie structuree a partir d'une liste preparee.

Points a remarquer :

- `summary` reutilise `config-summary` plutot que de relire la configuration autrement ;
- la sortie `Map<String,Int>` reste ABI-compatible ;
- les stats calculees restent pures et donc faciles a recomposer.

#### 5. `@guide.case.service`

Ce module assemble le tout et expose l'API hote.

Points a remarquer :

- `refresh` et `preview` sont dirty parce qu'ils chargent des scores et journalisent ;
- `scores.load ?` garde un chemin nominal lineaire pour l'erreur `String` ;
- le `case` sur `first-reportable` sert ici a produire deux logs differents, sans changer le contrat de retour ;
- `summary Ok!` construit une sortie `Result<Map<String,Int>,String>` stable pour l'hote ;
- les deux exports exposent une facade minimale sur des helpers plus fins.

### Ce que l'etude de cas montre bien

- l'effet hote reste concentre dans un petit module service ;
- les quotations restent locales et courtes ;
- le domaine manipule surtout des valeurs Nicole ordinaires ;
- les `Result` ne sont pas utilises partout de la meme facon ;
- la frontiere ABI reste explicite, lisible et relativement mince.

## 10. Questions frequentes

### Pourquoi les locals sont-ils immuables ?

Observation de conception :

- les entrees deviennent des noms stables ;
- les sous-mots ne capturent pas implicitement les locals d'un parent ;
- les quotations capturent par valeur.

Cela suggere que Nicole prefere des contrats de frame faciles a relire plutot qu'un modele de variables evolutives.

### Pourquoi utiliser `Result` ?

Observation de conception :

- `map.get`, `map.remove`, `list.first`, `list.last`, `list.get` et `list.set` modelisent des echecs normaux avec `Result` ;
- `case` et `?` donnent deux manieres explicites de le traiter.

Le langage semble donc privilegier une representation visible des echecs normaux plutot qu'un mecanisme implicite.

### Pourquoi une quotation ne capture-t-elle pas tout l'environnement ?

Observation de conception :

- les captures sont declarees explicitement ;
- il n'y a pas de capture lexicale implicite ;
- une quotation possede sa propre frame.

Cela semble viser la lisibilite locale : un lecteur voit exactement quelles valeurs sont embarquees dans la quotation.

### Pourquoi les effets sont-ils explicites ?

Observation de conception :

- `dirty` se propage statiquement ;
- `pure` n'existe en source que dans l'ABI `require` ;
- les builtins structurels restent purs sauf si une `DirtyQuote` les rend dirty au point d'appel.

Cela rend visible la frontiere entre calcul et integration.

### Pourquoi l'ABI est-elle separee ?

Observation de conception :

- `module @host` declare les capacites et les types opaques ;
- `export` expose les mots Nicole vers l'hote ;
- les appels `host.*` directs sont interdits.

La frontiere hote n'est donc pas un detail d'implementation. Elle fait partie du modele de langage.

### Pourquoi `?` ne traverse-t-il pas `list.map` ou `call` ?

Observation de conception :

- `?` est explicitement frame-local ;
- les builtins d'ordre superieur consomment une quotation deja construite ;
- une quotation reste une frame distincte.

Cela preserve un raisonnement local par contrat de frame au lieu d'introduire une propagation inter-frame implicite.

### Pourquoi les quotations ne franchissent-elles pas l'ABI ?

Observation de conception :

- `HOST_ABI.md` limite l'ABI a des valeurs de donnees et types opaques declares ;
- callbacks, quotations et handles executables sont explicitement differes.

Le guide n'en deduit pas davantage : la specification fixe seulement cette limite actuelle.

## 11. Limites connues et points ouverts

Cette section rassemble les zones differees, ambiguities et non-objectifs visibles dans le depot. Elle ne cherche pas a les resoudre.

### TODO(spec) explicites ou equivalents

1. `include` existe en syntaxe, mais sa semantique detaillee de mapping fichiers/chemins reste differee.
2. Le litteral concret eventuel de `Unit` n'est pas encore fixe.
3. La couverture non exhaustive de `case` sur `Bool` est formulee differemment selon `SEMANTIQUE.md`, `INVALID_EXAMPLES.md` et le comportement confirme par les tests du checker.

### Fonctions et surfaces explicitement differees

- `result.unwrap`
- `result.map`
- `result.map-err`
- `result.and-then`
- `result.match`
- `list.try-map`
- `list.try-filter`
- `list.try-fold`
- `map.has`
- `map.to-list`
- `map.entries`
- `map.items`
- `map.map`
- `map.filter`
- `map.fold`
- `list.zip`

### Limites connues de l'ABI v1

- pas de quotations a l'entree ou a la sortie de l'ABI ;
- pas d'alias de types opaques hote ;
- pas de wildcard imports ;
- pas de mecanisme d'ownership ou de finalisation automatique documente pour les types opaques hote ;
- pas de protocole concret de serialisation ou de ABI binaire ;
- pas de callback hote base sur quotations.

### Points ou le guide evite volontairement de speculer

- organisation officielle d'un depot Nicole ;
- intentions de performance ;
- futures extensions de la bibliotheque standard ;
- conventions de packaging autour de `include` ;
- semantique d'une eventuelle execution autonome hors hote ;
- politique future concernant les callbacks ABI et les aliases de types opaques.
