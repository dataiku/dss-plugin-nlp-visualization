# -*- coding: utf-8 -*-

import dataiku
from dataiku.customrecipe import *
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
from wordcloud_generator import WordcloudGenerator
from plugin_config_loading import load_plugin_config_wordcloud


# Load config
params = load_plugin_config_wordcloud()

# Load tokenizer
tokenizer = MultilingualTokenizer()

# Load wordcloud generator
generator = WordcloudGenerator(
    params["df"],
    tokenizer,
    params["text_column"],
    params["output_folder"],
    params["language"],
    params["language_column"],
    params["subchart_column"],
)

# Generate wordclouds and save to folder
generator.generate()
