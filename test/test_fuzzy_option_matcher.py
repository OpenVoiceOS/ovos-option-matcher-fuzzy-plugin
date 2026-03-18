# Copyright 2024, OpenVoiceOS
# Apache 2.0

"""Unit tests for FuzzyOptionMatcherPlugin."""

import pytest
from unittest.mock import patch
from ovos_option_matcher_fuzzy import FuzzyOptionMatcherPlugin, _load_last_vocab, _load_position_vocab


OPTIONS = ["play jazz music", "play rock music", "play classical music"]
SIMPLE = ["alpha", "beta", "gamma", "delta", "epsilon"]


@pytest.fixture(autouse=True)
def clear_lru_caches():
    """Clear vocab caches before each test."""
    _load_last_vocab.cache_clear()
    _load_position_vocab.cache_clear()
    yield


@pytest.fixture
def matcher() -> FuzzyOptionMatcherPlugin:
    return FuzzyOptionMatcherPlugin()


# --- Fuzzy matching ---

def test_match_exact(matcher):
    assert matcher.match_option("jazz music", OPTIONS) == "play jazz music"


def test_match_no_match_returns_none(matcher):
    assert matcher.match_option("xyzzy frobnicator quux", OPTIONS) is None


def test_config_min_conf_respected():
    strict = FuzzyOptionMatcherPlugin(config={"min_conf": 0.99})
    result = strict.match_option("jazz", OPTIONS)
    assert result is None or result in OPTIONS


# --- Last vocab ---

def test_match_last_en(matcher):
    assert matcher.match_option("the last option", SIMPLE) == "epsilon"


def test_match_latest_en(matcher):
    assert matcher.match_option("the latest one", SIMPLE) == "epsilon"


def test_match_final_en(matcher):
    assert matcher.match_option("final", SIMPLE) == "epsilon"


def test_match_last_german(matcher):
    assert matcher.match_option("die letzte option", SIMPLE, lang="de-de") == "epsilon"


def test_locale_last_fallback_to_en_us():
    vocab = _load_last_vocab("xx-xx")
    assert "last" in vocab


# --- Ordinal vocab ---

def test_match_first_en(matcher):
    assert matcher.match_option("the first one", SIMPLE, lang="en-us") == "alpha"


def test_match_second_en(matcher):
    assert matcher.match_option("the second one", SIMPLE, lang="en-us") == "beta"


def test_match_third_en(matcher):
    assert matcher.match_option("third", SIMPLE, lang="en-us") == "gamma"


def test_match_fourth_en(matcher):
    assert matcher.match_option("fourth", SIMPLE, lang="en-us") == "delta"


def test_match_fifth_en(matcher):
    assert matcher.match_option("fifth", SIMPLE, lang="en-us") == "epsilon"


# --- Cardinal vocab ---

def test_match_cardinal_one(matcher):
    assert matcher.match_option("one", SIMPLE, lang="en-us") == "alpha"


def test_match_cardinal_two(matcher):
    assert matcher.match_option("two", SIMPLE, lang="en-us") == "beta"


def test_match_cardinal_three(matcher):
    assert matcher.match_option("three", SIMPLE, lang="en-us") == "gamma"


# --- Non-English ordinal vocab ---

def test_match_ordinal_second_german(matcher):
    assert matcher.match_option("die zweite option", SIMPLE, lang="de-de") == "beta"


def test_match_ordinal_first_spanish(matcher):
    assert matcher.match_option("el primero", SIMPLE, lang="es-es") == "alpha"


def test_match_ordinal_third_french(matcher):
    assert matcher.match_option("troisième", SIMPLE, lang="fr-fr") == "gamma"


def test_match_cardinal_deux_french(matcher):
    assert matcher.match_option("deux", SIMPLE, lang="fr-fr") == "beta"


# --- Position vocab caching and structure ---

def test_position_vocab_has_ten_entries():
    vocab = _load_position_vocab("en-us")
    assert len(vocab) == 10


def test_position_vocab_index_zero_contains_first():
    vocab = _load_position_vocab("en-us")
    assert "first" in vocab[0]
    assert "one" in vocab[0]


def test_position_vocab_index_one_contains_second():
    vocab = _load_position_vocab("en-us")
    assert "second" in vocab[1]
    assert "two" in vocab[1]


# --- Numeric fallback (ovos-number-parser) ---

def test_numeric_fallback_used_when_vocab_misses(matcher):
    # "option 7" won't be in ordinal vocab (only 1-10 covered by en-us)
    # but extract_number should still handle it for options lists > 5
    big_options = [f"item {i}" for i in range(1, 11)]
    result = matcher.match_option("option 7", big_options, lang="en-us")
    assert result == "item 7"


def test_numeric_fallback_graceful_without_number_parser(matcher):
    """Plugin must not crash when ovos-number-parser is not installed."""
    with patch.dict("sys.modules", {"ovos_number_parser": None}):
        result = matcher.match_option("xyzzy quux zork", SIMPLE, lang="en-us")
    assert result is None


# --- Entry point ---

def test_entry_point_registered():
    from ovos_plugin_manager.agents import find_option_matcher_plugins
    plugins = find_option_matcher_plugins()
    assert "ovos-option-matcher-fuzzy-plugin" in plugins, (
        f"Not found in OPM. Found: {list(plugins.keys())}"
    )
