# -*- coding: utf-8 -*-
"""Module with constants defining the wordcloud font exceptions for languages not supported by the default font.
- Default font is NotoSansMerged-Regular-1000upem.ttf, which is a merged font based on various NotoSans fonts:
    - NotoSansDisplay-Regular
    - NotoSansArabic-Regular
    - NotoSansArmenian-Regular
    - NotoSansBengali-Regular
    - NotoSansDevanagari-Regular
    - NotoSansHebrew-Regular
    - NotoSansSinhala-Regular
    - NotoSansTamil-Regular
    - NotoSansThai-Regular

- NotoSansMerged-Regular-2048upem.ttf is a similar font containing fonts that couldn't be merged with precited ones:
    - NotoSansGujarati-Regular
    - NotoSansKannada-Regular
    - NotoSansMalayalam-Regular
    - NotoSansTelugu-Regular

- NotoSansCJKsc-Regular.otf couldn't be merged with other fonts as it contains too many different characters
- Arial Unicode MS is the font used in the multilingual case because of optimal language support
"""

FONT_EXCEPTIONS_DICT = {
    "gu": "NotoSansMerged-ar1000upem.ttf",
    "kn": "NotoSansMerged-ar1000upem.ttf",
    "ml": "NotoSansMerged-ar1000upem.ttf",
    "te": "NotoSansMerged-ar1000upem.ttf",
    "zh": "NotoSansMerged-ar1000upem.ttf",
    "language_column": "NotoSansMerged-ar1000upem.ttf",
}


"""
Dictionary with ISO 639-1 language code (key) and associated font (value).
"""
