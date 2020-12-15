# -*- coding: utf-8 -*-
"""Module with read/write utility functions which are *not* based on the Dataiku API"""

import re
from typing import List, AnyStr


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
