# -*- coding: utf-8 -*-

import os
import logging
import os
from time import perf_counter

from dataiku.customrecipe import get_recipe_resource
from spacy_tokenizer import MultilingualTokenizer
from wordcloud_visualizer import WordcloudVisualizer
from plugin_config_loading import load_plugin_config_wordcloud


# Load config
params = load_plugin_config_wordcloud()
font_folder_path = os.path.join(get_recipe_resource(), "fonts")
output_folder = params["output_folder"]
output_partition_path = params["output_partition_path"]
df = params["df"]

# Load wordcloud visualizer
worcloud_visualizer = WordcloudVisualizer(
    tokenizer=MultilingualTokenizer(),
    text_column=params["text_column"],
    font_folder_path=font_folder_path,
    language=params["language"],
    language_column=params["language_column"],
    subchart_column=params["subchart_column"],
    font=params["font"],
)

# Prepare data and count tokens for each subchart
frequencies = worcloud_visualizer.tokenize_and_count(df)

# Clear output folder's target partition
output_folder.delete_path(output_partition_path)

# Save wordclouds to folder
start = perf_counter()
logging.info("Generating wordclouds...")
for temp, output_file_name in worcloud_visualizer.generate_wordclouds(frequencies):
    output_folder.upload_data(os.path.join(output_partition_path, output_file_name), temp.getvalue())

end = perf_counter()
logging.info(f"Generating wordclouds: Done in {end - start:.2f} seconds.")
