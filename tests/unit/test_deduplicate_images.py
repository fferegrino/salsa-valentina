from pathlib import Path
from unittest.mock import MagicMock

import pytest
from tools.deduplicate_images import attach_tqdm, find_to_keep, query_images


@pytest.mark.parametrize("quiet", [True, False])
def test_attach_tqdm(quiet):
    items = list(range(10))
    expected = list(attach_tqdm(items, quiet=quiet))

    assert items == expected


def test_query_images():
    signature_es = MagicMock()
    signature_es.search_image = MagicMock(
        side_effect=[
            [
                {"path": "/p3", "dist": 0.8},
                {"path": "/p2", "dist": 0.2},
                {"path": "/p4", "dist": 0.7},
            ],
            [
                {"path": "/p5", "dist": 0.0},
                {"path": "/p6", "dist": 0.1},
                {"path": "/p7", "dist": 0.1},
            ],
            [
                {"path": "/em4", "dist": 0.3},
                {"path": "/em5", "dist": 0.7},
                {"path": "/em1", "dist": 0.0},
                {"path": "/em2", "dist": 0.1},
                {"path": "/em3", "dist": 0.2},
            ],
        ]
    )
    paths = ["/p1", "/a1", "/em"]
    max_count = 2

    results = query_images(signature_es, paths, max_count)

    assert results == {
        "/p1": [("/p2", 0.2), ("/p4", 0.7)],
        "/a1": [("/p5", 0.0), ("/p6", 0.1)],
        "/em": [("/em1", 0.0), ("/em2", 0.1)],
    }
    assert signature_es.search_image.call_count == 3


@pytest.mark.parametrize(
    ["threshold", "expected"],
    [
        (0.0, ["k1", "k2", "k3", "k4"]),
        (0.1, ["k1", "k2", "k4"]),
        (1.0, ["k4"]),
        (0.4, ["k2", "k4"]),
    ],
)
def test_filter(threshold, expected):
    expected = [Path(path) for path in expected]
    kyes = {
        "k1": [("A", 0.1), ("B", 0.4), ("C", 0.4)],
        "k2": [("A", 0.8), ("B", 0.9), ("C", 1.0)],
        "k3": [("A", 0.05), ("B", 0.2), ("C", 0.3)],
        "k4": [],
    }

    actual = find_to_keep(kyes, threshold)

    assert expected == actual
