# -*- coding: utf-8 -*-
from dataiku.customrecipe import get_recipe_resource
from spacy_tokenizer import MultilingualTokenizer
from wordcloud_generator import WordcloudGenerator
from plugin_config_loading import load_plugin_config_wordcloud

# Load config
params = load_plugin_config_wordcloud()
resource_path = get_recipe_resource()
output_folder = params["output_folder"]

# Load tokenizer
tokenizer = MultilingualTokenizer()

# Load wordcloud generator
generator = WordcloudGenerator(
    df=params["df"],
    tokenizer=tokenizer,
    text_column=params["text_column"],
    font_path=resource_path,
    language=params["language"],
    language_column=params["language_column"],
    subchart_column=params["subchart_column"],
)

# Compute wordclouds
generator.compute()

# Save wordclouds to folder
for temp, output_file_name in generator.save_wordclouds():
    output_folder.upload_data(output_file_name, temp.getvalue())
