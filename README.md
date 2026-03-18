# ovos-option-matcher-fuzzy-plugin

Fuzzy-match `OptionMatcherEngine` plugin for [OpenVoiceOS](https://openvoiceos.org).

Resolves a free-form user utterance to one of a predefined set of option slots — the kind of matching needed by `OVOSSkill.ask_selection`. Supports 15 languages out of the box via locale vocab files, with no required dependency on a number parser.

## Install

```bash
pip install ovos-option-matcher-fuzzy-plugin
```

With optional numeric-fallback support (handles positions above 10 and raw digit references):

```bash
pip install "ovos-option-matcher-fuzzy-plugin[number-parser]"
```

## How it works

Resolution runs in four stages — first match wins:

1. **Fuzzy match** — rapidfuzz `WRatio` similarity against all options. Returns immediately if score ≥ `min_conf`.
2. **Last-option vocab** — locale-aware `last.voc` words ("last", "final", "letzte", …). Returns the final option.
3. **Ordinal/cardinal vocab** — locale files `first.voc` … `tenth.voc` and `one.voc` … `ten.voc`. Longest matching word wins to avoid false positives (e.g. "one" in "second one").
4. **Numeric fallback** — `ovos-number-parser` (optional). Handles digits and ordinals above ten.

Returns `None` if nothing matches.

## Usage

```python
from ovos_option_matcher_fuzzy import FuzzyOptionMatcherPlugin

matcher = FuzzyOptionMatcherPlugin()
options = ["play jazz music", "play rock music", "play classical music"]

# Fuzzy match
matcher.match_option("jazz music", options)            # "play jazz music"

# Ordinal
matcher.match_option("the second one", options)        # "play rock music"

# Cardinal
matcher.match_option("three", options)                 # "play classical music"

# Last-word
matcher.match_option("the last option", options)       # "play classical music"

# Non-English (German)
matcher.match_option("die erste", options, lang="de-de")  # "play jazz music"

# No match
matcher.match_option("xyzzy quux", options)            # None
```

## Configuration

Set under `mycroft.conf` `skills` block or per-skill `settings.json`:

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `min_conf` | `float` | `0.65` | Minimum fuzzy score (0–1) to accept a direct match. |

## Supported languages

Ordinal, cardinal, and last-word vocab is provided for:

`ca-es` `cs-cz` `da-dk` `de-de` `en-us` `es-es` `eu-eu` `fr-fr` `gl-es` `it-it` `nl-nl` `pl-pl` `pt-br` `pt-pt` `sv-se`

Falls back to the language prefix (`de` → `de-de`) then `en-us` if a locale file is absent.
Translations are contributed via the [OVOS GitLocalize](https://gitlocalize.com/openvoiceos) platform.

## Entry point

Registered under `opm.agents.option_matcher`:

```
ovos-option-matcher-fuzzy-plugin = ovos_option_matcher_fuzzy:FuzzyOptionMatcherPlugin
```

## License

Apache 2.0
