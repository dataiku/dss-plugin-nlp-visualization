# -*- coding: utf-8 -*-
from dataiku.customrecipe import get_recipe_resource
from spacy_tokenizer import MultilingualTokenizer
from wordcloud_visualizer import WordcloudVisualizer
from plugin_config_loading import load_plugin_config_wordcloud

# Load config
params = load_plugin_config_wordcloud()
resource_path = get_recipe_resource()
output_folder = params["output_folder"]
df = params["df"]

# Load tokenizer
tokenizer = MultilingualTokenizer()

# Load wordcloud generator
generator = WordcloudVisualizer(
    tokenizer,
    params["text_column"],
    resource_path,
    params["language"],
    params["language_column"],
    params["subchart_column"],
)

# Prepare data and count tokens for each subchart
frequencies = generator.prepare_and_count(df)

# Save wordclouds to folder
for temp, output_file_name in generator.generate_wordclouds(frequencies):
    output_folder.upload_data(output_file_name, temp.getvalue())
