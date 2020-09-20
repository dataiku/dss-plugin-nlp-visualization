import dataiku
import logging

logger = logging.getLogger(__name__)
import traceback
import json
from typing import List, AnyStr
import pandas as pd
from flask import request
import spacy.lang
import os
from wordcloud import WordCloud
import json
from collections import Counter
import datetime
from dataiku.customwebapp import get_webapp_config
from spacy_tokenizer import MultilingualTokenizer
from plugin_io_utils import count_records
import random


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


def get_wordcloud_svg(frequencies, colour_func, scale=1.7):
    # Return a wordcloud as a svg file
    wordcloud = (
        WordCloud(background_color="white", scale=scale, margin=4, max_words=max_words)
        .generate_from_frequencies(frequencies)
        .recolor(color_func=color_func, random_state=3)
    )

    svg = wordcloud.to_svg(embed_font=True)

    return svg


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
    svg = get_wordcloud_svg(filtered_count, color_func)
    logging.info("Wordcloud generation successful")

    response = [{"subchart": None, "svg": svg}]
    return response


def generate_multiple_charts(
    df,
    text_column,
    tokenizer,
    language,
    subchart_column,
    token_attributes,
    max_words,
    color_func,
    lemmatize,
    language_column=None,
):
    # Group data
    group_columns = [col for col in [language_column, subchart_column] if col != None]
    df.dropna(subset=group_columns, inplace=True)
    df_grouped = df.groupby(group_columns)

    # Tokenize text
    logging.info("Initializing multiple tokenizations")
    texts = []
    group_names = []
    for name, group in df_grouped:
        texts.append([group[text_column].str.cat(sep=" ")])
        group_names.append(name)

    if language_column != None and subchart_column != None:
        languages, subcharts = zip(*group_names)
        languages = list(languages)
        subcharts = list(subcharts)
        docs = [tokenizer.tokenize_list(text, language)[0] for text, language in zip(texts, languages)]
    elif subchart_column != None:
        subcharts = group_names
        languages = [language] * len(subcharts)
        docs = [tokenizer.tokenize_list(text, language)[0] for text in texts]
    else:
        languages = group_names
        docs = [tokenizer.tokenize_list(text, language)[0] for text, language in zip(texts, languages)]

    # Count and lemmatize tokens
    logging.info("Initializing count and lemmatization")
    counts = []
    for doc in docs:
        counter = Counter()
        for token in doc:
            if lemmatize:
                counter[(token.lemma_)] += 1  # Equivalently, token.text
            else:
                counter[(token.text)] += 1
        counts.append(counter)
    logging.info("Count and lemmatization successful")

    # Filter tokens
    logging.info("Initializing token filtering")
    filtered_counts = []

    for counter, language in zip(counts, languages):
        filtered_counter = {}
        nlp = tokenizer.spacy_nlp_dict[language]
        sorted_counter = counter.most_common()
        i = 0
        while len(filtered_counter) < max_words:
            if not exclude(nlp(sorted_counter[i][0])[0], token_attributes=token_attributes):
                filtered_counter[sorted_counter[i][0]] = sorted_counter[i][1]
            i += 1

        filtered_counts.append(filtered_counter)

    if subchart_column == None:
        filtered_count = sum(filtered_counts)
        logging.info("Token filtering successful")
    else:
        filtered_counts_df = pd.DataFrame(
            list(zip(subcharts, filtered_counts)),
            columns=["subchart", "filtered_count"],
        )
        filtered_counts_df = filtered_counts_df.groupby(by=["subchart"]).agg({"filtered_count": "sum"})
        logging.info("Token filtering successful")

    # Generate wordcloud
    if subchart_column == None:
        logging.info("Generating wordcloud")
        svg = get_wordcloud_svg(text, color_func)
        logging.info("Wordcloud generation successful")

        response = [{"subchart": None, "svg": svg}]

    else:
        facets = []
        svgs = []

        logging.info("Generating wordclouds")
        for name, row in filtered_counts_df.iterrows():
            wordcloud = get_wordcloud_svg(row["filtered_count"], color_func, scale=1.5)
            facets.append("<h3>" + name + "</h3>")
            svgs.append(wordcloud)
        logging.info("Wordclouds generation successful")

        response = [{"subchart": facet, "svg": svg} for facet, svg in zip(facets, svgs)]

    return response


# config = get_webapp_config().get("webAppConfig")
# dataset_name = config.get("dataset")
# dataset = dataiku.Dataset(dataset_name)
# if count_records(dataset) >= 100000:
#    raise Exception("Dataframe is too long (more than 100 000 rows)")

tokenizer = MultilingualTokenizer()


@app.route("/get_svg/<path:params>")
def get_svg(params):
    try:
        # Load parameters
        params_dict = json.loads(params)
        logging.info("Webapp parameters loaded: {}".format(params_dict))

        dataset_name = params_dict.get("dataset_name", None)
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
        necessary_columns = [
            column for column in set([text_column, language_column, subchart_column]) if column != None
        ]
        df = dataiku.Dataset(dataset_name).get_dataframe(columns=necessary_columns, limit=10000)

        if df.empty:
            raise Exception("Dataframe is empty")
        else:
            logging.info("Read dataset of shape: {}".format(df.shape))

        if language_column == None and subchart_column == None:

            response = generate_single_chart(
                df, text_column, tokenizer, language, token_attributes, max_words, color_func, lemmatize
            )
            return json.dumps(response)

        else:

            response = generate_multiple_charts(
                df,
                text_column,
                tokenizer,
                language,
                subchart_column,
                token_attributes,
                max_words,
                color_func,
                lemmatize,
                language_column,
            )
            return json.dumps(response)

    except:
        logger.error(traceback.format_exc())
        return traceback.format_exc(), 500
