"""Read Kaggle context safely and gate the only state-changing command: submit."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.package_submission import validate_archive

COMPETITION = "pokemon-tcg-ai-battle"
CONTEXT = ROOT / "context" / "kaggle"
SUBMISSIONS = ROOT / "submissions"
CONFIRMATION = "SUBMIT_PTCG_AI_BATTLE"
REMOTE_SDK = "sample_submission/sample_submission/cg"
SDK_FILES = ("__init__.py", "api.py", "game.py", "libcg.so", "sim.py", "utils.py")
LOCAL_SDK_FILES = (*SDK_FILES, "libcg.dylib")


class KaggleCommandError(RuntimeError):
    pass


def utc_stamp() -> str:
    return datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")


def kaggle_executable() -> str:
    executable = shutil.which("kaggle") or str(Path(sys.executable).with_name("kaggle"))
    if Path(executable).exists() or shutil.which(executable):
        return executable
    raise KaggleCommandError("Kaggle CLI를 찾지 못했습니다. `uv sync`를 실행하세요.")


def run_kaggle(arguments: Sequence[str]) -> str:
    completed = subprocess.run(
        [kaggle_executable(), *arguments], cwd=ROOT, capture_output=True, text=True, check=False
    )
    if completed.returncode:
        detail = (completed.stderr or completed.stdout).strip()
        raise KaggleCommandError(detail or f"Kaggle CLI exited with {completed.returncode}")
    return completed.stdout.strip()


def parse_json_output(output: str) -> object:
    decoder = json.JSONDecoder()
    for match in re.finditer(r"(?m)^[\[{]", output.strip()):
        try:
            value, _ = decoder.raw_decode(output.strip()[match.start() :])
            return value
        except json.JSONDecodeError:
            pass
    raise ValueError("Kaggle CLI output did not contain JSON")


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def safe_ref(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "__", value).strip("._-")
    if not cleaned:
        raise ValueError("safe filename could not be made")
    return cleaned


def command_auth_check(_: argparse.Namespace) -> int:
    print(run_kaggle(["competitions", "list", "-s", COMPETITION]))
    print(run_kaggle(["competitions", "submission-limits", COMPETITION]))
    return 0


def command_status(_: argparse.Namespace) -> int:
    commands = [
        ("limits", ["competitions", "submission-limits", COMPETITION]),
        ("submissions", ["competitions", "submissions", COMPETITION]),
        ("leaderboard", ["competitions", "leaderboard", COMPETITION, "-s"]),
    ]
    for label, command in commands:
        print(f"## {label}\n{run_kaggle(command)}\n")
    return 0


def command_sync_context(args: argparse.Namespace) -> int:
    destination = CONTEXT / "snapshots" / utc_stamp()
    operations = {
        "competition-pages": [
            "competitions",
            "pages",
            COMPETITION,
            "list",
            COMPETITION,
            "--content",
            "--format",
            "json",
        ],
        "recent-topics": [
            "competitions",
            "topics",
            "list",
            COMPETITION,
            "--sort-by",
            "recent",
            "--format",
            "json",
        ],
        "top-notebooks": [
            "kernels",
            "list",
            "--competition",
            COMPETITION,
            "--page-size",
            str(args.notebooks),
            "--sort-by",
            "voteCount",
            "--format",
            "json",
        ],
    }
    manifest = {
        "competition": COMPETITION,
        "created_at_utc": datetime.now(UTC).isoformat(),
        "sources": {},
    }
    failures = 0
    for name, command in operations.items():
        try:
            value = parse_json_output(run_kaggle(command))
            write_json(destination / f"{name}.json", value)
            manifest["sources"][name] = {"status": "ok", "command": ["kaggle", *command]}
        except (KaggleCommandError, ValueError) as exc:
            failures += 1
            manifest["sources"][name] = {"status": "error", "error": str(exc)}
    write_json(destination / "manifest.json", manifest)
    print(
        f"snapshot: {destination.relative_to(ROOT)} ({len(operations) - failures} ok, {failures} failed)"
    )
    return bool(failures)


def command_show_topic(args: argparse.Namespace) -> int:
    ref = args.topic_ref if "/" in args.topic_ref else f"{COMPETITION}/{args.topic_ref}"
    value = parse_json_output(
        run_kaggle(["competitions", "topics", "show", ref, "--format", "json"])
    )
    output = CONTEXT / "topics" / f"{safe_ref(ref)}--{utc_stamp()}.json"
    write_json(output, value)
    print(output.relative_to(ROOT))
    return 0


def command_pull_notebook(args: argparse.Namespace) -> int:
    output = CONTEXT / "notebooks" / safe_ref(args.kernel_ref) / utc_stamp()
    output.mkdir(parents=True, exist_ok=True)
    print(run_kaggle(["kernels", "pull", args.kernel_ref, "--path", str(output), "--metadata"]))
    write_json(
        output / "source.json",
        {
            "ref": args.kernel_ref,
            "url": f"https://www.kaggle.com/code/{args.kernel_ref}",
            "downloaded_at_utc": datetime.now(UTC).isoformat(),
        },
    )
    return 0


def command_fetch_sdk(_: argparse.Namespace) -> int:
    destination = ROOT / "data" / "raw" / "sample_submission" / "cg"
    destination.mkdir(parents=True, exist_ok=True)
    for name in LOCAL_SDK_FILES:
        print(
            run_kaggle(
                [
                    "competitions",
                    "download",
                    COMPETITION,
                    "--file",
                    f"{REMOTE_SDK}/{name}",
                    "--path",
                    str(destination),
                    "--force",
                    "--quiet",
                ]
            )
        )
    missing = [name for name in LOCAL_SDK_FILES if not (destination / name).is_file()]
    if missing:
        raise ValueError(f"downloaded SDK is missing: {', '.join(missing)}")
    print(f"SDK ready: {destination.relative_to(ROOT)}")
    return 0


def command_track_ratings(_: argparse.Namespace) -> int:
    values = parse_json_output(
        run_kaggle(["competitions", "submissions", COMPETITION, "--format", "json"])
    )
    if not isinstance(values, list):
        raise TypeError("submission JSON is not a list")
    history = SUBMISSIONS / "rating_history.tsv"
    if not history.exists():
        history.write_text("checked_at_utc\tsubmission_id\tstatus\tpublic_score\tdescription\n")
    stamp = utc_stamp()
    with history.open("a", encoding="utf-8") as output:
        for item in values:
            description = " ".join(str(item.get("description", "")).split()).replace("\t", " ")
            row = [
                stamp,
                item.get("ref", "?"),
                str(item.get("status", "?")).split(".")[-1],
                item.get("publicScore", ""),
                description[:100],
            ]
            output.write("\t".join(map(str, row)) + "\n")
            print("\t".join(map(str, row)))
    return 0


def command_submit(args: argparse.Namespace) -> int:
    if args.confirm != CONFIRMATION:
        raise ValueError(f"submission requires --confirm {CONFIRMATION}")
    path = Path(args.file)
    if not path.is_absolute():
        path = ROOT / path
    path = path.resolve()
    try:
        path.relative_to(ROOT.resolve())
    except ValueError as exc:
        raise ValueError("submission archive must be inside this workspace") from exc
    validate_archive(path)
    print(run_kaggle(["competitions", "submission-limits", COMPETITION]))
    result = run_kaggle(
        ["competitions", "submit", COMPETITION, "--file", str(path), "--message", args.message]
    )
    history = SUBMISSIONS / "history.tsv"
    if not history.exists():
        history.write_text("submitted_at_utc\tfile\tmessage\tcli_result\n")
    compact = " ".join(result.split()).replace("\t", " ")
    message = " ".join(args.message.split()).replace("\t", " ")
    with history.open("a", encoding="utf-8") as output:
        output.write(f"{utc_stamp()}\t{path.relative_to(ROOT)}\t{message}\t{compact}\n")
    print(result)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name, handler in (
        ("auth-check", command_auth_check),
        ("status", command_status),
        ("track-ratings", command_track_ratings),
        ("fetch-sdk", command_fetch_sdk),
    ):
        command = commands.add_parser(name)
        command.set_defaults(handler=handler)
    sync = commands.add_parser("sync-context")
    sync.add_argument("--notebooks", type=int, default=100)
    sync.set_defaults(handler=command_sync_context)
    topic = commands.add_parser("show-topic")
    topic.add_argument("topic_ref")
    topic.set_defaults(handler=command_show_topic)
    notebook = commands.add_parser("pull-notebook")
    notebook.add_argument("kernel_ref")
    notebook.set_defaults(handler=command_pull_notebook)
    submit = commands.add_parser("submit")
    submit.add_argument("--file", required=True)
    submit.add_argument("--message", required=True)
    submit.add_argument("--confirm", required=True)
    submit.set_defaults(handler=command_submit)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if hasattr(args, "notebooks") and not 1 <= args.notebooks <= 100:
        parser.error("--notebooks must be between 1 and 100")
    try:
        return int(args.handler(args))
    except (KaggleCommandError, OSError, TypeError, ValueError) as exc:
        parser.exit(2, f"ERROR: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
