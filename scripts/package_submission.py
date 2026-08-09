"""Validate and build a PTCG submission archive."""

from __future__ import annotations

import argparse
import importlib
import os
import py_compile
import re
import shutil
import sys
import tarfile
import tempfile
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGES = ROOT / "submissions" / "packages"
MAX_BYTES = int(197.7 * 1024 * 1024)
SDK_FILES = {"__init__.py", "api.py", "game.py", "libcg.so", "sim.py", "utils.py"}


def read_deck(path: Path) -> list[int]:
    try:
        deck = [int(line.strip()) for line in path.read_text().splitlines() if line.strip()]
    except ValueError as exc:
        raise ValueError(f"deck.csv contains a non-integer: {path}") from exc
    if len(deck) != 60:
        raise ValueError(f"deck.csv must contain 60 card IDs, got {len(deck)}")
    return deck


def needs_cg(main_path: Path) -> bool:
    # 동봉 모듈(fork_policy.py 등)이 cg를 임포트하는 경우도 잡도록 소스 전체를 본다.
    pattern = r"(?m)^\s*(?:from\s+cg\b|import\s+cg\b)"
    return any(
        re.search(pattern, path.read_text())
        for path in main_path.parent.glob("*.py")
        if "__pycache__" not in path.parts
    )


def installed_cg() -> Path:
    downloaded = ROOT / "data" / "raw" / "sample_submission" / "cg"
    if SDK_FILES <= {path.name for path in downloaded.glob("*") if path.is_file()}:
        return downloaded
    module = importlib.import_module("kaggle_environments.envs.cabt.cg")
    bundled = Path(module.__file__).resolve().parent
    if SDK_FILES <= {path.name for path in bundled.iterdir() if path.is_file()}:
        return bundled
    raise ValueError(
        "submission SDK not found; run `uv run python scripts/kaggle_ops.py fetch-sdk`"
    )


def copy_sdk(source: Path, destination: Path) -> None:
    destination.mkdir()
    missing = SDK_FILES - {path.name for path in source.iterdir() if path.is_file()}
    if missing:
        raise ValueError(f"CABT SDK is missing: {', '.join(sorted(missing))}")
    for name in sorted(SDK_FILES):
        shutil.copy2(source / name, destination / name)


def validate_self_play(main_path: Path) -> None:
    from kaggle_environments import make

    previous = Path.cwd()
    temporary_library = main_path.parent / "cg" / "libcg.dylib"
    try:
        if sys.platform == "darwin" and temporary_library.parent.is_dir():
            bundled = (
                Path(importlib.import_module("kaggle_environments.envs.cabt.cg").__file__)
                .resolve()
                .parent
            )
            shutil.copy2(bundled / "libcg.dylib", temporary_library)
        os.chdir(main_path.parent)
        env = make("cabt", debug=True)
        env.run([str(main_path), str(main_path)])
    finally:
        os.chdir(previous)
        if temporary_library.is_file():
            temporary_library.unlink()
    final = env.steps[-1]
    statuses = [state.status for state in final]
    rewards = [state.reward for state in final]
    if statuses != ["DONE", "DONE"] or any(reward is None for reward in rewards):
        raise ValueError(f"self-play failed: statuses={statuses}, rewards={rewards}")


def validate_archive(path: Path) -> None:
    if not path.is_file():
        raise ValueError(f"archive not found: {path}")
    if path.stat().st_size > MAX_BYTES:
        raise ValueError("archive exceeds the 197.7 MiB submission limit")
    with tarfile.open(path, "r:gz") as archive:
        names = set(archive.getnames())
    missing = {"main.py", "deck.csv"} - names
    if missing:
        raise ValueError(f"archive root is missing: {', '.join(sorted(missing))}")
    if any(name.startswith("./") or "__pycache__" in name for name in names):
        raise ValueError("archive contains a bad root path or Python cache")


def build(source: Path, output: Path | None = None) -> Path:
    source = source.resolve()
    main_path = source / "main.py"
    deck_path = source / "deck.csv"
    if not main_path.is_file() or not deck_path.is_file():
        raise ValueError(f"source must contain main.py and deck.csv: {source}")
    read_deck(deck_path)
    py_compile.compile(str(main_path), doraise=True)

    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    output = output or PACKAGES / f"{stamp}__submission.tar.gz"
    output = output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as temporary:
        stage = Path(temporary)
        shutil.copy2(main_path, stage / "main.py")
        shutil.copy2(deck_path, stage / "deck.csv")
        for extra in source.glob("*.json"):  # 후보 옆 보조 데이터(예: 증류 policy_table.json)
            shutil.copy2(extra, stage / extra.name)
        for extra in source.glob("*.py"):  # 동봉 모듈(예: fork_policy.py) — main.py 제외
            if extra.name != "main.py":
                shutil.copy2(extra, stage / extra.name)
        if needs_cg(main_path):
            copy_sdk(installed_cg(), stage / "cg")
        validate_self_play(stage / "main.py")
        with tarfile.open(output, "w:gz") as archive:
            for item in sorted(stage.rglob("*")):
                if item.is_file() and "__pycache__" not in item.parts and item.suffix != ".pyc":
                    archive.add(item, arcname=str(item.relative_to(stage)))

    validate_archive(output)
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        output = build(args.source, args.output)
    except (OSError, ValueError, py_compile.PyCompileError) as exc:
        parser.exit(2, f"ERROR: {exc}\n")
    print(f"submission ready: {output.relative_to(ROOT)} ({output.stat().st_size:,} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
