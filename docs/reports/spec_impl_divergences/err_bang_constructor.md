# Divergence spec / NicolePy : constructeur postfixe `Err!`

## Resume court

La specification Nicole v1 documente `Err!` comme constructeur postfixe valide de `Result`.

NicolePy accepte cette forme au parsing, mais `analyze_program(...)` echoue ensuite sur un programme minimal utilisant `MissingKey Err!`.

La divergence doit etre traitee cote NicolePy. La spec ne doit pas etre modifiee pour suivre cette limitation d'implementation.

## Comportement attendu selon la spec

La specification normative decrit explicitement `Err!` comme constructeur postfixe utilisable hors `case`.

Points confirmes :

- [SYNTAXE.md](/data/data/com.termux/files/home/Sources/nicole/nicole_language_docs_seed/SYNTAXE.md:1896) : hors `case`, la construction d'une valeur `Result` utilise les mots postfixes `Ok!` et `Err!`
- [SYNTAXE.md](/data/data/com.termux/files/home/Sources/nicole/nicole_language_docs_seed/SYNTAXE.md:1903) : `Err! { error:E -- r:Result<T,E> }`
- [SYNTAXE.md](/data/data/com.termux/files/home/Sources/nicole/nicole_language_docs_seed/SYNTAXE.md:1909) : `Err!` consomme la valeur d'erreur et produit `Err(error)`
- [SEMANTIQUE.md](/data/data/com.termux/files/home/Sources/nicole/nicole_language_docs_seed/SEMANTIQUE.md:845) : hors `case`, la construction d'une valeur `Result` utilise `Ok!` et `Err!`
- [SEMANTIQUE.md](/data/data/com.termux/files/home/Sources/nicole/nicole_language_docs_seed/SEMANTIQUE.md:851) : `Err!` a l'effet de pile `E -- Result<T,E>`

Conclusion attendue :

```nicole
MissingKey Err!
```

doit etre accepte dans une frame qui attend une sortie de type `Result<_,MapError>`.

## Comportement observe dans NicolePy

NicolePy accepte la forme au niveau du parser, mais echoue ensuite pendant `analyze_program(...)`.

Observation confirmee :

- [test_parser.py](/data/data/com.termux/files/home/Sources/nicole/nicole_python_implementation/tests/test_parser.py:1466) contient un test qui accepte `MissingKey Err!`
- la reproduction locale avec `analyze_program(...)` echoue avec `ResolutionError: unresolved name at 3:5`

## Programme minimal de reproduction

```nicole
module @app
  : err-result { -- r:Result<Int,MapError> }
    MissingKey Err!
  ;
end-module
```

## Commande de reproduction

```sh
../nicole_python_implementation/.venv/bin/python - <<'PY'
from nicole.pipeline import analyze_program

source = '''module @app
  : err-result { -- r:Result<Int,MapError> }
    MissingKey Err!
  ;
end-module
'''

analyze_program(source)
PY
```

## Erreur obtenue

```text
ResolutionError: unresolved name at 3:5
```

## Analyse probable

Le parser semble deja reconnaitre correctement la construction postfixe `Err!`.

L'echec se produit donc plus tard dans le pipeline, probablement a la resolution des noms ou dans une phase proche de la resolution semantique.

Hypothese la plus probable :

- `MissingKey` est encore traite comme un identifiant ordinaire a resoudre ;
- dans le contexte `MissingKey Err!`, NicolePy ne reconnait pas correctement `MissingKey` comme valeur normative de type `MapError` ;
- le support du parser pour `ResultErrNode` n'est pas encore aligne avec la resolution / verification complete du programme.

Cette hypothese est coherente avec les observations suivantes :

- le parser accepte `MissingKey Err!`
- le parser rejette bien `Err(MissingKey)` comme forme de construction invalide en v1
- l'erreur reproduite est une `ResolutionError`, pas une `ParseError`

## Impact

Impact immediat :

- les exemples ajoutes sous [examples/](/data/data/com.termux/files/home/Sources/nicole/nicole_language_docs_seed/examples/README.md:1) n'utilisent pas cette forme, donc ils restent validables avec NicolePy
- la documentation peut rester pedagogiquement correcte si elle ne pretend pas que NicolePy valide deja toutes les formes normatives documentees

Impact de fond :

- la spec et NicolePy ne sont pas encore totalement alignes sur une forme normative documentee de `Result`
- NicolePy ne peut pas encore servir de validation complete de toutes les formes normatives autour de `Err!`
- tant que cette divergence n'est pas traitee ou explicitement acceptee, le blocage du commit/push documentaire reste justifie

## Decision recommandee

1. Corriger NicolePy pour accepter les variantes d'erreur normatives avec `Err!`.
2. Ajouter au minimum un test checker ou pipeline couvrant explicitement :

```nicole
module @app
  : err-result { -- r:Result<Int,MapError> }
    MissingKey Err!
  ;
end-module
```

3. Relancer ensuite :

```sh
../nicole_python_implementation/.venv/bin/python examples/validate_examples.py
```

4. Refaire une verification finale de coherence spec / docs / exemples / NicolePy.
5. Seulement apres cette etape, reconsiderer le commit puis le push de la documentation et des exemples.
