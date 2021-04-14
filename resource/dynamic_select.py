# -*- coding: utf-8 -*-

from language_support import SUPPORTED_LANGUAGES_SPACY
from color_palettes import DSS_BUILTIN_COLOR_PALETTES


def do(payload, config, plugin_config, inputs):
    if payload.get("parameterName") == "language":
        language_choices = sorted(
            [{"value": k, "label": v} for k, v in SUPPORTED_LANGUAGES_SPACY.items()], key=lambda x: x.get("label")
        )
        language_choices.insert(0, {"value": "language_column", "label": "Language column"})
        return {"choices": language_choices}
    elif payload.get("parameterName") == "color_palette":
        color_palette_choices = [
            {"value": color_palette["id"], "label": color_palette["name"]}
            for color_palette in DSS_BUILTIN_COLOR_PALETTES
        ]
        color_palette_choices.append({"value": "custom", "label": "Custom palette"})
        return {"choices": color_palette_choices}
    else:
        return {"choices": []}
