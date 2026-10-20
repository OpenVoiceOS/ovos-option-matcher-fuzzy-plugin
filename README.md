# ovos-option-matcher-fuzzy-plugin

Fuzzy-match `OptionMatcherEngine` plugin for [OpenVoiceOS](https://openvoiceos.org).

Resolves a free-form user utterance to one of a predefined set of option slots: the kind of matching needed by `OVOSSkill.ask_selection`. Supports 15 languages out of the box via locale vocab files, with no required dependency on a number parser.

## Install

```bash
pip install ovos-option-matcher-fuzzy-plugin
```

With optional numeric-fallback support (handles positions above 10 and raw digit references):

```bash
pip install "ovos-option-matcher-fuzzy-plugin[number-parser]"
```

## How a skill uses it

Skills call `self.ask_selection(options, dialog=...)`. The framework speaks the options to the user, collects a spoken response, then calls `FuzzyOptionMatcherPlugin.match_option` automatically. No skill code references the plugin directly.

```python
from ovos_workshop.skills.ovos import OVOSSkill

class MySkill(OVOSSkill):
    def handle_intent(self, message):
        choice = self.ask_selection(
            ["play jazz", "play rock", "play classical"],
            dialog="what would you like"
        )
        # choice is one of the list elements, or None if nothing matched
        if choice:
            self.speak_dialog("you_chose", {"choice": choice})
```

The user can answer with:
- A direct name: `"rock music"`: matched by fuzzy scoring
- An ordinal or cardinal: `"the second one"`, `"number two"`, `"two"`: matched by locale vocab
- A last-position reference: `"the last one"`: matched by `last.voc`
- A digit or higher ordinal: `"option 7"`: matched by `ovos-number-parser` if installed

`ask_selection` passes `self.lang` (canonical BCP-47, e.g. `en-US`) to the plugin.

## How it works

Resolution runs in four stages: first match wins:

1. **Fuzzy match**: rapidfuzz `WRatio` similarity against all options. Returns immediately if score ≥ `min_conf` (default `0.65`).
2. **Last-option vocab**: locale-aware `last.voc` words ("last", "final", "letzte", …). Returns the final option.
3. **Ordinal/cardinal vocab**: locale files `first.voc` … `tenth.voc` and `one.voc` … `ten.voc`. Longest matching phrase wins to avoid false positives (e.g. "one" in "second one").
4. **Numeric fallback**: `ovos-number-parser` (optional). Handles digits and ordinals above ten.

Returns `None` if nothing matches.

## Direct usage

```python
from ovos_option_matcher_fuzzy import FuzzyOptionMatcherPlugin

matcher = FuzzyOptionMatcherPlugin()
options = ["play jazz music", "play rock music", "play classical music"]

matcher.match_option("jazz music", options)                   # "play jazz music"
matcher.match_option("the second one", options)               # "play rock music"
matcher.match_option("three", options)                        # "play classical music"
matcher.match_option("the last option", options)              # "play classical music"
matcher.match_option("die erste", options, lang="de-DE")      # "play jazz music"
matcher.match_option("xyzzy quux", options)                   # None

# Custom confidence threshold
strict = FuzzyOptionMatcherPlugin(config={"min_conf": 0.85})
```

Note: when the plugin is loaded automatically by `ask_selection`, it is instantiated with no config, so `min_conf` is always `0.65`. Pass a custom value only when instantiating directly.

## Supported languages

Ordinal, cardinal, and last-word vocab is provided for:

| Tag | Language |
|-----|----------|
| `ca-ES` | Catalan |
| `cs-CZ` | Czech |
| `da-DK` | Danish |
| `de-DE` | German |
| `en-US` | English |
| `es-ES` | Spanish |
| `eu-ES` | Basque |
| `fr-FR` | French |
| `gl-ES` | Galician |
| `it-IT` | Italian |
| `nl-NL` | Dutch |
| `pl-PL` | Polish |
| `pt-BR` | Portuguese (Brazil) |
| `pt-PT` | Portuguese (Portugal) |
| `sv-SE` | Swedish |

Falls back to the language prefix (`de-DE` → `de`) then `en-US` if a locale file is absent.
Translations are contributed via the [OVOS GitLocalize](https://gitlocalize.com/openvoiceos) platform.

## Entry point

Registered under `opm.agents.option_matcher`:

```
ovos-option-matcher-fuzzy-plugin = ovos_option_matcher_fuzzy:FuzzyOptionMatcherPlugin
```

This plugin is the default when no `ask_selection_plugin` is configured. See [docs/integration.md](docs/integration.md) for how to switch plugins per-skill or globally.

## License

Apache 2.0
