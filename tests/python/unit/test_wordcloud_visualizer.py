# -*- coding: utf-8 -*-
# This is a test file intended to be used with pytest
# pytest automatically runs all the function starting with "test_"
# see https://docs.pytest.org for more information

import os

import pandas as pd
from collections import Counter

from spacy_tokenizer import MultilingualTokenizer
from wordcloud_visualizer import WordcloudVisualizer

font_path = os.getenv("RESOURCE_FOLDER_PATH", "path_is_no_good")


def test_tokenize_english():
    input_df = pd.DataFrame({"input_text": ["I hope nothing. I fear nothing. I am free. 💩 😂 #OMG"]})
    tokenizer = MultilingualTokenizer()
    worcloud_visualizer = WordcloudVisualizer(
        tokenizer=tokenizer, text_column="input_text", font_path=font_path, language="en"
    )
    frequencies = worcloud_visualizer.tokenize_and_count(input_df)
    assert frequencies == [
        ("", {"I": 3, "hope": 1, "nothing": 2, ".": 3, "fear": 1, "am": 1, "free": 1, "💩": 1, "😂": 1, "#OMG": 1})
    ]


def test_tokenize_multilingual():
    input_df = pd.DataFrame(
        {
            "input_text": [
                "I hope nothing. I fear nothing. I am free.",
                " Les sanglots longs des violons d'automne",
                "子曰：“學而不思則罔，思而不學則殆。”",
            ],
            "language": ["en", "fr", "zh"],
        }
    )
    tokenizer = MultilingualTokenizer()
    worcloud_visualizer = WordcloudVisualizer(
        tokenizer=tokenizer,
        text_column="input_text",
        font_path="toto",
        language="language_column",
        language_column="language",
        subchart_column="language",
    )
    frequencies = worcloud_visualizer.tokenize_and_count(input_df)
    assert frequencies == [
        ("en", Counter({"I": 3, "hope": 1, "nothing": 2, ".": 3, "fear": 1, "am": 1, "free": 1})),
        ("fr", Counter({" ": 1, "Les": 1, "sanglots": 1, "longs": 1, "des": 1, "violons": 1, "d'": 1, "automne": 1})),
        (
            "zh",
            Counter(
                {
                    "子": 1,
                    "曰": 1,
                    "：": 1,
                    "“": 1,
                    "學而": 1,
                    "不思則": 1,
                    "罔": 1,
                    "，": 1,
                    "思而": 1,
                    "不學則": 1,
                    "殆": 1,
                    "。": 1,
                    "”": 1,
                }
            ),
        ),
    ]


def test_wordcloud_english():
    input_df = pd.DataFrame({"input_text": ["I hope nothing. I fear nothing. I am free. 💩 😂 #OMG"]})
    tokenizer = MultilingualTokenizer()
    worcloud_visualizer = WordcloudVisualizer(
        tokenizer=tokenizer, text_column="input_text", font_path=font_path, language="en"
    )
    frequencies = worcloud_visualizer.tokenize_and_count(input_df)
    for temp, output_file_name in worcloud_visualizer.generate_wordclouds(frequencies):
        assert temp is not None
        assert output_file_name == "wordcloud.png"


def test_wordcloud_multilingual():
    input_df = pd.DataFrame(
        {
            "input_text": [
                "I hope nothing. I fear nothing. I am free.",
                " Les sanglots longs des violons d'automne",
                "子曰：“學而不思則罔，思而不學則殆。”",
            ],
            "language": ["en", "fr", "zh"],
        }
    )
    tokenizer = MultilingualTokenizer()
    worcloud_visualizer = WordcloudVisualizer(
        tokenizer=tokenizer,
        text_column="input_text",
        font_path=font_path,
        language="language_column",
        language_column="language",
        subchart_column="language",
    )
    worcloud_visualizer.tokenize_and_count(input_df)
    num_wordclouds = 0
    for temp, name in worcloud_visualizer.generate_wordclouds():
        assert temp is not None
        assert "wordcloud_" in name
        num_wordclouds += 1
    assert num_wordclouds == 3
