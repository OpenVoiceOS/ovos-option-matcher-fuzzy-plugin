# ovos-option-matcher-fuzzy-plugin

## Overview

`ovos-option-matcher-fuzzy-plugin` implements the `OptionMatcherEngine` agent plugin type for OpenVoiceOS. It resolves a free-form user utterance to one of a predefined set of option slots — the kind of matching required by `OVOSSkill.ask_selection`.

**Plugin class**: `FuzzyOptionMatcherPlugin` — `ovos_option_matcher_fuzzy/__init__.py`
**Entry point group**: `opm.agents.option_matcher`
**Entry point name**: `ovos-option-matcher-fuzzy-plugin`

---

## Resolution pipeline

`FuzzyOptionMatcherPlugin.match_option(utterance, options, lang)` runs four stages in order; the first match wins.

| Stage | Mechanism | Returns |
|-------|-----------|---------|
| 1 | **Fuzzy match** — rapidfuzz `WRatio` via `ovos_utils.parse.match_one` | Matched option string |
| 2 | **Last-option vocab** — `locale/<lang>/last.voc` word in utterance | `options[-1]` |
| 3 | **Ordinal/cardinal vocab** — `first.voc`…`tenth.voc`, `one.voc`…`ten.voc`; longest phrase wins | `options[n]` |
| 4 | **Numeric fallback** — `ovos_number_parser.extract_number` (optional dep) | `options[n]` |
| — | No match | `None` |

### Multi-word ordinal entries

Each ordinal `.voc` file contains single-word forms **and** multi-word phrases such as "second one", "number two", "option two". The matcher picks the longest phrase found in the utterance, so "second one" correctly wins over the bare cardinal "one" — no regex word-boundary logic needed.

---

## Locale files

```
locale/
  <lang>/
    last.voc          # words meaning "last/final"
    first.voc         # words/phrases for position 1 (incl. "first one", "number one")
    one.voc           # cardinal for position 1
    second.voc        # words/phrases for position 2 (incl. "second one", "number two")
    two.voc
    …
    tenth.voc
    ten.voc
```

Lookup order for a missing locale file: `<lang>` → language prefix (e.g. `de`) → `en-us`.
Results are cached per language tag with `functools.lru_cache`.

### Supported languages

| Tag | Language |
|-----|----------|
| `ca-es` | Catalan |
| `cs-cz` | Czech |
| `da-dk` | Danish |
| `de-de` | German |
| `en-us` | English |
| `es-es` | Spanish |
| `eu-eu` | Basque |
| `fr-fr` | French |
| `gl-es` | Galician |
| `it-it` | Italian |
| `nl-nl` | Dutch |
| `pl-pl` | Polish |
| `pt-br` | Portuguese (Brazil) |
| `pt-pt` | Portuguese (Portugal) |
| `sv-se` | Swedish |

Translations are contributed via the [OVOS GitLocalize](https://gitlocalize.com/openvoiceos) platform. To add a new language, create a `locale/<lang>/` directory and submit a PR.

---

## Configuration

Set under `mycroft.conf` `skills` block or per-skill `settings.json`:

```json
{
  "ask_selection_plugin": "ovos-option-matcher-fuzzy-plugin",
  "ask_selection_plugin_config": {
    "min_conf": 0.65
  }
}
```

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `min_conf` | `float` | `0.65` | Fuzzy score threshold (0–1). Below this, vocab and numeric fallbacks are tried. |

---

## Adding translations

To translate the vocab files for a new language:

1. Copy `locale/en-us/` to `locale/<your-lang>/`.
2. Translate every word/phrase in each `.voc` file. **Do not translate the filename itself** — filenames are the canonical English slot names (`first.voc`, `one.voc`, etc.).
3. Multi-word entries (e.g. "second one") should be translated as natural phrases in the target language.
4. Submit a PR or contribute via GitLocalize.

---

## Public API

### `FuzzyOptionMatcherPlugin.match_option`

```python
def match_option(
    utterance: str,
    options: List[str],
    lang: Optional[str] = None,
) -> Optional[str]
```

**Args**:
- `utterance` — raw user response string
- `options` — list of candidate option strings the skill presented
- `lang` — BCP-47 language code (default `"en-us"`)

**Returns**: the matched option string, or `None` if no match.

### Module-level helpers (internal, cached)

| Function | Signature | Description |
|----------|-----------|-------------|
| `_load_last_vocab` | `(lang: str) -> Set[str]` | Load `last.voc` for *lang* |
| `_load_position_vocab` | `(lang: str) -> Dict[int, Set[str]]` | Load all ordinal+cardinal voc files into a 0-based position map |
