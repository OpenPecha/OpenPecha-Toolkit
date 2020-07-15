from collections import defaultdict
from pathlib import Path

import pytest

from openpecha.formatters import HFMLFormatter
from openpecha.formatters.layers import *


@pytest.fixture()
def formatter():
    """Return HFMLFormatter object."""
    from openpecha.formatters.layers import HFML_ANN_PATTERN

    config = {"ann_patterns": HFML_ANN_PATTERN}
    return HFMLFormatter(config=config)


@pytest.fixture()
def one_vol_test_data():
    m_text = Path("tests/data/formatter/hfml/v001.txt").read_text()
    base_id = "v001"
    expected = defaultdict(lambda: defaultdict(list))
    expected[AnnType.pecha_title][base_id].append((":", OnlySpan(Span(0, 3))))
    return m_text, base_id, expected


def test_parse_ann_one_vol(formatter, one_vol_test_data):
    m_text, base_id, expected = one_vol_test_data

    formatter.parse_ann(m_text, base_id)

    assert formatter.layers == expected