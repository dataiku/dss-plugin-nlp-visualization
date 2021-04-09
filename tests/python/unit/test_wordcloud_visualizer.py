# -*- coding: utf-8 -*-
# This is a test file intended to be used with pytest
# pytest automatically runs all the function starting with "test_"
# see https://docs.pytest.org for more information

import os

import pandas as pd
from collections import Counter
from PIL import Image

from spacy_tokenizer import MultilingualTokenizer
from wordcloud_visualizer import WordcloudVisualizer

font_folder_path = os.getenv("FONT_FOLDER_PATH", "path_is_no_good")
stopwords_folder_path = os.getenv("STOPWORDS_FOLDER_PATH", "path_is_no_good")
test_resource_folder_path = os.getenv("TEST_RESOURCE_FOLDER_PATH")


def test_tokenize_and_count_english():
    input_df = pd.DataFrame({"input_text": ["I hope nothing. I fear nothing. I am free. 💩 😂 #OMG"]})
    tokenizer = MultilingualTokenizer(stopwords_folder_path=stopwords_folder_path)
    worcloud_visualizer = WordcloudVisualizer(
        tokenizer=tokenizer, text_column="input_text", font_folder_path=font_folder_path, language="en"
    )
    frequencies = worcloud_visualizer.tokenize_and_count(input_df)
    assert frequencies == [("", {"hope": 1, "nothing": 2, "fear": 1, "free": 1, "💩": 1, "😂": 1, "#OMG": 1})]


def test_tokenize_and_count_multilingual():
    input_df = pd.DataFrame(
        {
            "input_text": [
                "I hope nothing. I fear Nothing. Nothing. I am free.",
                " Les sanglots longs des violons d'automne",
                "子曰：“學而不思則罔，思而不學則殆。”",
            ],
            "language": ["en", "fr", "zh"],
        }
    )
    tokenizer = MultilingualTokenizer(stopwords_folder_path=stopwords_folder_path)
    worcloud_visualizer = WordcloudVisualizer(
        tokenizer=tokenizer,
        text_column="input_text",
        font_folder_path="toto",
        language="language_column",
        language_column="language",
        subchart_column="language",
        remove_stopwords=True,
        remove_punctuation=True,
        case_insensitive=True,
    )
    frequencies = worcloud_visualizer.tokenize_and_count(input_df)
    assert frequencies == [
        ("en", Counter({"hope": 1, "Nothing": 3, "fear": 1, "free": 1})),
        ("fr", Counter({"sanglots": 1, "longs": 1, "violons": 1, "automne": 1})),
        ("zh", Counter({"子": 1, "曰": 1, "學而": 1, "不思則": 1, "罔": 1, "思而": 1, "不學則": 1}),),
    ]


def test_wordcloud_english():
    input_df = pd.DataFrame({"input_text": ["I hope nothing. I fear nothing. I am free. 💩 😂 #OMG"]})
    tokenizer = MultilingualTokenizer(stopwords_folder_path=stopwords_folder_path)
    worcloud_visualizer = WordcloudVisualizer(
        tokenizer=tokenizer, text_column="input_text", font_folder_path=font_folder_path, language="en"
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
    tokenizer = MultilingualTokenizer(stopwords_folder_path=stopwords_folder_path)
    worcloud_visualizer = WordcloudVisualizer(
        tokenizer=tokenizer,
        text_column="input_text",
        font_folder_path=font_folder_path,
        language="language_column",
        language_column="language",
        subchart_column="language",
        remove_stopwords=True,
        remove_punctuation=True,
        case_insensitive=True,
    )
    frequencies = worcloud_visualizer.tokenize_and_count(input_df)
    num_wordclouds = 0
    for temp, name in worcloud_visualizer.generate_wordclouds(frequencies):
        assert temp is not None
        assert "wordcloud_" in name
        num_wordclouds += 1
    assert num_wordclouds == 3


def test_wordcloud_deterministic():
    reference_test_image = Image.open(os.path.join(test_resource_folder_path, "test_image.png"))
    input_df = pd.DataFrame({"input_text": ["I hope nothing. I fear nothing. I am free. 💩 😂 #OMG"]})
    tokenizer = MultilingualTokenizer(stopwords_folder_path=stopwords_folder_path)
    worcloud_visualizer = WordcloudVisualizer(
        tokenizer=tokenizer,
        text_column="input_text",
        font_folder_path=font_folder_path,
        language="en",
        max_words=10,
        color_list=["#ff0000", "#0000ff", "#008000"],
    )
    frequencies = worcloud_visualizer.tokenize_and_count(input_df)
    for temp, output_file_name in worcloud_visualizer.generate_wordclouds(frequencies):
        generated_test_image = Image.open(temp)
        assert list(generated_test_image.getdata()) == list(reference_test_image.getdata())
