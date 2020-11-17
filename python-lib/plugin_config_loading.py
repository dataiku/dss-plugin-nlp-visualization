# -*- coding: utf-8 -*-
"""Module with utility functions for loading, resolving and validating plugin parameters"""

import logging
import re
import os
from typing import Dict, Set

import dataiku
from dataiku.customrecipe import (
    get_recipe_config,
    get_input_names_for_role,
    get_output_names_for_role,
    get_recipe_resource,
)


class PluginParamValidationError(ValueError):
    """Custom exception raised when the the plugin parameters chosen by the user are invalid"""

    pass


def load_plugin_config_wordcloud() -> Dict:
    """Utility function to validate and load language detection parameters into a clean dictionary
    Returns:
        Dictionary of parameter names (key) and values
    """
    params = {}
    # Input dataset
    input_dataset_names = get_input_names_for_role("input")
    if len(input_dataset_names) != 1:
        raise PluginParamValidationError("Please specify one input dataset")
    input_dataset = dataiku.Dataset(input_dataset_names[0])
    input_dataset_columns = [p["name"] for p in input_dataset.read_schema()]

    # Output folder
    output_folder_names = get_output_names_for_role("output")
    if len(output_folder_names) != 1:
        raise PluginParamValidationError("Please specify one output folder")
    params["output_folder"] = dataiku.Folder(output_folder_names[0])

    # Recipe parameters
    recipe_config = get_recipe_config()
    # Text column
    params["text_column"] = recipe_config.get("text_column", None)
    if params["text_column"] not in input_dataset_columns:
        raise PluginParamValidationError("Invalid text column selection")
    logging.info(f"Text column: {params['text_column']}")
    # Language selection
    # Monolingual
    params["language"] = recipe_config.get("language", None)
    if not params["language"]:
        raise PluginParamValidationError(f"Invalid language selection: {params['language']}")
    params["language_column"] = None
    # Multilingual
    if params["language"] == "language_column":
        params["language_column"] = params["text_column"] + "_language_code"
        if params["language_column"] not in input_dataset_columns:
            raise PluginParamValidationError("Invalid language column selection")
    logging.info(f"Language: {params['language']}")
    # Subcharts
    params["subchart_column"] = recipe_config.get("subchart_column", None)
    # If parameter is saved then cleared, config retrieves ""
    params["subchart_column"] = None if not params["subchart_column"] else params["subchart_column"]
    if params["subchart_column"] and ((params["subchart_column"] not in input_dataset_columns + ["order66"])):
        raise PluginParamValidationError("Invalid subcharts column selection")
    logging.info(f"Subcharts column: {params['subchart_column']}")

    # Input dataframe
    necessary_columns = [
        column
        for column in set([params["text_column"], params["language_column"], params["subchart_column"]])
        if (column not in [None, "order66"])
    ]
    params["df"] = input_dataset.get_dataframe(columns=necessary_columns)
    if params["df"].empty:
        raise PluginParamValidationError("Dataframe is empty")
    else:
        logging.info(f"Read dataset of shape: {params['df'].shape}")

    return params
