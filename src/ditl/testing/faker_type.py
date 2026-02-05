from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ditl.testing.faker_manager import FakerManager

from faker import Faker


from abc import abstractmethod
from typing import Any


class FakerType:
    def __init__(
        self,
        generation_id: str | None = None,
        reuse_percentage_min: float = 0.3,
        reuse_percentage_max: float = 0.8,
        allow_duplicate_values: bool = False,
    ):
        self.generation_id = generation_id
        self.reuse_percentage_min = (
            reuse_percentage_min
            if reuse_percentage_min <= 1 and reuse_percentage_min >= 0
            else 0
        )
        self.reuse_percentage_max = (
            reuse_percentage_max
            if reuse_percentage_max <= 1 and reuse_percentage_max >= 0
            else 1
        )
        self.allow_duplicate_values = allow_duplicate_values
        if self.reuse_percentage_min > self.reuse_percentage_max:
            self.reuse_percentage_min = self.reuse_percentage_max

    def register_in_manager(self, manager: "FakerManager") -> Any:
        manager.register_faker_type(self)

    @abstractmethod
    def __call__(self, *, faker_: Faker, **kwds: Any) -> Any:
        pass


class FakerTextType(FakerType):
    def __call__(self, *, faker_: Faker, **kwds: Any) -> Any:
        return faker_.text()


class FakerStringType(FakerType):
    def __call__(self, *, faker_: Faker, **kwds: Any) -> Any:
        return faker_.word()


class FakerIntType(FakerType):
    def __init__(
        self,
        min_val: int,
        max_val: int,
        generation_id: str | None = None,
        reuse_percentage_min: float = 0.3,
        reuse_percentage_max: float = 0.8,
        allow_duplicate_values: bool = False,
    ):
        super().__init__(
            generation_id,
            reuse_percentage_min,
            reuse_percentage_max,
            allow_duplicate_values,
        )
        self.min_val = min_val
        self.max_val = max_val

    def __call__(self, *, faker_: Faker, **kwds: Any) -> Any:
        return faker_.random_int(min=self.min_val, max=self.max_val)


class FakerIDType(FakerType):
    def __call__(self, *, faker_: Faker, **kwds: Any) -> Any:
        return faker_.uuid4()
