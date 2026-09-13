"""Run with: uv run python tests/test_report_figures.py"""
import sys
from math import isclose
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from report_figures import _meta_tv


def test_meta_tv_includes_other():
    # Matching the six reference categories and the 47.1% residual gives zero.
    reference_counts = {
        'Dragapult': 427, 'Alakazam': 49, 'Meganium/TapuBulu': 23,
        'MegaLucario': 30, 'Other': 471,
    }
    assert isclose(_meta_tv(reference_counts, 1000), 0, abs_tol=1e-12)
    # Omitting Other would halve the distance in this disjoint-mass example.
    assert isclose(_meta_tv({'Other': 1000}, 1000), 0.529)
    assert isclose(_meta_tv({'Dragapult': 1000}, 1000), 0.573)


if __name__ == '__main__':
    test_meta_tv_includes_other()
    print('TV checks passed')
