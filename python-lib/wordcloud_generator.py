# -*- coding: utf-8 -*-
"""Module with a class to generate a wordcloud based on cleaned text"""

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


class wordcloud_generator:
    """Class to generate a multilingual wordcloud based on text data
    Attributes:
        default_language (str): Fallback language code in ISO 639-1 format
        use_models (bool): If True, load spaCy models for available languages.
            Slower but adds additional tagging capabilities to the pipeline.
        hashtags_as_token (bool): Treat hashtags as one token instead of two
        batch_size (int): Number of documents to process in spaCy pipelines
        spacy_nlp_dict (dict): Dictionary holding spaCy Language instances (value) by language code (key)
        tokenized_column (str): Name of the dataframe column storing tokenized documents
    """

    DEFAULT_MAX_WORDS = 100
    DEFAULT_NUM_PROCESS = 2

    def __init__(
        self,
        df: pd.DataFrame,
        tokenizer: MultilingualTokenizer,
        text_column: AnyStr,
        language: AnyStr,
        language_column: AnyStr,
        subchart_column: AnyStr,
        path: AnyStr,
        max_words: int = DEFAULT_MAX_WORDS,
    ):
        """Initialization method for the MultilingualTokenizer class, with optional arguments
        Args:
            default_language (str, optional): Fallback language code in ISO 639-1 format.
                Default is the "multilingual language code": https://spacy.io/models/xx
            use_models: If True, loads spaCy models, which is slower but allows to retrieve
                Part-of-Speech and Entities tags for downstream tasks
            hashtags_as_token (bool, optional): Treat hashtags as one token instead of two
                Default is True, which overrides the spaCy default behavior
            batch_size (int, optional): Number of documents to process in spaCy pipelines
                Default is set by the DEFAULT_BATCH_SIZE class constant
        """
        self.df = df
        self.tokenizer = tokenizer
        self.text_column = text_column
        self.language = language
        self.language_column = language_column
        self.subchart_column = subchart_column
        self.path = path
        self.max_words = max_words

    def _color_func(self, word, font_size, position, orientation, random_state=None, **kwargs):
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

    def _get_wordcloud(self, frequencies, scale=6.8):
        # Return a wordcloud as a svg file
        wordcloud = (
            WordCloud(background_color="white", scale=scale, margin=4, max_words=self.max_words)
            .generate_from_frequencies(frequencies)
            .recolor(color_func=self._color_func, random_state=3)
        )

        return wordcloud

    def _prepare_data(self):
        if self.subchart_column != None:
            # Group data per language and subchart for tokenization
            group_columns = [col for col in [self.language_column, self.subchart_column] if col != None]
            self.df.dropna(subset=group_columns, inplace=True)
            self.df_grouped = self.df.groupby(group_columns)
        else:
            # Simply format data similarly
            self.df_grouped = [(self.language, self.df)]

    def _tokenize_texts(self):
        logging.info("Initializing multiple tokenizations")
        self.texts = []
        self.group_names = []
        for name, group in self.df_grouped:
            self.texts.append([group[self.text_column].str.cat(sep=" ")])
            self.group_names.append(name)

        if self.language_column == None and self.subchart_column == None:
            self.languages = [self.language]
        elif self.language_column != None and self.subchart_column != None:
            languages, subcharts = zip(*self.group_names)
            self.languages = list(languages)
            self.subcharts = list(subcharts)
        elif self.subchart_column != None:
            self.subcharts = self.group_names
            self.languages = [self.language] * len(self.subcharts)
        else:
            self.languages = self.group_names

        self.docs = [
            self.tokenizer.tokenize_list(text, language)[0] for text, language in zip(self.texts, self.languages)
        ]

    def _count_tokens(self):
        logging.info("Initializing count")
        self.counters = []
        for doc in self.docs:
            counter = Counter()
            for token in doc:
                counter[(token.text)] += 1  # Equivalently, token.text
            self.counters.append(counter)
        logging.info("Count successful, aggregating counters according to chart settings")

        if self.subchart_column == None:
            # sum the values with same keys
            self.counts = Counter()
            for d in self.counters:
                self.counts.update(d)

            self.counts = dict(self.counts)
            logging.info("Counter aggregation successful")
        else:
            self.counts_df = pd.DataFrame(
                list(zip(self.subcharts, self.counters)),
                columns=["subchart", "count"],
            )
            self.counts_df = self.counts_df.groupby(by=["subchart"]).agg({"count": "sum"})
            # remove subcharts emptied by filter
            self.counts_df = self.counts_df.loc[self.counts_df["count"] != {}, :]
            logging.info("Counter aggregation successful")

    def _generate_wordclouds(self):
        logging.info("Generating wordclouds")
        if self.subchart_column != None:
            for name, row in self.counts_df.iterrows():
                print(name, row)
                plt.close()
                wc = self._get_wordcloud(row["count"])
                fig = plt.figure(figsize=(38.4, 21.6), dpi=100)
                fig.tight_layout()
                plt.axis("off")
                plt.imshow(wc, interpolation="bilinear")
                path_fig = os.path.join(self.path, "wordcloud_" + name)
                plt.savefig(path_fig, bbox_inches="tight", pad_inches=0, dpi=fig.dpi)
            logging.info("Wordclouds generation successful")
        else:
            plt.close()
            wc = self._get_wordcloud(self.counts)
            fig = plt.figure(figsize=(38.4, 21.6), dpi=100)
            fig.tight_layout()
            plt.axis("off")
            plt.imshow(wc, interpolation="bilinear")
            path_fig = os.path.join(self.path, "wordcloud")
            plt.savefig(path_fig, bbox_inches="tight", pad_inches=0, dpi=fig.dpi)
            logging.info("Wordcloud generation successful")

    def generate(self):
        self._prepare_data()
        self._tokenize_texts()
        self._count_tokens()
        self._generate_wordclouds()
