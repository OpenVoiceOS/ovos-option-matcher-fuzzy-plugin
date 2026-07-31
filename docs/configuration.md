# Configuration

## Config keys

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `min_conf` | `float` | `0.65` | Fuzzy-match confidence threshold (0-1). The utterance must score at least this high against an option for Stage 1 to return it. Scores below this fall through to vocab and numeric stages. |

`min_conf` is read from `self.config` inside `FuzzyOptionMatcherPlugin.match_option`: `ovos_option_matcher_fuzzy/__init__.py:105`.

---

## Passing config

The `config` dict is set at instantiation time via `FuzzyOptionMatcherPlugin(config={...})`.

When the plugin is loaded automatically by `OVOSSkill.ask_selection`, it is instantiated with no arguments (`cls()`: `ovos_workshop/skills/ovos.py:1964`), so `min_conf` is always `0.65` in that path. To use a custom threshold, switch to a different plugin entry point or use the plugin directly.

**Direct instantiation with a custom threshold:**

```python
from ovos_option_matcher_fuzzy import FuzzyOptionMatcherPlugin

matcher = FuzzyOptionMatcherPlugin(config={"min_conf": 0.80})
result = matcher.match_option("rock", ["jazz", "rock", "classical"])
# "rock"
```

---

## Switching the plugin per-skill

To use a different `OptionMatcherEngine` plugin for one skill only, set `ask_selection_plugin` in that skill's `settings.json`:

```json
{
  "ask_selection_plugin": "my-custom-option-matcher-plugin"
}
```

`OVOSSkill._get_selection_engine` checks `settings.json` first, then `mycroft.conf` `skills.ask_selection_plugin`, then defaults to `"ovos-option-matcher-fuzzy-plugin"`: `ovos_workshop/skills/ovos.py:1957-1959`.

## Setting the global default

To make this plugin the system-wide default in `mycroft.conf`:

```json
{
  "skills": {
    "ask_selection_plugin": "ovos-option-matcher-fuzzy-plugin"
  }
}
```

---

## Choosing `min_conf`

| Value | Behaviour |
|-------|-----------|
| `0.0` | Stage 1 always matches (highest-scoring option returned regardless of relevance). Skips vocab stages entirely. |
| `0.5` | Lenient: accepts rough paraphrases. May produce false positives. |
| `0.65` | **Default.** Good balance for typical short option labels. |
| `0.80` | Strict: user must name the option closely. Vocab/numeric stages handle ordinal references. |
| `1.0` | Stage 1 disabled: only vocab and numeric stages match. |

Lower values reduce the chance of `None` returns but increase the risk of wrong matches when options are similar (e.g. `["small", "smaller", "smallest"]`).

---

## Optional dependency

To enable Stage 4 (numeric fallback for positions > 10 and digit references):

```bash
pip install "ovos-option-matcher-fuzzy-plugin[number-parser]"
# or separately:
pip install ovos-number-parser
```

Without this package the plugin still works fully for Stages 1-3. Stage 4 is skipped silently if `ovos-number-parser` is not installed.

---
[← How it works](how-it-works.md) · [Home](index.md) · [Localization →](localization.md)
