#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _bootstrap_import() -> None:
    try:
        import nicole  # noqa: F401
        return
    except ModuleNotFoundError:
        candidate = _repo_root().parent / "nicole_python_implementation" / "src"
        if candidate.exists():
            sys.path.insert(0, str(candidate))
        try:
            import nicole  # noqa: F401
        except ModuleNotFoundError as exc:
            raise SystemExit(
                "Impossible d'importer le package nicole. "
                "Utilisez de preference : "
                "../nicole_python_implementation/.venv/bin/python "
                "examples/validate_examples.py"
            ) from exc


_bootstrap_import()

from nicole.pipeline import analyze_program


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Valide statiquement les exemples Nicole avec NicolePy."
    )
    parser.add_argument(
        "paths",
        nargs="*",
        help="Fichiers ou dossiers a valider. Par defaut : tout examples/.",
    )
    return parser.parse_args()


def _collect_files(paths: list[str]) -> list[Path]:
    base = _repo_root()
    examples_root = base / "examples"
    targets = [examples_root] if not paths else [base / item for item in paths]
    files: list[Path] = []
    for target in targets:
        if not target.exists():
            raise FileNotFoundError(f"chemin introuvable: {target}")
        if target.is_file():
            if target.suffix == ".nicole":
                files.append(target)
            continue
        files.extend(sorted(target.rglob("*.nicole")))
    deduped = sorted({path.resolve() for path in files})
    return deduped


def main() -> int:
    args = _parse_args()
    base = _repo_root()
    files = _collect_files(args.paths)
    if not files:
        print("Aucun fichier .nicole trouve.")
        return 1

    failures = 0
    for path in files:
        display = path.relative_to(base)
        try:
            source = path.read_text(encoding="utf-8")
            analyze_program(source)
        except Exception as exc:  # pragma: no cover - direct CLI reporting
            failures += 1
            print(f"FAIL {display}")
            print(f"  {exc}")
        else:
            print(f"OK   {display}")

    print(f"\nResume: {len(files) - failures} valide(s), {failures} echec(s).")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
