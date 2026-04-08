# Integration

## With OVOSSkill.ask_selection (automatic)

When `ovos-option-matcher-fuzzy-plugin` is installed, `ask_selection` uses it automatically as the default matcher — no skill code changes needed.

```python
from ovos_workshop.skills.ovos import OVOSSkill

class MySkill(OVOSSkill):
    def handle_intent(self, message):
        choice = self.ask_selection(
            ["pizza", "pasta", "salad"],
            dialog="what would you like"
        )
        # choice is "pizza", "pasta", "salad", or None
        if choice:
            self.speak_dialog("you_chose", {"choice": choice})
```

The user can answer any of:
- `"pasta"` — fuzzy match
- `"the second one"` / `"number two"` / `"two"` — position vocab
- `"the last one"` — last.voc
- `"option 3"` — numeric fallback (requires `ovos-number-parser`)

### Per-skill plugin override

To use a different plugin for one skill only, set in `settings.json`:

```json
{
  "ask_selection_plugin": "my-custom-option-matcher-plugin"
}
```

### Global default

To make this plugin the system-wide default in `mycroft.conf`:

```json
{
  "skills": {
    "ask_selection_plugin": "ovos-option-matcher-fuzzy-plugin"
  }
}
```

---

## Direct usage from Python

```python
from ovos_option_matcher_fuzzy import FuzzyOptionMatcherPlugin

matcher = FuzzyOptionMatcherPlugin()

options = ["red", "green", "blue", "yellow"]

# Fuzzy
matcher.match_option("something blue", options)           # "blue"

# Ordinal
matcher.match_option("the first one", options)            # "red"
matcher.match_option("second", options)                   # "green"
matcher.match_option("number three", options)             # "blue"

# Cardinal
matcher.match_option("four", options)                     # "yellow"

# Last-word
matcher.match_option("the last", options)                 # "yellow"

# No match
matcher.match_option("I have no idea", options)           # None
```

### With a custom confidence threshold

```python
strict = FuzzyOptionMatcherPlugin(config={"min_conf": 0.85})
# Stage 1 now requires a very close fuzzy match
# Ordinal/last/numeric stages still work normally when fuzzy fails
```

Note: when the plugin is loaded by `OVOSSkill._get_selection_engine`, it is instantiated with no config (`cls()` — `ovos_workshop/skills/ovos.py:1964`). A custom `min_conf` is only effective when you instantiate the plugin directly as shown above.

### With explicit language

```python
matcher.match_option("die zweite", options, lang="de-DE")   # "green"
matcher.match_option("primera", options, lang="es-ES")      # "red"
matcher.match_option("troisième", options, lang="fr-FR")    # "blue"
```

When called through `OVOSSkill.ask_selection`, `lang` is `self.lang` — a canonical BCP-47 tag (e.g. `en-US`, `de-DE`) returned by `standardize_lang_tag`. — `ovos_workshop/skills/ovos.py:2035`

---

## Loading via OPM

```python
from ovos_plugin_manager.agents import load_option_matcher_plugin

cls = load_option_matcher_plugin("ovos-option-matcher-fuzzy-plugin")
matcher = cls(config={"min_conf": 0.7})
result = matcher.match_option("the third option", ["a", "b", "c"])
# "c"
```

---

## Writing your own OptionMatcherEngine plugin

If you need a different matching strategy (neural embeddings, LLM reranking, etc.), implement `OptionMatcherEngine` and register it under `opm.agents.option_matcher`:

```python
# my_plugin/__init__.py
from typing import List, Optional
from ovos_plugin_manager.templates.agents import OptionMatcherEngine

class MyOptionMatcher(OptionMatcherEngine):
    def match_option(self, utterance: str, options: List[str],
                     lang: Optional[str] = None) -> Optional[str]:
        # your logic here
        ...
```

```toml
# pyproject.toml
[project.entry-points."opm.agents.option_matcher"]
my-option-matcher-plugin = "my_plugin:MyOptionMatcher"
```

Skills pick it up via `ask_selection_plugin: "my-option-matcher-plugin"` in `settings.json` or `mycroft.conf`.

---

## Handling `None` returns

`match_option` returns `None` when no stage matches. `ask_selection` propagates this as `None` to the skill. Always handle it:

```python
choice = self.ask_selection(options, dialog="which_option")
if choice is None:
    self.speak_dialog("did_not_understand")
    return
```
