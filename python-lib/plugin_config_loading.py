# -*- coding: utf-8 -*-
"""Module with utility functions for loading, resolving and validating plugin parameters"""

import logging
from typing import Dict
import dataiku
from dataiku.customrecipe import (
    get_recipe_config,
    get_input_names_for_role,
    get_output_names_for_role,
)

from language_dict import SUPPORTED_LANGUAGES_SPACY
from plugin_partitioning_utils import get_output_partition_path


class PluginParamValidationError(ValueError):
    """Custom exception raised when the plugin parameters chosen by the user are invalid"""

    pass


def load_plugin_config_wordcloud() -> Dict:
    """Utility function to validate and load language detection parameters into a clean dictionary

    Returns:
        Dictionary of parameter names (key) and values

    """
    params = {}
    # Input dataset
    input_dataset_names = get_input_names_for_role("input_dataset")
    if len(input_dataset_names) != 1:
        raise PluginParamValidationError("Please specify one input dataset")
    input_dataset = dataiku.Dataset(input_dataset_names[0])
    input_dataset_columns = [p["name"] for p in input_dataset.read_schema()]

    # Output folder
    output_folder_names = get_output_names_for_role("output_folder")
    if len(output_folder_names) != 1:
        raise PluginParamValidationError("Please specify one output folder")
    params["output_folder"] = dataiku.Folder(output_folder_names[0])

    # Partition handling
    output_folder_id = output_folder_names[0].split(".")[-1]
    params["output_partition_path"] = get_output_partition_path(output_folder_id)

    # Recipe parameters
    recipe_config = get_recipe_config()

    # Text column
    params["text_column"] = recipe_config.get("text_column")
    if params["text_column"] not in input_dataset_columns:
        raise PluginParamValidationError(f"Invalid text column selection: {params['text_column']}")
    logging.info(f"Text column: {params['text_column']}")
    # Language selection
    params["language"] = recipe_config.get("language")
    if params["language"] == "language_column":
        params["language_column"] = recipe_config.get("language_column")
        if params["language_column"] not in input_dataset_columns:
            raise PluginParamValidationError(f"Invalid language column selection: {params['language_column']}")
        logging.info(f"Language column: {params['language_column']}")
    else:
        if not params["language"]:
            raise PluginParamValidationError("Empty language selection")
        if params["language"] not in SUPPORTED_LANGUAGES_SPACY:
            raise PluginParamValidationError(f"Unsupported language code: {params['language']}")
        params["language_column"] = None
        logging.info(f"Language: {params['language']}")
    # Subcharts
    params["subchart_column"] = recipe_config.get("subchart_column")
    # If parameter is saved then cleared, config retrieves ""
    params["subchart_column"] = None if not params["subchart_column"] else params["subchart_column"]
    if params["subchart_column"] and ((params["subchart_column"] not in input_dataset_columns + ["order66"])):
        raise PluginParamValidationError(f"Invalid categorical column selection: {params['subchart_column']}")
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
    # Check if unsupported languages in multilingual case
    elif params["language_column"]:
        languages = set(params["df"][params["language_column"]].unique())
        unsupported_lang = languages - SUPPORTED_LANGUAGES_SPACY.keys()
        if unsupported_lang:
            raise PluginParamValidationError(
                f"Found {len(unsupported_lang)} unsupported languages: {', '.join(sorted(unsupported_lang))}"
            )

    logging.info(f"Read dataset of shape: {params['df'].shape}")

    return params
