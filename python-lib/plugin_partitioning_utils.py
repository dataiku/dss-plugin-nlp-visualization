# -*- coding: utf-8 -*-
"""Module to get paths of necessary input/output folders partitions"""

import dataiku
import re
import itertools
from typing import List, AnyStr, Dict, Generator

from utils import time_logging

PARTITION_PATH_PATTERN = "(%Y|%M|%D|%H|%{.*})"
DISCRETE_DIMENSION_PATTERN = "%{(.*)}"
DEFAULT_NR_TIME_COMPONENTS = 4
INPUT_DEFAULT_FLOW_VARIABLES_DICT = {"%Y": None, "%M": None, "%D": None, "%H": None}
OUTPUT_DEFAULT_FLOW_VARIABLES_DICT = {
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

    # Get partitioning settings
    file_path_pattern = folder.get_definition().get("partitioning").get("filePathPattern")
    partiton_dimensions = re.findall(PARTITION_PATH_PATTERN, file_path_pattern)

    # Get all necessary values per partitioning dimension
    flow_variables_dict = OUTPUT_DEFAULT_FLOW_VARIABLES_DICT.copy()
    for dimension in partiton_dimensions:
        if dimension not in flow_variables_dict.keys():
            flow_variables_dict[dimension] = "DKU_DST_" + re.findall(DISCRETE_DIMENSION_PATTERN, dimension)[0]

    # Generate path
    dst_file_path = file_path_pattern
    for dimension in partiton_dimensions:
        variable = flow_variables_dict[dimension]
        dst_file_path = dst_file_path.replace(dimension, dataiku.get_flow_variables()[variable])

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

    # Get partitioning settings
    file_path_pattern = folder.get_definition().get("partitioning").get("filePathPattern")
    partiton_dimensions = re.findall(PARTITION_PATH_PATTERN, file_path_pattern)

    # Get time dimension name if defined
    dimensions = folder.get_definition().get("partitioning").get("dimensions")
    try:
        time_dimension = [dimension.get("name") for dimension in dimensions if dimension.get("type") == "time"][0]
    except IndexError:
        time_dimension = None

    # Get all necessary values per partitioning dimension
    dimension_names = [dimension.get("name") for dimension in dimensions]
    values_per_dimension = {
        dimension: dataiku.get_flow_variables()[f"DKU_SRC_{dimension}_VALUES"].replace("'", "").split(", ")
        for dimension in dimension_names
    }

    # Iterate over values combinations:
    for combination in dict_product(values_per_dimension):
        flow_variables_dict = INPUT_DEFAULT_FLOW_VARIABLES_DICT.copy()

        # Get time dimension components
        if time_dimension:
            time_components = combination.get(time_dimension).split("-")
            time_components += [None] * (DEFAULT_NR_TIME_COMPONENTS - len(time_components))
            (
                flow_variables_dict["%Y"],
                flow_variables_dict["%M"],
                flow_variables_dict["%D"],
                flow_variables_dict["%H"],
            ) = time_components

        # Get discrete dimensions values
        for dimension in partiton_dimensions:
            if dimension not in flow_variables_dict.keys():
                flow_variables_dict[dimension] = combination.get(re.findall(DISCRETE_DIMENSION_PATTERN, dimension)[0])

        # Generate path
        src_file_path = file_path_pattern
        for dimension in partiton_dimensions:
            src_file_path = src_file_path.replace(dimension, flow_variables_dict[dimension])
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
