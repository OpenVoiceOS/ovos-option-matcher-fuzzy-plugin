# ovos-option-matcher-fuzzy-plugin

Resolves a user's spoken response to one of a predefined list of options.

`OVOSSkill.ask_selection` uses it for multiple-choice prompts, such as asking the user to pick pizza, pasta, or salad. The plugin maps what the user said back to one of the option slots.

## Docs

- [How it works](how-it-works.md): resolution pipeline, matching stages, examples
- [Configuration](configuration.md): `min_conf`, per-skill overrides, mycroft.conf
- [Localization](localization.md): adding or improving translations for a language
- [Integration](integration.md): using the plugin from skills and custom code

## Quick start

```bash
pip install ovos-option-matcher-fuzzy-plugin
# or with numeric-fallback support for positions 11+:
pip install "ovos-option-matcher-fuzzy-plugin[number-parser]"
```

```python
from ovos_option_matcher_fuzzy import FuzzyOptionMatcherPlugin

matcher = FuzzyOptionMatcherPlugin()
options = ["pizza", "pasta", "salad"]

matcher.match_option("I'll have pasta", options)        # "pasta"
matcher.match_option("the second one", options)         # "pasta"
matcher.match_option("number two", options)             # "pasta"
matcher.match_option("two", options)                    # "pasta"
matcher.match_option("the last one", options)           # "salad"
matcher.match_option("something else entirely", options) # None
```

## Key facts

| | |
|--|--|
| **Package** | `ovos-option-matcher-fuzzy-plugin` |
| **Python module** | `ovos_option_matcher_fuzzy` |
| **Plugin class** | `FuzzyOptionMatcherPlugin` |
| **Base class** | `OptionMatcherEngine` (`ovos_plugin_manager.templates.agents`) |
| **Entry point group** | `opm.agents.option_matcher` |
| **Entry point name** | `ovos-option-matcher-fuzzy-plugin` |
| **Required deps** | `ovos-plugin-manager`, `rapidfuzz` |
| **Optional deps** | `ovos-number-parser` (positions 11+, digit references) |
| **Languages** | 15 built-in: `ca-ES` `cs-CZ` `da-DK` `de-DE` `en-US` `es-ES` `eu-ES` `fr-FR` `gl-ES` `it-IT` `nl-NL` `pl-PL` `pt-BR` `pt-PT` `sv-SE`: see [Localization](localization.md) |
