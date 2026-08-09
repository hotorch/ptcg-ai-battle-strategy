import io
import tarfile
from pathlib import Path

import pytest

from scripts.curate_context import notebook_score, topic_score
from scripts.evaluate import resolve_agent, summarize, wilson_interval
from scripts.gauntlet import rank
from scripts.kaggle_ops import parse_json_output, safe_ref
from scripts.package_submission import read_deck, validate_archive


def test_small_helpers(tmp_path):
    low, high = wilson_interval(50, 100)
    assert 0.40 < low < 0.41
    assert 0.59 < high < 0.60
    assert parse_json_output('Next Page Token = x\n[{"id": 1}]') == [{"id": 1}]
    assert safe_ref("owner/notebook") == "owner__notebook"
    assert topic_score({"title": "Engine bug", "votes": 1, "commentCount": 2}) > 20
    assert notebook_score({"title": "RL baseline", "totalVotes": 1}) > 20

    deck = tmp_path / "deck.csv"
    deck.write_text("\n".join(map(str, range(60))))
    assert len(read_deck(deck)) == 60

    shared = tmp_path / "shared.py"
    shared.write_text("def agent(obs): return []\n")
    candidate = tmp_path / "candidate"
    candidate.mkdir()
    (candidate / "deck.csv").write_text(deck.read_text())
    (candidate / "main.py").symlink_to(shared)
    assert Path(resolve_agent(str(candidate))).parent == candidate


def test_summarize_by_opponent_and_timing():
    records = [
        {
            "opponent": "random",
            "candidate_seat": 0,
            "error": False,
            "outcome": "win",
            "turns": 30,
            "candidate_moves": 12,
            "candidate_move_ms_max": 8.0,
            "candidate_move_ms_mean": 2.0,
        },
        {
            "opponent": "random",
            "candidate_seat": 1,
            "error": False,
            "outcome": "loss",
            "turns": 40,
            "candidate_moves": 15,
            "candidate_move_ms_max": 4.0,
            "candidate_move_ms_mean": 1.0,
        },
        {"opponent": "first", "candidate_seat": 0, "error": True, "outcome": "error"},
    ]
    total = summarize(records)
    assert total["games"] == 3
    assert total["errors"] == 1
    assert total["win_rate"] == 0.5
    assert total["candidate_move_ms_max"] == 8.0
    assert total["candidate_move_ms_mean"] == 1.5
    assert total["by_opponent"]["random"]["wins"] == 1
    assert total["by_opponent"]["random"]["games"] == 2
    assert total["by_opponent"]["first"]["errors"] == 1


def test_gauntlet_rank_symmetry():
    records = [
        {"pair": ("a", "b"), "outcome": "win"},
        {"pair": ("a", "b"), "outcome": "loss"},
        {"pair": ("a", "b"), "outcome": "win"},
        {"pair": ("b", "a"), "outcome": "error"},
    ]
    table = rank(records, ["a", "b"])
    assert table["a"]["wins"] == 2
    assert table["b"]["wins"] == 1
    assert table["a"]["games"] == table["b"]["games"] == 3
    assert table["a"]["errors"] == table["b"]["errors"] == 1
    assert table["a"]["pairs"]["b"]["win_rate"] == round(2 / 3, 4)


def test_archive_root_contract(tmp_path):
    path = tmp_path / "submission.tar.gz"
    with tarfile.open(path, "w:gz") as archive:
        for name in ("main.py", "deck.csv"):
            data = b"pass\n"
            info = tarfile.TarInfo(name)
            info.size = len(data)
            archive.addfile(info, io.BytesIO(data))
    validate_archive(path)

    bad = tmp_path / "bad.tar.gz"
    with tarfile.open(bad, "w:gz") as archive:
        info = tarfile.TarInfo("nested/main.py")
        info.size = 0
        archive.addfile(info, io.BytesIO())
    with pytest.raises(ValueError):
        validate_archive(bad)
