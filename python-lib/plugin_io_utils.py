# -*- coding: utf-8 -*-
"""Module with read/write utility functions which are *not* based on the Dataiku API"""

import re
from typing import List, AnyStr
import dataiku

TIME_DIMENSION_PATTERNS = {"DKU_DST_YEAR": "%Y", "DKU_DST_MONTH": "%M", "DKU_DST_DAY": "%D", "DKU_DST_HOUR": "%H"}


def truncate_text_list(text_list: List[AnyStr], num_characters: int = 140) -> List[AnyStr]:
    """Truncate a list of strings to a given number of characters
    Args:
        text_list: List of strings
        num_characters: Number of characters to truncate each string to
    Returns:
       List with truncated strings
    """
    output_text_list = []
    for text in text_list:
        if len(text) > num_characters:
            output_text_list.append(text[:num_characters] + " (...)")
        else:
            output_text_list.append(text)
    return output_text_list


def generate_unique(name: AnyStr, existing_names: List[AnyStr], prefix: AnyStr = None) -> AnyStr:
    """Generate a unique name among existing ones by suffixing a number and adding a prefix
    Args:
        name: Input name
        existing_names: List of existing names
        prefix: Optional prefix to add to the output name
    Returns:
       Unique name with a number suffix in case of conflict, and an optional prefix
    """
    name = re.sub(r"[^\x00-\x7F]", "_", name).replace(
        " ", "_"
    )  # replace non ASCII and whitespace characters by an underscore _
    if prefix:
        new_name = f"{prefix}_{name}"
    else:
        new_name = name
    for j in range(1, 1001):
        if new_name not in existing_names:
            return new_name
        new_name = f"{new_name}_{j}"
    raise RuntimeError(f"Failed to generated a unique name for '{name}'")


def get_partition_root(dataset):
    """Retrieve the partition root path using a dataiku.Dataset.
    Args:
        dataset (dataiku.Dataset): Input or output dataset of the recipe used to retrieve the partition path pattern.
    Returns:
        Partition path or None if dataset is not partitioned.
    """
    dku_flow_variables = dataiku.get_flow_variables()
    file_path_pattern = dataset.get_config().get("partitioning").get("filePathPattern", None)
    if file_path_pattern is None:
        return None
    dimensions = get_dimensions(dataset)
    partitions = get_partitions(dku_flow_variables, dimensions)
    file_path = complete_file_path_pattern(file_path_pattern, partitions, dimensions)
    file_path = complete_file_path_time_pattern(dku_flow_variables, file_path)
    print("ALX:file_path={}".format(file_path))
    return file_path


def get_dimensions(dataset):
    """Retrieve the list of partition dimension names.
    Args:
        dataset (dataiku.Dataset)
    Returns:
        List of dimensions.
    """
    dimensions_dict = dataset.get_config().get("partitioning").get("dimensions")
    dimensions = []
    for dimension in dimensions_dict:
        dimensions.append(dimension.get("name"))
    return dimensions


def get_partitions(dku_flow_variables, dimensions):
    """Retrieve the list of partition values corresponding to the partition dimensions.
    Args:
        dku_flow_variables (dict): Dictionary of flow variables for a project.
        dimensions (list): List of partition dimensions.
    Raises:
        ValueError: If a 'DKU_DST_$DIMENSION' is not in dku_flow_variables.
    Returns:
        List of partitions.
    """
    partitions = []
    for dimension in dimensions:
        partition = dku_flow_variables.get("DKU_DST_{}".format(dimension))
        if partition is None:
            raise ValueError(
                "Partition dimension '{}' not found in output.\
                     Make sure the output has the same partitioning as the input".format(
                    dimension
                )
            )
        partitions.append(partition)
    return partitions


def complete_file_path_pattern(file_path_pattern, partitions, dimensions):
    """Fill the placeholders of the partition path pattern for the discrete dimensions with the right partition values.
    Args:
        file_path_pattern (str)
        partitions (list): List of partition values corresponding to the partition dimensions.
        dimensions (list): List of partition dimensions.
    Returns:
        File path prefix. Time dimensions pattern are not filled.
    """
    file_path = file_path_pattern.replace(".*", "")
    for partition, dimension in zip(partitions, dimensions):
        file_path = file_path.replace("%{{{}}}".format(dimension), partition)
    return file_path


def complete_file_path_time_pattern(dku_flow_variables, file_path_pattern):
    """Fill the placeholders of the partition path pattern for the time dimensions with the right partition values.
    Args:
        dku_flow_variables (dict): Dictionary of flow variables for a project.
        file_path_pattern (str)
    Returns:
        File path prefix.
    """
    file_path = file_path_pattern
    for time_dimension in TIME_DIMENSION_PATTERNS:
        time_value = dku_flow_variables.get(time_dimension)
        if time_value is not None:
            time_pattern = TIME_DIMENSION_PATTERNS.get(time_dimension)
            file_path = file_path.replace(time_pattern, time_value)
    return file_path
