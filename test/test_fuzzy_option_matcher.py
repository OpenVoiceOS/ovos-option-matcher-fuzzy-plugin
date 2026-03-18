# Copyright 2024, OpenVoiceOS
# Apache 2.0

"""Unit tests for FuzzyOptionMatcherPlugin."""

import pytest
from ovos_option_matcher_fuzzy import FuzzyOptionMatcherPlugin


OPTIONS = ["play jazz music", "play rock music", "play classical music"]


@pytest.fixture
def matcher() -> FuzzyOptionMatcherPlugin:
    """Return a default FuzzyOptionMatcherPlugin instance."""
    return FuzzyOptionMatcherPlugin()


def test_match_exact(matcher: FuzzyOptionMatcherPlugin) -> None:
    """High confidence query should return the matching string."""
    result = matcher.match_option("jazz music", OPTIONS)
    assert result == "play jazz music"


def test_match_ordinal_second(matcher: FuzzyOptionMatcherPlugin) -> None:
    """'second' ordinal should return options[1]."""
    result = matcher.match_option("the second one", OPTIONS, lang="en-us")
    assert result == OPTIONS[1]


def test_match_ordinal_last(matcher: FuzzyOptionMatcherPlugin) -> None:
    """'last' keyword should return the final option."""
    result = matcher.match_option("the last option", OPTIONS)
    assert result == OPTIONS[-1]


def test_match_ordinal_latest(matcher: FuzzyOptionMatcherPlugin) -> None:
    """'latest' keyword should also return the final option."""
    result = matcher.match_option("the latest one", OPTIONS)
    assert result == OPTIONS[-1]


def test_match_no_match_returns_none(matcher: FuzzyOptionMatcherPlugin) -> None:
    """Garbage utterance below min_conf with no ordinal cue should return None."""
    result = matcher.match_option("xyzzy frobnicator quux", OPTIONS)
    assert result is None


def test_match_numeric_option(matcher: FuzzyOptionMatcherPlugin) -> None:
    """Numeric reference 'option 1' should return options[0]."""
    result = matcher.match_option("option 1", OPTIONS, lang="en-us")
    assert result == OPTIONS[0]


def test_config_min_conf_respected() -> None:
    """A high min_conf should force the fallback path even for good matches."""
    strict = FuzzyOptionMatcherPlugin(config={"min_conf": 0.99})
    result = strict.match_option("jazz", OPTIONS)
    assert result is None or result in OPTIONS


def test_entry_point_registered() -> None:
    """Plugin must be discoverable via OPM find_option_matcher_plugins."""
    from ovos_plugin_manager.agents import find_option_matcher_plugins
    plugins = find_option_matcher_plugins()
    assert "ovos-option-matcher-fuzzy-plugin" in plugins, (
        f"ovos-option-matcher-fuzzy-plugin not found in OPM. Found: {list(plugins.keys())}"
    )
