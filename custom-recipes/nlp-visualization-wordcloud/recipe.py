# -*- coding: utf-8 -*-
import dataiku
from spacy_tokenizer import MultilingualTokenizer
from wordcloud_generator import WordcloudGenerator
from wordcloud_exporter import WordcloudExporter
from plugin_config_loading import load_plugin_config_wordcloud


# Load config
params = load_plugin_config_wordcloud()
resource_path = dataiku.customrecipe.get_recipe_resource()

# Load tokenizer
tokenizer = MultilingualTokenizer()

# Load exporter
exporter = WordcloudExporter()

# Load wordcloud generator
generator = WordcloudGenerator(
    params["df"],
    tokenizer,
    params["text_column"],
    resource_path,
    params["language"],
    params["language_column"],
    params["subchart_column"],
)

# Generate wordclouds
generator.generate()

# Save wordclouds to folder
for fig, output_file_name in generator._generate_wordclouds():
    exporter.upload_to_folder(fig, params["output_folder"], output_file_name)
