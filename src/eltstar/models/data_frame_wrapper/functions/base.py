from typing import TypeVar

from pydantic import ConfigDict

from eltstar.base_model import BaseModel


class WrapperArgSpec(BaseModel):
    model_config = ConfigDict(extra="allow")


WrapperArgSpecType = TypeVar("WrapperArgSpecType", bound=WrapperArgSpec)  # pylint: disable=invalid-name


class WrapperFunctionSpec[WrapperArg: WrapperArgSpecType](BaseModel):
    func_name: str
    arg_spec: WrapperArg
