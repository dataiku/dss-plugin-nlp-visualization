# -*- coding: utf-8 -*-
"""Module with a class to export Wordclouds generated with the WordcloudGenerator class"""

import matplotlib
from io import BytesIO


matplotlib.use("agg")


class WordcloudExporter:
    """
    Class to export as png images wordclouds generated with the WordcloudGenerator class
    """

    DEFAULT_PAD_INCHES = 1
    DEFAULT_BBOX_INCHES = "tight"

    def __init__(self, pad_inches: int = DEFAULT_PAD_INCHES, bbox_inches: str = DEFAULT_BBOX_INCHES):
        self.pad_inches = pad_inches
        self.bbox_inches = bbox_inches

    def upload_to_folder(self, fig, output_folder, output_file_name):
        temp = BytesIO()
        fig.savefig(temp, bbox_inches=self.bbox_inches, pad_inches=self.pad_inches, dpi=fig.dpi)
        output_folder.upload_data(output_file_name, temp.getvalue())
