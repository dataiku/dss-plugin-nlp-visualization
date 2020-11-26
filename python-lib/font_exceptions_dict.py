# -*- coding: utf-8 -*-
"""Module with constants defining the wordcloud font exceptions for languages not supported by Noto Sans Display"""

FONT_EXCEPTIONS_DICT = {
    "ar": "NotoSansArabic-Regular.ttf",
    "bn": "NotoSansBengali-Regular.ttf",
    "fa": "NotoSansArabic-Regular.ttf",
    "he": "NotoSansHebrew-Regular.ttf",
    "hi": "NotoSansDevanagari-Regular.ttf",
    "hy": "NotoSansArmenian-Regular.ttf",
    "kn": "NotoSansKannada-Regular.ttf",
    "mr": "NotoSansDevanagari-Regular.ttf",
    "ta": "NotoSansTamil-Regular.ttf",
    "ur": "NotoSansArabic-Regular.ttf",
    "zh": "NotoSansCJKsc-Regular.otf",
    "language_column": "Arial Unicode.ttf",
}
"""dict: Languages supported by spaCy: https://spacy.io/usage/models#languages
Dictionary with ISO 639-1 language code (key) and associated font (value).
"""
