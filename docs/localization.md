# Localization

The plugin ships one `.voc` file per language, `last.voc`, for 15 languages. It lives under `locale/<lang>/` and is loaded at runtime. Number words and ordinals come from [numtag](https://github.com/TigreGotico/numtag), so a missing or wrong number reading is fixed in numtag, not here.

---

## Supported languages

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

---

## File structure

```
locale/
  en-US/
    last.voc        ← words meaning "last/final"
```

**The filename is canonical English**: do not rename it. Only the content is translated.

Each file contains one word or phrase per line, lowercase. Blank lines and leading/trailing whitespace are ignored.

---

## How lookup works

For a given `lang` (e.g. `"de-DE"`), the plugin tries:

1. `locale/de-DE/<file>.voc`
2. `locale/de/<file>.voc` (language prefix without region)
3. `locale/en-US/<file>.voc` (hard fallback)

Locale folder names use canonical BCP-47 casing (e.g. `en-US`, `de-DE`, `pt-BR`). The `lang` value passed by `OVOSSkill.ask_selection` comes from `self.lang`, which is already normalized by `standardize_lang_tag` and matches this casing.: `ovos_workshop/skills/ovos.py:2035`

Results are cached per language tag in memory (`lru_cache`) so file I/O only happens once per process.

---

## Adding a new language

1. Create the directory using canonical BCP-47 casing (language subtag lowercase, region subtag uppercase):
   ```bash
   mkdir locale/xx-XX
   ```

2. Copy English as a starting point:
   ```bash
   cp locale/en-US/* locale/xx-XX/
   ```

3. Translate every line. Keep one entry per line.

4. **`last.voc`**: include all common words and inflected forms meaning "last", "final", or "latest" in the target language.

5. Check that numtag reads number words in the language. If it does not, the fix goes to numtag.

6. Submit a PR or contribute via [OVOS GitLocalize](https://gitlocalize.com/openvoiceos).

---

## Improving an existing language

Open `locale/<lang>/last.voc` and add missing:
- Inflected forms (plurals, gendered variants, case endings)
- Regional variants (e.g. `pt-BR` vs `pt-PT`)

Run the tests after editing to verify nothing regresses:

```bash
uv run pytest test/ -v
```

---

## Translation rules

| Rule | Detail |
|------|--------|
| One entry per line | No commas, semicolons, or pipes |
| Lowercase only | The plugin lowercases the utterance before matching |
| No diacritics stripping | Include the exact Unicode form users would say |
| Filename unchanged | Always `last.voc`: never translate the filename |

---
[← Configuration](configuration.md) · [Home](index.md) · [Integration →](integration.md)
