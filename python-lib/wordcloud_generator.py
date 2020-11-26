# -*- coding: utf-8 -*-
"""Module with a class to generate wordclouds based on cleaned text"""

import dataiku
import logging
import warnings
import matplotlib
import matplotlib.pyplot as plt
from typing import List, AnyStr
import pandas as pd
from io import BytesIO
from wordcloud import WordCloud
from collections import Counter
from spacy_tokenizer import MultilingualTokenizer
import random
import os
from utils import time_logging
from pathvalidate import sanitize_filename
from font_exceptions_dict import FONT_EXCEPTIONS_DICT
from language_dict import SUPPORTED_LANGUAGES_SPACY

matplotlib.use("agg")


class PluginUnsupportedLanguageWarning(Warning):
    """Custom warning raised when an unsupported language is detected in a language column"""

    pass


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
    DEFAULT_FONT = "NotoSansDisplay-Regular.ttf"
    DEFAULT_SCALE = 6.8
    DEFAULT_MARGIN = 4
    DEFAULT_RANDOM_STATE = 3
    DEFAULT_FIGSIZE = (38.4, 21.6)
    DEFAULT_DPI = 100
    DEFAULT_PAD_INCHES = 1
    DEFAULT_TITLEPAD = 60
    DEFAULT_TITLESIZE = 60

    def __init__(
        self,
        df: pd.DataFrame,
        tokenizer: MultilingualTokenizer,
        text_column: AnyStr,
        output_folder: dataiku.Folder,
        language: AnyStr = "en",
        language_column: AnyStr = None,
        subchart_column: AnyStr = None,
        max_words: int = DEFAULT_MAX_WORDS,
        color_list: List = DEFAULT_COLOR_LIST,
        font: str = DEFAULT_FONT,
        scale: float = DEFAULT_SCALE,
        margin: float = DEFAULT_MARGIN,
        random_state: int = DEFAULT_RANDOM_STATE,
        figsize: tuple = DEFAULT_FIGSIZE,
        dpi: int = DEFAULT_DPI,
        pad_inches: int = DEFAULT_PAD_INCHES,
        titlepad: int = DEFAULT_TITLEPAD,
        titlesize: int = DEFAULT_TITLESIZE,
    ):
        """Initialization method for the MultilingualTokenizer class, with optional arguments etailed above"""

        self.df = df
        self.tokenizer = tokenizer
        self.text_column = text_column
        self.language = language
        self.language_column = language_column
        self.subchart_column = subchart_column
        self.language_as_subchart = self.language_column == self.subchart_column
        self.output_folder = output_folder
        self.max_words = max_words
        self.color_list = color_list
        self.font = font
        self.scale = scale
        self.margin = margin
        self.random_state = random_state
        self.figsize = figsize
        self.dpi = dpi
        self.pad_inches = pad_inches
        self.titlepad = titlepad
        self.titlesize = titlesize
        if self.subchart_column == "order66":
            self.font = "DeathStar.otf"
            self.subchart_column = None

    def _color_func(self, word, font_size, position, orientation, random_state=None, **kwargs):
        """Return the color function used in the wordcloud"""
        return random.choice(self.color_list)

    def _retrieve_font(self, language):
        """Return the font to use for a given language"""
        return FONT_EXCEPTIONS_DICT.get(language, self.font)

    def _get_wordcloud(self, frequencies, font_path):
        """Return a wordcloud file"""
        wordcloud = (
            WordCloud(
                background_color="white",
                scale=self.scale,
                margin=self.margin,
                max_words=self.max_words,
                font_path=font_path,
            )
            .generate_from_frequencies(frequencies)
            .recolor(color_func=self._color_func, random_state=self.random_state)
        )

        return wordcloud

    def _generate_wordcloud(self, frequencies, title, language):
        """Return a wordcloud as a matplotlib figure"""
        # Manage font exceptions based on language
        font = self._retrieve_font(language)
        font_path = os.path.join(dataiku.customrecipe.get_recipe_resource(), font)
        # Generate wordcloud
        wc = self._get_wordcloud(frequencies, font_path)
        fig = plt.figure(figsize=self.figsize, dpi=self.dpi)
        fig.tight_layout()
        plt.axis("off")
        plt.rcParams["axes.titlepad"] = self.titlepad
        plt.rcParams["axes.titlesize"] = self.titlesize
        plt.title(title)
        plt.imshow(wc, interpolation="bilinear")
        return fig

    @time_logging(log_message="Preparing data")
    def _prepare_data(self):
        if self.subchart_column:
            # Group data per language and subchart for tokenization
            group_columns = [col for col in [self.language_column, self.subchart_column] if col]
            self.df.dropna(subset=group_columns, inplace=True)
            self.df_grouped = self.df.groupby(group_columns)
            # Filter unsupported languages contained in detected language column
            if self.language_as_subchart:
                temp = []
                unsupported_lang = []
                for group_name, group in self.df_grouped:
                    if group_name[0] in SUPPORTED_LANGUAGES_SPACY:
                        temp.append((group_name, group))
                    else:
                        unsupported_lang.append(group_name[0])
                self.df_grouped = temp
                if unsupported_lang:
                    logging.warn(
                        f"Found {len(unsupported_lang)} unsupported languages: {', '.join(unsupported_lang)}. No wordcloud will be generated for these languages"
                    )

        else:
            # Simply format data similarly
            self.df_grouped = [(self.language, self.df)]

    @time_logging(log_message="Tokenizing texts")
    def _tokenize_texts(self):
        """Tokenize each group of observations in its correct language"""
        # Get language and subchart name for each group
        self.texts = []
        self.group_names = []
        for name, group in self.df_grouped:
            self.texts.append([group[self.text_column].str.cat(sep=" ")])
            self.group_names.append(name)

        # Get tokenization languages differently depending on language/subchart settings combinations
        if not self.language_column and not self.subchart_column:
            self.languages = [self.language]
        elif self.language_column and self.subchart_column:
            languages, subcharts = zip(*self.group_names)
            self.languages = list(languages)
            self.subcharts = list(subcharts)
        elif self.subchart_column:
            self.subcharts = self.group_names
            self.languages = [self.language] * len(self.subcharts)
        else:
            self.languages = self.group_names

        # Tokenize
        self.docs = [
            self.tokenizer.tokenize_list(text, language)[0] for text, language in zip(self.texts, self.languages)
        ]

    @time_logging(log_message="Counting tokens")
    def _count_tokens(self):
        """Count tokens in each group"""
        self.counters = []
        for doc in self.docs:
            counter = Counter()
            for token in doc:
                counter[(token.text)] += 1  # Equivalently, token.lemma_
            self.counters.append(counter)
        logging.info("Count successful, aggregating counters according to chart settings")

        if not self.subchart_column:
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

    @time_logging(log_message="Generating wordclouds")
    def _generate_wordclouds(self):
        """Generate wordclouds and save them as png images"""
        if self.subchart_column:
            for name, row in self.counts_df.iterrows():
                # Generate file name and chart title
                print("name: ", name)
                output_file_name = sanitize_filename(f"wordcloud_{self.subchart_column}_{name}.png").lower()
                wordcloud_title = output_file_name[:-4]
                # Generate chart
                if self.language_as_subchart:
                    fig = self._generate_wordcloud(row["count"], wordcloud_title, name)
                else:
                    fig = self._generate_wordcloud(row["count"], wordcloud_title, self.language)
                # Save chart
                temp = BytesIO()
                fig.savefig(temp, bbox_inches="tight", pad_inches=self.pad_inches, dpi=fig.dpi)
                self.output_folder.upload_data(output_file_name, temp.getvalue())
                plt.close()
        else:
            # Generate chart
            fig = self._generate_wordcloud(self.counts, "wordcloud", self.language)
            # Save chart
            temp = BytesIO()
            fig.savefig(temp, bbox_inches="tight", pad_inches=self.pad_inches, dpi=fig.dpi)
            self.output_folder.upload_data("wordcloud.png", temp.getvalue())
            plt.close()

    def generate(self):
        self._prepare_data()
        self._tokenize_texts()
        self._count_tokens()
        self._generate_wordclouds()
