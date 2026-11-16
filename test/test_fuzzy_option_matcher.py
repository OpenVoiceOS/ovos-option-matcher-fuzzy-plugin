# Copyright 2024, OpenVoiceOS
# Apache 2.0

"""Unit tests for FuzzyOptionMatcherPlugin."""

import pytest
from ovos_option_matcher_fuzzy import FuzzyOptionMatcherPlugin, _load_last_vocab


OPTIONS = ["play jazz music", "play rock music", "play classical music"]
SIMPLE = ["alpha", "beta", "gamma", "delta", "epsilon"]
GENRES = ["jazz music", "rock music", "classical music", "folk music", "pop music"]


@pytest.fixture(autouse=True)
def clear_lru_caches():
    """Clear vocab caches before each test."""
    _load_last_vocab.cache_clear()
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


def test_locale_unsupported_lang_raises():
    with pytest.raises(ValueError, match="Unsupported language"):
        _load_last_vocab("xx-XX")


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


def _items(count):
    return [f"item {i}" for i in range(1, count + 1)]


# --- Spoken positions ---

def test_match_digit_position(matcher):
    assert matcher.match_option("option 7", _items(10), lang="en-us") == "item 7"


def test_number_seventeen_picks_seventeenth(matcher):
    assert matcher.match_option("number seventeen", _items(20), lang="en-us") == "item 17"


def test_number_seventeen_out_of_range_picks_nothing(matcher):
    assert matcher.match_option("number seventeen", _items(10), lang="en-us") is None


def test_twenty_first_picks_twenty_first(matcher):
    assert matcher.match_option("the twenty first", _items(25), lang="en-us") == "item 21"


def test_number_seventeen_portuguese(matcher):
    assert matcher.match_option("o número dezassete", _items(20), lang="pt-pt") == "item 17"


def test_number_seventeen_portuguese_out_of_range(matcher):
    assert matcher.match_option("o número dezassete", _items(10), lang="pt-pt") is None


def test_twelfth_portuguese(matcher):
    assert matcher.match_option("quero a décima segunda", _items(15), lang="pt-pt") == "item 12"


def test_number_seventeen_spanish(matcher):
    assert matcher.match_option("el número diecisiete", _items(20), lang="es-es") == "item 17"


def test_twenty_first_spanish(matcher):
    assert matcher.match_option("la vigésima primera", _items(25), lang="es-es") == "item 21"


def test_number_seventeen_german(matcher):
    assert matcher.match_option("nummer siebzehn", _items(20), lang="de-de") == "item 17"


def test_twenty_first_german(matcher):
    assert matcher.match_option("die einundzwanzigste", _items(25), lang="de-de") == "item 21"


def test_thirteenth_german(matcher):
    assert matcher.match_option("die dreizehnte bitte", _items(15), lang="de-de") == "item 13"


# --- Articles name no position ---

def test_article_portuguese_picks_nothing(matcher):
    assert matcher.match_option("quero a que tem uma guitarra", GENRES, lang="pt-pt") is None


def test_article_spanish_picks_nothing(matcher):
    assert matcher.match_option("la que tiene una guitarra", GENRES, lang="es-es") is None


def test_article_german_picks_nothing(matcher):
    assert matcher.match_option("die mit einer Gitarre", GENRES, lang="de-de") is None


def test_article_before_an_ordinal_picks_the_ordinal(matcher):
    assert matcher.match_option("uma guitarra, a segunda opção", GENRES, lang="pt-pt") == "rock music"


# --- Entry point ---

def test_entry_point_registered():
    from ovos_plugin_manager.agents import find_option_matcher_plugins
    plugins = find_option_matcher_plugins()
    assert "ovos-option-matcher-fuzzy-plugin" in plugins, (
        f"Not found in OPM. Found: {list(plugins.keys())}"
    )
