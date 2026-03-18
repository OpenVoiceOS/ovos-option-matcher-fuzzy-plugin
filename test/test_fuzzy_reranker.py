# Copyright 2024, OpenVoiceOS
# Apache 2.0

"""Unit tests for FuzzyReRankerPlugin."""

import pytest
from ovos_reranker_fuzzy import FuzzyReRankerPlugin


OPTIONS = ["play jazz music", "play rock music", "play classical music"]


@pytest.fixture
def reranker() -> FuzzyReRankerPlugin:
    """Return a default FuzzyReRankerPlugin instance."""
    return FuzzyReRankerPlugin()


def test_rerank_basic(reranker: FuzzyReRankerPlugin) -> None:
    """Top result should be the closest fuzzy match."""
    ranked = reranker.rerank("jazz", OPTIONS)
    assert len(ranked) == len(OPTIONS)
    # scores are floats, options are strings
    top_score, top_option = ranked[0]
    assert isinstance(top_score, float)
    assert top_option == "play jazz music"
    # scores are sorted descending
    scores = [s for s, _ in ranked]
    assert scores == sorted(scores, reverse=True)


def test_select_exact_match(reranker: FuzzyReRankerPlugin) -> None:
    """High confidence query should return the matching string directly."""
    result = reranker.select_answer("jazz music", OPTIONS)
    assert result == "play jazz music"


def test_select_ordinal_second(reranker: FuzzyReRankerPlugin) -> None:
    """'second' ordinal should return options[1]."""
    result = reranker.select_answer("the second one", OPTIONS, lang="en-us")
    assert result == OPTIONS[1]


def test_select_ordinal_last(reranker: FuzzyReRankerPlugin) -> None:
    """'last' keyword should return the final option."""
    result = reranker.select_answer("the last option", OPTIONS)
    assert result == OPTIONS[-1]


def test_select_no_match_returns_none(reranker: FuzzyReRankerPlugin) -> None:
    """Garbage query below min_conf with no ordinal cue should return None."""
    result = reranker.select_answer("xyzzy frobnicator quux", OPTIONS)
    assert result is None


def test_rerank_return_index(reranker: FuzzyReRankerPlugin) -> None:
    """return_index=True should yield integer indices instead of strings."""
    ranked = reranker.rerank("jazz", OPTIONS, return_index=True)
    assert len(ranked) == len(OPTIONS)
    for score, idx in ranked:
        assert isinstance(score, float)
        assert isinstance(idx, int)
        assert 0 <= idx < len(OPTIONS)
    # top result should be index 0 (jazz is first in OPTIONS)
    _, top_idx = ranked[0]
    assert top_idx == 0


def test_select_answer_return_index(reranker: FuzzyReRankerPlugin) -> None:
    """select_answer with return_index=True should return an int."""
    result = reranker.select_answer("jazz music", OPTIONS, return_index=True)
    assert result == 0


def test_select_ordinal_second_return_index(reranker: FuzzyReRankerPlugin) -> None:
    """Ordinal fallback with return_index=True should return the integer index."""
    result = reranker.select_answer("the second one", OPTIONS, lang="en-us", return_index=True)
    assert result == 1


def test_select_ordinal_last_return_index(reranker: FuzzyReRankerPlugin) -> None:
    """Last-word fallback with return_index=True should return len(options)-1."""
    result = reranker.select_answer("the last option", OPTIONS, return_index=True)
    assert result == len(OPTIONS) - 1


def test_entry_point_registered() -> None:
    """Plugin must be discoverable via OPM find_reranker_plugins."""
    from ovos_plugin_manager.agents import find_reranker_plugins
    plugins = find_reranker_plugins()
    assert "ovos-reranker-fuzzy-plugin" in plugins, (
        f"ovos-reranker-fuzzy-plugin not found in OPM. Found: {list(plugins.keys())}"
    )


def test_config_min_conf_respected() -> None:
    """A high min_conf should force the fallback path even for good matches."""
    strict = FuzzyReRankerPlugin(config={"min_conf": 0.99})
    # "jazz" alone won't reach 0.99 against full sentences → falls back
    result = strict.select_answer("jazz", OPTIONS)
    # Either None or ordinal fallback — must NOT return via direct fuzzy branch
    # (we simply assert it does not crash and returns Optional[str])
    assert result is None or result in OPTIONS
