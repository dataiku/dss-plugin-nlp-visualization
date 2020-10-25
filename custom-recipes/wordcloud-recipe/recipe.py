import dataiku
from dataiku.customrecipe import *
import logging

logger = logging.getLogger(__name__)

import matplotlib
import matplotlib.pyplot as plt

matplotlib.use("agg")

import traceback
from typing import List, AnyStr
import pandas as pd
import spacy.lang
import os
from wordcloud import WordCloud
from collections import Counter
import datetime
from spacy_tokenizer import MultilingualTokenizer
from plugin_io_utils import count_records
import random

# -------------------------------------------------------------------------------- NOTEBOOK-CELL: CODE
DEFAULT_FILTER_TOKEN_ATTRIBUTES = (
    "is_space",
    "is_punct",
    "is_digit",
    "is_currency",
    "is_stop",
    "like_url",
    "like_email",
    "like_num",
    # "is_emoji",
    # "is_hashtag",
    "is_username",
    "is_symbol",
    "is_unit",
    "is_time",
)

max_words = 100


def exclude(token, token_attributes: List[AnyStr] = DEFAULT_FILTER_TOKEN_ATTRIBUTES):
    match_token_attributes = [getattr(token, t, False) or getattr(token._, t, False) for t in token_attributes]
    match_token_attributes.append(token.text == "-PRON-")
    filter_conditions = any(match_token_attributes)
    return filter_conditions


def color_func(word, font_size, position, orientation, random_state=None, **kwargs):
    # Return the color function used in the wordcloud
    color_list = [
        "hsl(205,71%,41%)",
        "hsl(214,56%,80%)",
        "hsl(28,100%,53%)",
        "hsl(30,100%,74%)",
        "hsl(120,57%,40%)",
        "hsl(110,57%,71%)",
    ]

    return random.choice(color_list)


def get_wordcloud(frequencies, colour_func, scale=1.7):
    # Return a wordcloud as a svg file
    wordcloud = (
        WordCloud(background_color="white", scale=scale, margin=4, max_words=max_words)
        .generate_from_frequencies(frequencies)
        .recolor(color_func=color_func, random_state=3)
    )

    return wordcloud


def generate_single_chart(df, text_column, tokenizer, language, token_attributes, max_words, color_func, lemmatize):

    # Tokenize text
    logging.info("Initializing monolingual tokenization")
    text = [df[text_column].str.cat(sep=" ")]
    docs = tokenizer.tokenize_list(text_list=text, language=language)
    logging.info("Tokenization successful")

    # Count and lemmatize tokens
    logging.info("Initializing count and lemmatization")
    counts = Counter()
    for token in docs[0]:
        if lemmatize:
            counts[(token.lemma_)] += 1  # Equivalently, token.text
        else:
            counts[(token.text)] += 1
    logging.info("Count and lemmatization successful")

    # Filter tokens
    logging.info("Initializing token filtering")
    nlp = tokenizer.spacy_nlp_dict[language]
    filtered_count = {}
    sorted_count = counts.most_common()
    i = 0
    while len(filtered_count) < max_words:
        if not exclude(nlp(sorted_count[i][0])[0], token_attributes=token_attributes):
            filtered_count[sorted_count[i][0]] = sorted_count[i][1]
        i += 1
    logging.info("Token filtering successful")

    # Generate wordcloud
    logging.info("Generating wordcloud")
    wc = get_wordcloud(filtered_count, color_func)

    return wc


# -------------------------------------------------------------------------------- NOTEBOOK-CELL: CODE
# Load config
input_dataset_name = get_input_names_for_role("input")[0]
output_folder_name = get_output_names_for_role("output")[0]

params_dict = get_recipe_config()
logging.info("Webapp parameters loaded: {}".format(params_dict))

text_column = params_dict.get("text_column", None)
language = params_dict.get("language", None)
subchart_column = params_dict.get("subchart_column", None)
lemmatize = params_dict.get("lemmatize", None)
tokens_filter = params_dict.get("tokens_filter", None)

if tokens_filter == None:
    token_attributes = DEFAULT_FILTER_TOKEN_ATTRIBUTES
else:
    token_attributes = tokens_filter

language_column = None
if language == "language_column":
    language_column = text_column + "_language_code"

# Load input dataframe
necessary_columns = [column for column in set([text_column, language_column, subchart_column]) if column != None]
df = dataiku.Dataset(input_dataset_name).get_dataframe(columns=necessary_columns)

if df.empty:
    raise Exception("Dataframe is empty")
else:
    logging.info("Read dataset of shape: {}".format(df.shape))

# Load output folder path
output_path = dataiku.Folder(output_folder_name).get_path()

# -------------------------------------------------------------------------------- NOTEBOOK-CELL: CODE
tokenizer = MultilingualTokenizer()

# -------------------------------------------------------------------------------- NOTEBOOK-CELL: CODE
wc = generate_single_chart(df, text_column, tokenizer, language, token_attributes, max_words, color_func, lemmatize)

# -------------------------------------------------------------------------------- NOTEBOOK-CELL: CODE
fig = plt.figure()
plt.imshow(wc)

# -------------------------------------------------------------------------------- NOTEBOOK-CELL: CODE
path_fig = os.path.join(output_path, "wordcloud")
plt.savefig(path_fig)