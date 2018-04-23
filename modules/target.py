# coding=utf-8
# TODO: Add licence information
"""
Created on 27.3.2018
Updated on 16.4.2018
"""
from enum import Enum
from json import JSONEncoder

import datetime

__author__ = "Severi Jääskeläinen \n Samuel Kaiponen \n Heta Rekilä \n" \
             "Sinikka Siironen"
__versio__ = "2.0"

import json
import os

from modules.layer import Layer


class TargetEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Target):
            layers = []
            target_dict = {
                "name": obj.name,
                "distance": obj.distance,
                "layers": [],
                "type": obj.target_type.value,
                "image_size": obj.image_size,
                "image_file": obj.image_file,
                "scattering": obj.scattering
            }
            for l in obj.layers:
                layers.append(l)
            target_dict["layers"] = layers
            return target_dict
        return super(TargetEncoder, self).default(obj)


class TargetType(Enum):
    AFM = 0


class Target:
    """Target object describes the target.
    """

    __slots__ = "name", "date", "description", "target_type", "image_size",\
                "image_file", "scattering", "layers"

    def __init__(self, name="", date=datetime.date.today(), description="",
                 target_type=TargetType.AFM, image_size=(1024,1024),
                 image_file="", scattering=None, layers=[]):
        """Initialize a target.

        Args:
            name: Target name.
            date: Date of creation.
            description: Target description.
            target_type: Target type.
            image_size: Target image size.
            image_file: Target image file.
            scattering: Scattering element.
            layers: Target layers.

        """
        self.name = name
        self.date = date
        self.description = description
        self.target_type = target_type
        self.image_size = image_size
        self.image_file = image_file
        self.scattering = scattering
        self.layers = layers

    @classmethod
    def from_file(cls, file_path):
        """Initialize target from a JSON file.

        Args:
            file_path: A file path to JSON file containing the target
                       parameters.
        """

        obj = json.load(open(file_path))

        # Below we do conversion from dictionary to Target object
        name = os.path.splitext(os.path.split(file_path)[1])[0]
        angle = obj["angle"]
        layers = []

        for layer in obj["layers"]:
            layers.append(Layer(layer["elements"],
                                layer["thickness"],
                                layer["density"]))

        return cls(name, angle, layers)
