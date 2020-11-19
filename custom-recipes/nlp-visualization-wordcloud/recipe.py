# -*- coding: utf-8 -*-
from spacy_tokenizer import MultilingualTokenizer
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
