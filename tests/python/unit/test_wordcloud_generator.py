# -*- coding: utf-8 -*-
# This is a test file intended to be used with pytest
# pytest automatically runs all the function starting with "test_"
# see https://docs.pytest.org for more information

import os

import pandas as pd

from spacy_tokenizer import MultilingualTokenizer
from wordcloud_generator import WordcloudGenerator

font_path = os.getenv("RESOURCE_FOLDER_PATH", "path_is_no_good")


def test_wordcloud_english():
    input_df = pd.DataFrame({"input_text": ["I hope nothing. I fear nothing. I am free. 💩 😂 #OMG"]})
    tokenizer = MultilingualTokenizer()
    generator = WordcloudGenerator(
        df=input_df, tokenizer=tokenizer, text_column="input_text", font_path=font_path, language="en"
    )
    generator.compute()
    for temp, name in generator.save_wordclouds():
        assert temp is not None
        assert name == "wordcloud.png"


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
    generator = WordcloudGenerator(
        df=input_df,
        tokenizer=tokenizer,
        text_column="input_text",
        font_path=font_path,
        language="language_column",
        language_column="language",
        subchart_column="language",
    )
    generator.compute()
    num_wordclouds = 0
    for temp, name in generator.save_wordclouds():
        assert temp is not None
        assert "wordcloud_" in name
        num_wordclouds += 1
    assert num_wordclouds == 3
