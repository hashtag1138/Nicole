# score_processor

But :

- montrer plusieurs modules dans un meme fichier ;
- montrer des imports utilisateur ;
- montrer `List<Int>` ;
- montrer `list.map`, `list.filter` et `list.fold` ;
- montrer un traitement qui retourne `Result<Int,MapError>` ;
- garder une surface `export` minimale.

Fichier principal :

- [score_processor.nicole](score_processor.nicole)

Validation depuis la racine du depot :

```sh
../nicole_python_implementation/.venv/bin/python examples/validate_examples.py examples/score_processor
```
