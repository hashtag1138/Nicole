# DESIGN_NOTES.md

# Result Ergonomics Phase 1

## Statut

Cette note consolide une évolution compatible avec la spécification actuelle.

Elle ne remplace pas `SYNTAXE.md`, `SEMANTIQUE.md` ni `HOST_ABI.md`.

Elle décrit une direction de spécification à intégrer explicitement dans les sources normatives quand cette évolution sera ratifiée.

## Audit de compatibilité

La spécification actuelle définit déjà :

- `Result<V,E>` avec les variantes `Ok(v)` et `Err(e)`
- `case` comme mécanisme normal d’inspection de `Result`
- les quotations comme frames isolées avec captures par valeur
- `call` comme exécution d’une quotation dans sa propre frame
- `list.map`, `list.fold` et `list.reduce` comme builtins consommant une quotation déjà construite

La spécification actuelle ne définit pas encore :

- l’opérateur `?`
- les helpers `result.is-ok`, `result.is-err`, `result.unwrap-or`
- des builtins de collection à court-circuit implicite comme `list.try-map` ou `list.try-fold`

Aucun conflit direct n’a été trouvé avec les règles déjà présentes dans la v1.

## Décisions retenues maintenant

### Helpers `Result`

Les helpers suivants sont acceptés pour cette phase :

```text
result.is-ok
result.is-err
result.unwrap-or
```

Signatures conceptuelles :

```text
result.is-ok
Result<T,E> -- Bool

result.is-err
Result<T,E> -- Bool

result.unwrap-or
Result<T,E> T -- T
```

Ces helpers sont purement ergonomiques.

Ils ne remplacent pas `case`, qui reste la forme normale d’inspection détaillée d’un `Result`.

### Inspection de `Result`

`case` reste le mécanisme officiel d’inspection structurée.

Exemple idiomatique :

```nicole
: timeout-or-default { cfg:Map<String,Int> -- n:Int }
  cfg "timeout" map.get case
    Ok(v) => v
    Err(MissingKey) => 30
  end
;
```

Cette phase n’introduit pas `result.match`.

### Opérateur de propagation `?`

L’opérateur `?` est retenu avec une portée strictement locale à la frame courante.

Comportement conceptuel :

```text
Ok(v)  ?  -> pousse v et continue
Err(e) ?  -> retourne immédiatement Err(e) depuis la frame courante
```

Règle fondamentale :

```text
? propage uniquement depuis la frame d’exécution courante.
```

Conséquences :

- dans un mot, `?` quitte ce mot
- dans une quotation, `?` quitte cette quotation
- `?` ne saute jamais directement hors du mot appelant, de l’`export` appelant, d’une quotation extérieure, ni d’un builtin de collection

### Contrainte de typage de `?`

La frame qui contient `?` doit déclarer une sortie compatible avec :

```text
Result<_,E>
```

Autrement dit, si `?` peut produire `Err(e)`, le contrat de retour de la frame doit déjà autoriser ce `Result`.

Un `?` ne peut donc pas apparaître dans une frame qui promet seulement une valeur simple comme `Int`.

## Interaction avec quotations et `call`

Les quotations suivent déjà la même discipline de frame que les mots normaux.

Cette phase étend cette règle à `?` de manière explicite :

- une quotation qui contient `?` doit elle-même déclarer une sortie compatible `Result<_,E>`
- `call` n’introduit aucun mécanisme spécial de propagation trans-frame
- si une quotation appelée par `call` exécute `Err(e) ?`, elle retourne `Err(e)` à son propre appelant, comme n’importe quelle autre sortie déclarée

Exemple valide :

```nicole
: run-check { x:Int -- r:Result<Int,MapError> }
  x :[ | n:Int -- r:Result<Int,MapError> |
    n maybe-fail ?
    1 +
  ;] call
;
```

Conceptuellement, la quotation produit ensuite :

```text
Ok(result)
```

Dans cet exemple :

- `?` agit à l’intérieur de la frame de la quotation
- si `maybe-fail` produit `Err(e)`, la quotation retourne immédiatement `Err(e)`
- `call` restitue alors ce `Result` au mot appelant

## Interaction avec `list.map`

`list.map` ne propage pas implicitement les erreurs.

Il consomme une quotation déjà construite et applique uniquement sa signature appelable.

Si la quotation renvoie `U`, alors `list.map` renvoie `List<U>`.

Si la quotation renvoie `Result<U,E>`, alors `list.map` renvoie :

```text
List<Result<U,E>>
```

et non :

```text
Result<List<U>,E>
```

Exemple invalide :

```nicole
: bad-map-propagation { xs:List<Int> -- ys:List<Int> }
  xs :[ | x:Int -- y:Int |
    x maybe-fail ?
    1 +
  ;] list.map
;
```

Cet exemple doit être rejeté :

- la quotation annonce `x:Int -- y:Int`
- pourtant `?` peut quitter la quotation avec `Err(e)`
- la signature de la quotation n’autorise donc pas ce comportement

Exemple valide :

```nicole
: map-with-results { xs:List<Int> -- ys:List<Result<Int,MapError>> }
  xs :[ | x:Int -- r:Result<Int,MapError> |
    x maybe-fail ?
    1 +
  ;] list.map
;
```

Conceptuellement, chaque application de la quotation produit ensuite :

```text
Ok(result)
```

Ici :

- la quotation est compatible avec l’usage de `?`
- `list.map` retourne une liste de `Result`
- aucun court-circuit implicite de collection n’a lieu

## Interaction future avec `list.fold` et `list.reduce`

Le même principe doit s’appliquer aux builtins d’ordre supérieur existants :

- `list.fold` n’acquiert pas de propagation implicite inter-frame
- `list.reduce` n’acquiert pas de propagation implicite inter-frame
- un `Result` retourné par leur quotation reste une valeur explicite, sauf spécification future d’un builtin distinct

Cette phase ne spécifie pas encore de variantes spécialisées à court-circuit.

## Décisions différées

Les éléments suivants restent hors de cette phase :

```text
result.unwrap
result.map
result.map-err
result.and-then
result.match
list.try-map
list.try-fold
```

Motifs de report :

- `result.unwrap` est partiel et introduit une ergonomie d’échec non retenue pour la v1 actuelle
- `result.map`, `result.map-err` et `result.and-then` dépendent d’une sémantique plus stabilisée des quotations comme combinators
- `result.match` ferait doublon avec `case` dans cette phase
- `list.try-map` et `list.try-fold` doivent rester explicites s’ils sont ajoutés plus tard

## Rationnel

Cette direction conserve :

- le raisonnement local par frame
- des signatures de pile explicites
- un style concaténatif et linéaire
- l’absence d’exceptions implicites trans-frame
- l’absence de court-circuit caché dans les builtins de collection

Elle évite qu’un `?` se comporte comme une fuite de contrôle invisible à travers `call`, `export`, `list.map`, `list.fold` ou `list.reduce`.

Le programmeur doit toujours pouvoir lire la signature immédiate de la frame courante et savoir si une sortie `Result` est possible.
