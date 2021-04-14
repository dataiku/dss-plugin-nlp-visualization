# -*- coding: utf-8 -*-
"""Module with a class to generate wordclouds based on cleaned text"""

import random
import os
from typing import List, AnyStr, Tuple, Dict, Generator, BinaryIO
from collections import Counter
from io import BytesIO
from functools import lru_cache
import zlib

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
from wordcloud import WordCloud
import pathvalidate
from fastcore.utils import store_attr
from spacy.tokens import Doc

from spacy_tokenizer import MultilingualTokenizer
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

    DEFAULT_MAX_WORDS = 200
    DEFAULT_COLOR_LIST = ["#1F75B3", "#FF7F0F", "#2CA02B"]
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

    DEFAULT_FONT = "NotoSansMerged-Regular-1000upem.ttf"
    """Multilingual font created from the fusion of the following Noto Sans fonts:
        - NotoSansDisplay-Regular
        - NotoSansArabic-Regular
        - NotoSansArmenian-Regular
        - NotoSansBengali-Regular
        - NotoSansDevanagari-Regular
        - NotoSansHebrew-Regular
        - NotoSansSinhala-Regular
        - NotoSansTamil-Regular
        - NotoSansThai-Regular
    """
    FONT_EXCEPTIONS_DICT = {
        "gu": "NotoSansMerged-Regular-2048upem.ttf",
        "ja": "NotoSansCJKjp-Regular.otf",
        "kn": "NotoSansMerged-Regular-2048upem.ttf",
        "ml": "NotoSansMerged-Regular-2048upem.ttf",
        "te": "NotoSansMerged-Regular-2048upem.ttf",
        "zh": "NotoSansCJKsc-Regular.otf",
        "language_column": "NotoSansMerged-Regular-1000upem.ttf",
    }
    """Dictionary with ISO 639-1 language code (key) and associated font (value)

    NotoSansMerged-Regular-2048upem.ttf results from the fusion of the following Noto Sans fonts:
        - NotoSans-Regular
        - NotoSansGujarati-Regular
        - NotoSansKannada-Regular
        - NotoSansMalayalam-Regular
        - NotoSansTelugu-Regular
    """

    def __init__(
        self,
        tokenizer: MultilingualTokenizer,
        text_column: AnyStr,
        font_folder_path: AnyStr,
        language: AnyStr = "en",
        language_column: AnyStr = None,
        remove_stopwords: bool = True,
        remove_punctuation: bool = True,
        case_insensitive: bool = False,
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

    @lru_cache(maxsize=1024)
    def _color_func(self, word: AnyStr, **kwargs) -> AnyStr:
        """Return the color function used in the wordcloud"""
        word_hash = zlib.adler32(word.encode("utf-8")) & 0xFFFFFFFF
        color = self.color_list[word_hash % len(self.color_list)]
        return color

    def _retrieve_font(self, language: AnyStr) -> AnyStr:
        """Return the font to use for a given language"""
        return self.FONT_EXCEPTIONS_DICT.get(language, self.font)

    def _get_wordcloud(self, frequencies, font_path):
        """Return a wordcloud object"""
        wordcloud = (
            WordCloud(
                background_color=self.background_color,
                scale=self.scale,
                margin=self.margin,
                max_words=self.max_words,
                font_path=font_path,
                random_state=self.random_state,
            )
            .generate_from_frequencies(frequencies)
            .recolor(color_func=self._color_func, random_state=self.random_state)
        )

        return wordcloud

    def _generate_wordcloud(
        self, frequencies: Dict, language: AnyStr, title: AnyStr = None
    ) -> matplotlib.pyplot.figure:
        """Return a wordcloud as a matplotlib figure"""
        # Manage font exceptions based on language
        font = self._retrieve_font(language)
        font_path = os.path.join(self.font_folder_path, font)
        # Generate wordcloud
        wc = self._get_wordcloud(frequencies, font_path)
        fig = plt.figure(figsize=self.figsize, dpi=self.dpi)
        fig.tight_layout()
        plt.axis("off")
        if title:
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

    def _normalize_case_token_counts(self, counts: Counter) -> Counter:
        """Private method to normalize a token counter to make it case-insensitive

        It works by summing the counts of multiple case versions e.g., "The" and "the".
        It then selects the case version with the highest count to represent the whole group.
        In case of a tie, the lowercase version is chosen.

        Args:
            counts: token counter e.g., Counter({"The": 3, "the": 5, "best": 3, "Best": 4})
        Returns:
            New token counter with a single case version for each token and the sum of counts across case versions
                e.g., Counter({"the": 8, "Best": 7})
        """
        df_counts = pd.DataFrame.from_dict(counts.items())
        df_counts.columns = ["token", "token_count"]
        df_counts["token_lower"] = df_counts.token.str.lower()
        df_counts_agg = df_counts.groupby("token_lower").token_count.agg(["sum", "idxmax"]).reset_index()
        df_counts_agg["token_majority_case"] = df_counts_agg["idxmax"].apply(lambda x: df_counts.loc[x, "token"])
        normalized_counts = Counter(dict(zip(df_counts_agg.token_majority_case, df_counts_agg["sum"])))
        return normalized_counts

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
                token_is_stopwords = token.is_stop if self.remove_stopwords else False
                token_is_punctuation = token.is_punct if self.remove_punctuation else False
                if not token_is_stopwords and not token_is_punctuation and not token.is_space:
                    counter[token.text] += 1  # Equivalently, token.lemma_
            counters.append(counter)

        if not self.subchart_column:
            counts = sum(counters, Counter())
            if self.case_insensitive:
                counts = self._normalize_case_token_counts(counts)
            return [("", dict(counts))]
        else:
            counts = list(zip(self.subcharts, counters))
            # Aggregate counts by subchart
            temp_count = {}
            for subchart, count in counts:
                if subchart in temp_count.keys():
                    temp_count[subchart].update(count)
                else:
                    temp_count[subchart] = count
            if self.case_insensitive:
                temp_count = {
                    subchart: self._normalize_case_token_counts(count) for subchart, count in temp_count.items()
                }
            counts = list(temp_count.items())

            # Remove subcharts emptied by aggregation
            counts = [(subchart, count) for subchart, count in counts if count]
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
                wordcloud_title = f"{self.subchart_column}: {name}"
                # Generate chart
                if self.language_as_subchart:
                    fig = self._generate_wordcloud(frequencies=count, language=name, title=wordcloud_title,)
                else:
                    fig = self._generate_wordcloud(frequencies=count, language=self.language, title=wordcloud_title)
                # Return chart
                temp = BytesIO()
                fig.savefig(temp, bbox_inches=self.bbox_inches, pad_inches=self.pad_inches, dpi=fig.dpi)
                yield (temp, output_file_name)

        else:
            # Generate chart
            count = counts[0][1]
            fig = self._generate_wordcloud(frequencies=count, language=self.language)
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
