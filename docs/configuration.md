# Configuration

## Config keys

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `min_conf` | `float` | `0.65` | Fuzzy-match confidence threshold (0–1). The utterance must score at least this high against an option for Stage 1 to return it. Scores below this fall through to vocab and numeric stages. |

---

## Where to set it

### Global default — `mycroft.conf`

Applies to every skill that uses the default plugin:

```json
{
  "skills": {
    "ask_selection_plugin": "ovos-option-matcher-fuzzy-plugin",
    "ask_selection_plugin_config": {
      "min_conf": 0.65
    }
  }
}
```

### Per-skill override — `settings.json`

Place in the skill's `settings.json` to override the global value for that skill only:

```json
{
  "ask_selection_plugin": "ovos-option-matcher-fuzzy-plugin",
  "ask_selection_plugin_config": {
    "min_conf": 0.75
  }
}
```

A skill can also switch to a completely different plugin by setting `ask_selection_plugin` to another entry point name.

---

## Choosing `min_conf`

| Value | Behaviour |
|-------|-----------|
| `0.0` | Stage 1 always matches (highest-scoring option returned regardless of relevance). Skips vocab stages entirely. |
| `0.5` | Lenient — accepts rough paraphrases. May produce false positives. |
| `0.65` | **Default.** Good balance for typical short option labels. |
| `0.80` | Strict — user must name the option closely. Vocab/numeric stages handle ordinal references. |
| `1.0` | Stage 1 disabled — only vocab and numeric stages match. |

Lower values reduce the chance of `None` returns but increase the risk of wrong matches when options are similar (e.g. `["small", "smaller", "smallest"]`).

---

## Optional dependency

To enable Stage 4 (numeric fallback for positions > 10 and digit references):

```bash
pip install "ovos-option-matcher-fuzzy-plugin[number-parser]"
# or separately:
pip install ovos-number-parser
```

Without this package the plugin still works fully for Stages 1–3. Stage 4 is skipped silently if `ovos-number-parser` is not installed.
