import io
import tarfile

import pytest

from scripts.curate_context import notebook_score, topic_score
from scripts.evaluate import wilson_interval
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
