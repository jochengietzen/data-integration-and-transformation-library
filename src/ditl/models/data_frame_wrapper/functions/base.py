from typing import TypeVar

from pydantic import ConfigDict

from ditl.base_model import BaseModel


class WrapperArgSpec(BaseModel):
    model_config = ConfigDict(extra="allow")


WrapperArgSpecType = TypeVar("WrapperArgSpecType", bound=WrapperArgSpec)


class WrapperFunction[WrapperArg: WrapperArgSpecType](BaseModel):
    func_name: str
    arg_spec: WrapperArg
