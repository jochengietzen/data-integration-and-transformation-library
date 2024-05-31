from os import PathLike

import yaml
from pydantic import BaseModel as _BaseModel


class BaseModel(_BaseModel):

    @classmethod
    def from_yaml(cls, path: PathLike, encoding: str = "utf-8"):
        """
        Allows you to instantiate a model from a yaml file
        :param path: Path of the yaml file
        :param encoding: Encoding of the file
        returns: Model
        """
        with open(path, "r", encoding=encoding) as f:
            return cls(**yaml.full_load(f))
