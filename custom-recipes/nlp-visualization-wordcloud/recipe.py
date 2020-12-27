# -*- coding: utf-8 -*-

import logging
from time import perf_counter

from dataiku.customrecipe import get_recipe_resource
from spacy_tokenizer import MultilingualTokenizer
from wordcloud_visualizer import WordcloudVisualizer
from plugin_config_loading import load_plugin_config_wordcloud


# Load config
params = load_plugin_config_wordcloud()
resource_path = get_recipe_resource()
output_folder = params["output_folder"]
output_partition_path = params["output_partition_path"]
df = params["df"]

# Load tokenizer
tokenizer = MultilingualTokenizer()

# Load wordcloud visualizer
worcloud_visualizer = WordcloudVisualizer(
    tokenizer=tokenizer,
    text_column=params["text_column"],
    font_path=resource_path,
    language=params["language"],
    language_column=params["language_column"],
    subchart_column=params["subchart_column"],
)

# Prepare data and count tokens for each subchart
frequencies = worcloud_visualizer.tokenize_and_count(df)

# Save wordclouds to folder
start = perf_counter()
logging.info("Generating wordclouds...")

for temp, output_file_name in worcloud_visualizer.generate_wordclouds(frequencies):
    output_folder.upload_data(output_partition_path + output_file_name, temp.getvalue())

end = perf_counter()
logging.info(f"Generating wordclouds: Done in {end - start:.2f} seconds.")
