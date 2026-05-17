# HOST_ABI.md

# Contrat hôte du langage Nicole

Ce document formalise le contrat conceptuel entre un programme Nicole et l’hôte qui l’embarque.

Il décrit les frontières d’intégration du langage :

- `export` : mot du programme appelable par l’hôte
- `host.*` : mot de l’hôte appelable par le programme

Ce document ne définit pas :

- une API C
- une ABI binaire
- une FFI Rust
- une FFI Lua
- des bindings LLVM
- une représentation mémoire concrète
- des structures runtime
- des conventions de pointeurs
- un format binaire de bytecode
- des détails de VM

Le niveau visé est celui d’une spécification de langage, pas celui d’une implémentation.

---

# 1. Principes généraux

Le contrat hôte sépare deux rôles :

1. le programme Nicole expose certains mots à l’hôte ;
2. l’hôte expose certains mots au programme Nicole.

Ces deux directions sont distinctes.

Un mot `export` appartient au programme Nicole mais peut être invoqué par l’hôte.

Un mot `host.*` appartient au contrat fourni par l’hôte et peut être invoqué par le programme Nicole.

Le contrat hôte ne crée pas de mutation implicite, ne partage pas de pile globale et ne contourne pas les règles de typage ou de retour définies ailleurs dans la documentation.

---

# 2. `export` : mots du programme appelables par l’hôte

`export` désigne un mot défini par le programme Nicole et rendu visible à l’hôte.

## Garanties d’un mot exporté

Un mot exporté garantit :

- un nom d’export unique dans le programme
- une signature connue
- des entrées typées
- des sorties typées
- une discipline de retour identique à celle de tout mot Nicole
- l’exécution dans une stack frame isolée

Le mot exporté reste un mot du programme.

Il peut aussi être appelé depuis d’autres mots du programme, comme tout mot visible.

## Appel conceptuel par l’hôte

L’hôte appelle un mot exporté en sélectionnant ce mot par son nom d’export et en lui fournissant les valeurs d’entrée attendues par sa signature.

Le nom d’export est le point de liaison public entre le programme et l’hôte.

Au niveau de l’interface hôte, un nom d’export désigne un seul point d’entrée.

Deux mots exportés ne peuvent jamais partager le même nom d’export.

La surcharge par types d’entrée ne s’applique pas aux mots `export`.

Toute collision de noms d’export est invalide et doit être rejetée comme une erreur de contrat détectable statiquement.

Le programme exécute alors le mot dans sa frame propre et renvoie exactement les sorties déclarées.

L’hôte ne reçoit que ces sorties déclarées, dans l’ordre défini par la signature.

L’hôte ne voit pas la pile locale interne du mot.

## Contrat de retour

Pour un mot exporté, la conformité du retour relève de la sémantique du langage.

Un mot Nicole défini dans le programme ne peut pas avoir un retour “opaque” pour l’hôte.

Sa signature doit être respectée exactement.

Exemple conceptuel :

```sorte
export : app.on-message { msg:String -- }
  msg host.log
;
```

Dans cet exemple, l’hôte peut invoquer `app.on-message` avec une valeur de type `String`.
Le mot ne renvoie aucune valeur.

---

# 3. `host.*` : mots de l’hôte appelables par le programme

`host.*` désigne des mots fournis par l’hôte et appelables depuis le programme Nicole.

## Garanties d’un mot `host.*`

Un mot `host.*` garantit :

- une signature connue ou déclarée par le contrat d’intégration
- des entrées typées
- des sorties typées si le mot en déclare
- une sémantique stable du point de vue du programme Nicole

Le programme peut appeler un mot `host.*` comme il appelle un mot normal, mais le mot n’est pas défini dans le code Nicole.

## Appel conceptuel depuis le programme

Le programme appelle le mot `host.*` selon la discipline de pile définie dans `SEMANTIQUE.md`.

Le mot hôte s’exécute selon son contrat et renvoie ses sorties déclarées sur la pile du programme.

Le programme ne doit pas supposer :

- une représentation mémoire précise
- une stratégie d’allocation
- une identité de pointeur
- une structure de fermeture
- un format de sérialisation particulier

Exemple conceptuel :

```sorte
: save-log { msg:String -- }
  msg host.log
;
```

Ici, le programme appelle un mot fourni par l’hôte et lui transmet une chaîne.

---

# 4. Obligations de typage

Le contrat hôte repose sur le typage statique déjà défini dans le langage.

## Pour `export`

Un mot exporté doit avoir une signature explicite.

L’hôte ne peut appeler ce mot qu’en respectant :

- le nombre d’entrées
- l’ordre des entrées
- les types des entrées
- le nombre de sorties attendues
- l’ordre des sorties attendues
- les types des sorties attendues

## Pour `host.*`

Un mot `host.*` doit aussi être vu comme une entité typée.

Le programme n’a pas à connaître l’implémentation du mot hôte, mais il doit connaître son contrat de type.

Le contrat d’intégration doit donc fournir :

- le nom du mot
- sa signature
- le statut de disponibilité du mot

Le statut de disponibilité est conceptuellement l’un des deux suivants :

- requis
- optionnel

Un mot `host.*` requis doit être présent pour que le contrat soit valide.

Son absence constitue une erreur d’intégration.

Un mot `host.*` optionnel peut être absent sans invalider le contrat en lui-même.

Le programme ne peut pas supposer la disponibilité d’un mot optionnel sans règle explicite du contrat d’intégration.

Si ces informations sont insuffisantes ou ambiguës, le contrat n’est pas valable pour la v1.

---

# 5. Obligations de contrat

Le contrat hôte impose que les appels respectent les signatures annoncées.

## Pour les mots exportés

L’hôte doit :

- fournir les entrées attendues
- accepter exactement les sorties annoncées
- traiter les erreurs de contrat si le mot ne peut pas être invoqué correctement

Le programme ne peut pas exiger de l’hôte qu’il accepte des entrées d’un autre type ou qu’il ignore des sorties non déclarées.

## Pour les mots `host.*`

Le programme doit :

- appeler le mot avec les types attendus
- ne pas inventer d’arguments
- ne pas attendre de sortie non déclarée

L’hôte doit :

- fournir le mot annoncé
- respecter sa signature
- signaler toute absence ou tout échec de liaison comme une erreur d’intégration

Le contrat hôte n’autorise pas de conversions implicites au niveau de la frontière.

---

# 6. Erreurs d’intégration

Une erreur d’intégration est un échec de liaison entre le programme Nicole et l’hôte.

Ce n’est ni une erreur normale représentée par `Result`, ni une erreur de simple logique métier du programme.

## Cas typiques

- un mot `host.*` est absent alors que le contrat hôte le déclare
- un mot exporté est demandé par l’hôte mais n’est pas exposé
- une signature déclarée par le contrat hôte ne correspond pas à la signature attendue
- l’hôte ne peut pas satisfaire une liaison requise par le programme ou par l’export

## Erreur statique ou erreur d’exécution

Si le contrat hôte est connu statiquement et qu’un mot manque, l’erreur doit pouvoir être détectée avant exécution.

Si l’environnement hôte est dynamique et que la liaison disparaît ou n’existe pas au moment de l’appel, l’erreur peut apparaître à l’exécution.

Dans les deux cas, il s’agit d’une erreur d’intégration.

Lorsqu’elle apparaît à l’exécution, une erreur d’intégration constitue aussi une erreur de contrat d’exécution.

## Différence avec `Result`

Une erreur d’intégration n’est pas un `Result`, sauf si le mot hôte lui-même a explicitement été défini pour renvoyer un `Result`.

Dans ce cas, le `Result` fait partie du contrat du mot, pas du mécanisme de liaison lui-même.

---

# 7. Différences de niveau d’erreur

Le dépôt distingue trois catégories.

## Erreur normale

Une erreur normale est un cas attendu du domaine, représenté explicitement par `Result`.

Exemples conceptuels :

- clé absente dans une map
- calcul impossible que l’API choisit d’exprimer explicitement

## Erreur de contrat d’exécution

Une erreur de contrat d’exécution est une violation d’un contrat supposé valide, observée au moment de l’exécution.

Elle couvre des cas comme :

- `host.*` absent dans un environnement dynamique
- primitive fournie par intégration mais non satisfaisable au moment de l’appel
- `list.reduce` sur une liste vide non prouvable statiquement

Ce type d’erreur n’est pas un `Result`.

## Erreur d’intégration

Une erreur d’intégration est la catégorie spécifique d’erreur liée à la frontière entre le programme Nicole et l’hôte.

Elle peut être détectée avant exécution si le contrat hôte est connu statiquement, ou à l’exécution dans un environnement dynamique.

Lorsqu’elle apparaît à l’exécution, elle constitue aussi une erreur de contrat d’exécution.

---

# 8. Non-objectifs et limites de la v1

`HOST_ABI.md` ne définit pas :

- un mécanisme concret de découverte dynamique
- un registre d’exports concret
- un protocole de sérialisation
- un modèle async/thread
- une FFI native
- une API ou interface native C, Rust, Lua ou LLVM
- une représentation mémoire des valeurs
- une stratégie d’allocation
- une convention de pointeurs
- un format binaire ou ABI binaire
- des détails de VM ou de runtime

La seule chose normée ici est le contrat conceptuel entre un programme Nicole et un hôte embarquant.

---

# 9. Règle de fond

Le contrat hôte doit rester :

- explicite
- typé
- conceptuel
- stable
- indépendant des détails d’implémentation

Il doit permettre de documenter l’intégration sans transformer le dépôt en spécification de VM ou de FFI.
