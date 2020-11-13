# -*- coding: utf-8 -*-

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
from time import time
from spacy_tokenizer import MultilingualTokenizer
from plugin_io_utils import count_records
import random
from wordcloud_generator import WordcloudGenerator


# Load config
input_dataset_name = get_input_names_for_role("input")[0]
output_folder_name = get_output_names_for_role("output")[0]

params_dict = get_recipe_config()
logging.info("Webapp parameters loaded: {}".format(params_dict))

text_column = params_dict.get("text_column", None)
language = params_dict.get("language", None)

subchart_column = params_dict.get("subchart_column", None)
# If parameter is saved then cleared, config retrieves ""
subchart_column = subchart_column if subchart_column != "" else None

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

# Load tokenizer
tokenizer = MultilingualTokenizer()

# Load wordcloud generator
generator = WordcloudGenerator(df, tokenizer, text_column, output_path, language, language_column, subchart_column)

# Generate wordclouds and save to folder
generator.generate()
