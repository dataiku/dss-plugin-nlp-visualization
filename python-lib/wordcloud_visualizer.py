# -*- coding: utf-8 -*-
"""Module with a class to generate wordclouds based on cleaned text"""

import random
import os
from typing import List, AnyStr, Tuple, Dict, Generator, BinaryIO
from collections import Counter
from io import BytesIO

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
from wordcloud import WordCloud
import pathvalidate
from fastcore.utils import store_attr
from spacy.tokens import Doc

from spacy_tokenizer import MultilingualTokenizer
from font_exceptions_dict import FONT_EXCEPTIONS_DICT
from utils import time_logging

matplotlib.use("agg")


class WordcloudVisualizer:
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
    DEFAULT_FONT = "NotoSansMerged-ar1000upem.ttf"
    DEFAULT_SCALE = 6.8
    DEFAULT_MARGIN = 4
    DEFAULT_RANDOM_STATE = 3
    DEFAULT_FIGSIZE = (38.4, 21.6)
    DEFAULT_DPI = 100
    DEFAULT_TITLEPAD = 60
    DEFAULT_TITLESIZE = 60
    DEFAULT_PAD_INCHES = 1
    DEFAULT_BBOX_INCHES = "tight"
    DEFAULT_BACKGROUND_COLOR = "white"

    def __init__(
        self,
        tokenizer: MultilingualTokenizer,
        text_column: AnyStr,
        font_path: AnyStr,
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
        titlepad: int = DEFAULT_TITLEPAD,
        titlesize: int = DEFAULT_TITLESIZE,
        pad_inches: int = DEFAULT_PAD_INCHES,
        bbox_inches: str = DEFAULT_BBOX_INCHES,
        background_color: str = DEFAULT_BACKGROUND_COLOR,
    ):
        """Initialization method for the WordcloudVisualizer class, with optional arguments etailed above"""

        store_attr()
        random.seed(self.random_state)
        self.language_as_subchart = self.language_column == self.subchart_column
        if self.subchart_column == "order66":
            self.font = "DeathStar.otf"
            self.subchart_column = None

    def _color_func(self, word, font_size, position, orientation, random_state=None, **kwargs) -> AnyStr:
        """Return the color function used in the wordcloud"""
        return random.choice(self.color_list)

    def _retrieve_font(self, language: AnyStr) -> AnyStr:
        """Return the font to use for a given language"""
        return FONT_EXCEPTIONS_DICT.get(language, self.font)

    def _get_wordcloud(self, frequencies, font_path):
        """Return a wordcloud object"""
        wordcloud = (
            WordCloud(
                background_color=self.background_color,
                scale=self.scale,
                margin=self.margin,
                max_words=self.max_words,
                font_path=font_path,
            )
            .generate_from_frequencies(frequencies)
            .recolor(color_func=self._color_func, random_state=self.random_state)
        )

        return wordcloud

    def _generate_wordcloud(self, frequencies: Dict, title: AnyStr, language: AnyStr) -> matplotlib.pyplot.figure:
        """Return a wordcloud as a matplotlib figure"""
        # Manage font exceptions based on language
        font = self._retrieve_font(language)
        font_path = os.path.join(self.font_path, font)
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
    def _prepare_data(self, df: pd.DataFrame) -> List:
        """Private method to reshape data depending on language and subcharts settings
        Args:
            df: dataframe containing a text column and, optionally, language and subcharts columns
        Returns:
            List of pandas dataframes with one dataframe per language per subchart
        """
        if self.subchart_column or self.language_column:
            # Group data per language and subchart for tokenization
            group_columns = [col for col in [self.language_column, self.subchart_column] if col]
            df.dropna(subset=group_columns, inplace=True)
            df_grouped = df.groupby(group_columns)
        else:
            # Simply format data similarly
            df_grouped = [(self.language, df)]

        return df_grouped

    def _tokenize_texts(self, df_grouped: List) -> List:
        """Private method to tokenize each group of observations in its correct language
        Args:
            df_grouped: list of pandas dataframes with one dataframe per language per subchart
        Returns:
            List of spacy docs
        """
        # Get language and subchart name for each group
        texts = []
        group_names = []
        for name, group in df_grouped:
            texts.append([group[self.text_column].str.cat(sep=" ")])
            group_names.append(name)

        # Get tokenization languages differently depending on language/subchart settings combinations
        if not self.language_column and not self.subchart_column:
            languages = [self.language]
        elif self.language_column and self.subchart_column:
            languages, subcharts = zip(*group_names)
            languages = list(languages)
            self.subcharts = list(subcharts)
        elif self.subchart_column:
            self.subcharts = group_names
            languages = [self.language] * len(self.subcharts)
        else:
            languages = group_names

        # Tokenize
        docs = [self.tokenizer.tokenize_list(text, language)[0] for text, language in zip(texts, languages)]

        return docs

    @time_logging(log_message="Counting tokens")
    def _count_tokens(self, docs: List[Doc]) -> List[Tuple[AnyStr, Dict]]:
        """Private method to count tokens for each document in corpus
        Args:
            docs: list of spacy docs on which to count tokens
        Returns:
            List of tuples (subchart, counter) where subchart is the subchart the counter belongs to
        """
        counters = []
        for doc in docs:
            counter = Counter()
            for token in doc:
                counter[(token.text)] += 1  # Equivalently, token.lemma_
            counters.append(counter)

        if not self.subchart_column:
            # Sum values with same keys
            counts = Counter()
            for d in counters:
                counts.update(d)

            counts = [("", dict(counts))]
            return counts
        else:
            counts = list(zip(self.subcharts, counters))
            # Aggregate counts by subchart
            temp_count = {}
            for subchart, count in counts:
                if subchart in temp_count.keys():
                    temp_count[subchart].update(count)
                else:
                    temp_count[subchart] = count
            counts = list(temp_count.items())

            # Remove subcharts emptied by aggregation
            counts = [(subchart, count) for subchart, count in counts if count != {}]
            return counts

    def generate_wordclouds(self, counts: List[Tuple[AnyStr, Dict]]) -> Generator[Tuple[BinaryIO, AnyStr], None, None]:
        """Public method to generate wordclouds and yield them as bytes-like objects
        Args:
            counts: list of tuples( subchart, counter) where subchart is the subchart the counter belongs to
        Yields:
            One tuple (bytes, filename) per subchart where bytes contains data from a wordcloud png file
        """
        if self.subchart_column:
            for name, count in counts:
                # Generate file name and chart title
                output_file_name = pathvalidate.sanitize_filename(
                    f"wordcloud_{self.subchart_column}_{name}.png"
                ).lower()
                wordcloud_title = output_file_name[:-4]
                # Generate chart
                if self.language_as_subchart:
                    fig = self._generate_wordcloud(count, wordcloud_title, name)
                else:
                    fig = self._generate_wordcloud(count, wordcloud_title, self.language)
                # Return chart
                temp = BytesIO()
                fig.savefig(temp, bbox_inches=self.bbox_inches, pad_inches=self.pad_inches, dpi=fig.dpi)
                yield (temp, output_file_name)

        else:
            # Generate chart
            count = counts[0][1]
            fig = self._generate_wordcloud(count, "wordcloud", self.language)
            # Return chart
            temp = BytesIO()
            fig.savefig(temp, bbox_inches=self.bbox_inches, pad_inches=self.pad_inches, dpi=fig.dpi)
            yield (temp, "wordcloud.png")

    def tokenize_and_count(self, df: pd.DataFrame) -> List[Tuple[AnyStr, Dict]]:
        """Public method to prepare data before generating wordclouds.
        Preparation consists in tokenizing and reshaping text data according to language and subcharts settings
        Counting consists in counting tokens per subchart
        Args:
            df: DataFrame containing text data, with optional additional columns for language and subchart
        Returns:
            List of tuples (subchart, counter) where subchart is the subchart the counter belongs to
        """
        df_prepared = self._prepare_data(df)
        docs = self._tokenize_texts(df_prepared)
        counts = self._count_tokens(docs)
        return counts
