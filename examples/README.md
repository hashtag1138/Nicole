# Exemples Nicole valides

Ce dossier contient des exemples Nicole concus pour etre analyses avec NicolePy.

Chaque sous-dossier contient :

- un exemple `.nicole` auto-suffisant ;
- un `README.md` court ;
- une commande de validation ciblee.

Les exemples ici sont faits pour etre verifies par l'outil, pas seulement lus dans la documentation.

## Contenu

- [config_loader](config_loader/README.md)
- [score_processor](score_processor/README.md)
- [host_logging](host_logging/README.md)
- [collections](collections/README.md)
- [quotations](quotations/README.md)

## Validation

Depuis la racine de ce depot :

```sh
../nicole_python_implementation/.venv/bin/python examples/validate_examples.py
```

Validation d'un sous-dossier precis :

```sh
../nicole_python_implementation/.venv/bin/python examples/validate_examples.py examples/config_loader
```

Le script :

- parcourt tous les fichiers `.nicole` demandes ;
- appelle `nicole.pipeline.analyze_program(...)` ;
- affiche chaque fichier valide ;
- echoue avec un code non nul si un exemple ne passe pas.
