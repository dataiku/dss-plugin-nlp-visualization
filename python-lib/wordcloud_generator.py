# -*- coding: utf-8 -*-
"""Module with a class to generate wordclouds based on cleaned text"""

import dataiku
import logging
import matplotlib
import matplotlib.pyplot as plt

matplotlib.use("agg")

import traceback
from typing import List, AnyStr
import pandas as pd
import spacy.lang
from io import BytesIO
from wordcloud import WordCloud
from collections import Counter
from time import time
from spacy_tokenizer import MultilingualTokenizer
from plugin_io_utils import count_records
import random
import os


class WordcloudGenerator:
    """Class to generate multilingual wordclouds based on text data and save them as png images
    Attributes:
        df (pandas.DataFrame): Dataframe containing text data
        tokenizer (MultilingualTokenizer): Tokenizer used for text processing
        text_column (str): Name of the df column on which to compute wordclouds
        language (str, optional): Language in which to tokenize data (for monolingual wordcloud), defaults to english.
            Use "Detected language column" for multilingual tokenization
        language_column (str, optional): Name of the language column
        subchart_column (str, optional): Name of the subcharts column to compute wordclouds on, defaults to None
        max_words (int, optional): Maximum number of words to display in wordcloud, defaults to 100
    """

    DEFAULT_MAX_WORDS = 100
    DEFAULT_COLOR_LIST = [
        "hsl(205,71%,41%)",
        "hsl(214,56%,80%)",
        "hsl(28,100%,53%)",
        "hsl(30,100%,74%)",
        "hsl(120,57%,40%)",
        "hsl(110,57%,71%)",
    ]
    DEFAULT_FONT_PATH = os.path.join(dataiku.customrecipe.get_recipe_resource(), "NotoSansDisplay-Regular.ttf")

    def __init__(
        self,
        df: pd.DataFrame,
        tokenizer: MultilingualTokenizer,
        text_column: AnyStr,
        output_folder: dataiku.core.managed_folder.Folder,
        language: AnyStr = "en",
        language_column: AnyStr = None,
        subchart_column: AnyStr = None,
        max_words: int = DEFAULT_MAX_WORDS,
        color_list: list = DEFAULT_COLOR_LIST,
        font_path: str = DEFAULT_FONT_PATH,
    ):
        # Initialization method for the MultilingualTokenizer class, with optional arguments etailed above

        self.df = df
        self.tokenizer = tokenizer
        self.text_column = text_column
        self.language = language
        self.language_column = language_column
        self.subchart_column = subchart_column
        self.output_folder = output_folder
        self.max_words = max_words
        self.color_list = color_list
        self.font_path = font_path
        if self.subchart_column == "order66":
            self.font_path = os.path.join(dataiku.customrecipe.get_recipe_resource(), "DeathStar.otf")
            self.subchart_column = None

    def _color_func(self, word, font_size, position, orientation, random_state=None, **kwargs):
        # Return the color function used in the wordcloud
        return random.choice(self.color_list)

    def _get_wordcloud(self, frequencies, scale=6.8):
        # Return a wordcloud as a svg file
        wordcloud = (
            WordCloud(
                background_color="white", scale=scale, margin=4, max_words=self.max_words, font_path=self.font_path
            )
            .generate_from_frequencies(frequencies)
            .recolor(color_func=self._color_func, random_state=3)
        )

        return wordcloud

    def _prepare_data(self):
        start = time()
        logging.info("Preparing data")
        if self.subchart_column != None:
            # Group data per language and subchart for tokenization
            group_columns = [col for col in [self.language_column, self.subchart_column] if col != None]
            self.df.dropna(subset=group_columns, inplace=True)
            self.df_grouped = self.df.groupby(group_columns)
        else:
            # Simply format data similarly
            self.df_grouped = [(self.language, self.df)]
        logging.info(f"Data preparation: Done in {(time() - start):.2f} seconds.")

    def _tokenize_texts(self):
        # Tokenize each group of observations in its correct language
        start = time()
        logging.info("Initializing tokenization")

        # Get language and subchart name for each group
        self.texts = []
        self.group_names = []
        for name, group in self.df_grouped:
            self.texts.append([group[self.text_column].str.cat(sep=" ")])
            self.group_names.append(name)

        # Get tokenization languages differently depending on language/subchart settings combinations
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

        # Tokenize
        self.docs = [
            self.tokenizer.tokenize_list(text, language)[0] for text, language in zip(self.texts, self.languages)
        ]
        logging.info(f"Tokenization done in {(time() - start):.2f} seconds.")

    def _count_tokens(self):
        # Count tokens in each group
        start = time()
        logging.info("Initializing count")
        self.counters = []
        for doc in self.docs:
            counter = Counter()
            for token in doc:
                counter[(token.text)] += 1  # Equivalently, token.lemma_
            self.counters.append(counter)
        logging.info("Count successful, aggregating counters according to chart settings")

        if self.subchart_column == None:
            # sum the values with same keys
            self.counts = Counter()
            for d in self.counters:
                self.counts.update(d)

            self.counts = dict(self.counts)
        else:
            self.counts_df = pd.DataFrame(
                list(zip(self.subcharts, self.counters)),
                columns=["subchart", "count"],
            )
            self.counts_df = self.counts_df.groupby(by=["subchart"]).agg({"count": "sum"})
            # remove subcharts emptied by filter
            self.counts_df = self.counts_df.loc[self.counts_df["count"] != {}, :]

        logging.info(f"Counter aggregation successful, counting done in {(time() - start):.2f} seconds.")

    def _generate_wordclouds(self):
        # Generate wordclouds and save them as png images
        start = time()
        logging.info("Generating wordclouds")
        if self.subchart_column != None:
            for name, row in self.counts_df.iterrows():
                # Generate chart
                plt.close()
                wc = self._get_wordcloud(row["count"])
                fig = plt.figure(figsize=(38.4, 21.6), dpi=100)
                fig.tight_layout()
                plt.axis("off")
                plt.imshow(wc, interpolation="bilinear")
                # Save chart
                temp = BytesIO()
                fig.savefig(temp, bbox_inches="tight", pad_inches=0, dpi=fig.dpi)
                self.output_folder.upload_data("wordcloud_" + name + ".png", temp.getvalue())
            logging.info(f"Wordclouds generation done in {(time() - start):.2f} seconds.")
        else:
            # Generate chart
            plt.close()
            wc = self._get_wordcloud(self.counts)
            fig = plt.figure(figsize=(38.4, 21.6), dpi=100)
            fig.tight_layout()
            plt.axis("off")
            plt.imshow(wc, interpolation="bilinear")
            # Save chart
            temp = BytesIO()
            fig.savefig(temp, bbox_inches="tight", pad_inches=0, dpi=fig.dpi)
            self.output_folder.upload_data("wordcloud.png", temp.getvalue())
            logging.info(f"Wordcloud generation done in {(time() - start):.2f} seconds.")

    def generate(self):
        self._prepare_data()
        self._tokenize_texts()
        self._count_tokens()
        self._generate_wordclouds()
