# -*- coding: utf-8 -*-
"""Module to get paths of necessary input/output folders partitions"""

import dataiku
import itertools
from typing import List, AnyStr, Dict, Generator

from utils import time_logging

DEFAULT_NR_TIME_COMPONENTS = 4
DEFAULT_INPUT_PATH_REPLACEMENT_DICT = {"%Y": None, "%M": None, "%D": None, "%H": None}
DEFAULT_OUTPUT_PATH_REPLACEMENT_DICT = {
    "%Y": "DKU_DST_YEAR",
    "%M": "DKU_DST_MONTH",
    "%D": "DKU_DST_DAY",
    "%H": "DKU_DST_HOUR",
}


@time_logging(log_message="Getting output partition path")
def get_output_partition_path(folder_id: AnyStr) -> AnyStr:
    """Function returning the path to the output folder's target partition.
    If output folder isn't partitioned, returns an empty string
    Args:
        folder_id: output folder's id
    Returns:
        String containing the output partition's path
    """
    # Create folder handle
    client = dataiku.api_client()
    folder = client.get_default_project().get_managed_folder(folder_id)

    # Check partitioning
    if not folder.get_definition().get("partitioning"):
        return ""

    # Get partitioning file path pattern
    file_path_pattern = folder.get_definition().get("partitioning").get("filePathPattern")

    # Get discrete partitioning dimensions
    dimensions = folder.get_definition().get("partitioning").get("dimensions")
    discrete_dimensions = [dimension.get("name") for dimension in dimensions if dimension.get("type") != "time"]

    # Generate path placeholders replacements dictionnary
    path_replacement_dict = DEFAULT_OUTPUT_PATH_REPLACEMENT_DICT.copy()
    for dimension in discrete_dimensions:
        replacement_key = f"%{{{dimension}}}"
        # Get flow variable containing dimension's value
        replacement_value = dataiku.get_flow_variables()["DKU_DST_" + dimension]
        path_replacement_dict[replacement_key] = replacement_value

    # Generate path
    dst_file_path = file_path_pattern
    for dimension_placeholder in path_replacement_dict.keys():
        dst_file_path = dst_file_path.replace(dimension_placeholder, path_replacement_dict[dimension_placeholder])

    dst_file_path = "".join(dst_file_path.rsplit(".*"))

    return dst_file_path


@time_logging(log_message="Getting input partitions paths")
def get_input_partitions_paths(folder_id: AnyStr) -> List[AnyStr]:
    """Function returning the paths to the input folder's required partitions.
    If input folder isn't partitioned, returns an empty string
    Args:
        folder_id: input folder's id
    Returns:
        List of strings containing the input partitions' paths
    """
    # Create folder handle
    client = dataiku.api_client()
    folder = client.get_default_project().get_managed_folder(folder_id)

    # Check partitioning
    if not folder.get_definition().get("partitioning"):
        return [""]

    # Instanciate result
    src_file_paths = []

    # Get partitioning file path pattern
    file_path_pattern = folder.get_definition().get("partitioning").get("filePathPattern")

    # Get partitioning dimensions
    dimensions = folder.get_definition().get("partitioning").get("dimensions")

    # Get time dimension name if defined
    try:
        time_dimension = [dimension.get("name") for dimension in dimensions if dimension.get("type") == "time"][0]
    except IndexError:
        time_dimension = None

    # Get discrete partitioning dimensions
    discrete_dimensions = [dimension.get("name") for dimension in dimensions if dimension.get("type") != "time"]

    # Get all necessary values per partitioning dimension
    dimension_names = [dimension.get("name") for dimension in dimensions]
    values_per_dimension = {
        dimension_name: dataiku.get_flow_variables()[f"DKU_SRC_{dimension_name}_VALUES"].replace("'", "").split(", ")
        for dimension_name in dimension_names
    }

    # Iterate over values combinations:
    for combination in dict_product(values_per_dimension):
        # Generate path placeholders replacements dictionnary
        path_replacement_dict = DEFAULT_INPUT_PATH_REPLACEMENT_DICT.copy()

        # Get time dimension components
        if time_dimension:
            time_components = combination.get(time_dimension).split("-")
            time_components += [None] * (DEFAULT_NR_TIME_COMPONENTS - len(time_components))
            (
                path_replacement_dict["%Y"],
                path_replacement_dict["%M"],
                path_replacement_dict["%D"],
                path_replacement_dict["%H"],
            ) = time_components

        # Get discrete dimensions values
        for dimension in discrete_dimensions:
            replacement_key = f"%{{{dimension}}}"
            # Get flow variable containing dimension's value
            replacement_value = combination.get(dimension)[0]
            path_replacement_dict[replacement_key] = replacement_value

        # Generate path
        src_file_path = file_path_pattern
        for dimension_placeholder in path_replacement_dict.keys():
            src_file_path = src_file_path.replace(dimension_placeholder, path_replacement_dict[dimension_placeholder])
            src_file_path = "".join(src_file_path.rsplit(".*"))

        # Add path to result
        src_file_paths.append(src_file_path)

    return src_file_paths


def dict_product(d: Dict) -> Generator[Dict, None, None]:
    """Generator to compute cartesian product of input dictionary values.
    Yields dictionaries with same keys as input dictionary, but with unpacked values"""
    keys = d.keys()
    for element in itertools.product(*d.values()):
        yield dict(zip(keys, element))
