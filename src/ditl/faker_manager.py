
from abc import abstractmethod
import random
from typing import Any, Callable, Set
from faker import Faker
import math

from ditl.utils import columnar_dictionary_to_records


class FakerManager:
    def __init__(self, faker: Faker | None = None) -> None:
        self.faker = Faker() if faker is None else faker
        self.primary_key_generation_registry: dict[str, Set] = {}
        self.non_key_generation_registry: dict[str, Set] = {}
        # TODO: Make sure, that primary key generates the most values!
        # TODO: Maybe provide a possibility to generate corrupt foreign key values

    def register_faker_type(self, faker_type: "FakerType") -> "FakerManager":
        if faker_type.generation_id is not None and faker_type.generation_id not in self.non_key_generation_registry:
            self.non_key_generation_registry[faker_type.generation_id] = []
        return self

    def generate(self, columns: dict[str, "FakerType"], n_values: int = 100) -> dict[str, list[Any]]:
        result = {}
        for column, faker_type in columns.items():
            if faker_type.generation_id is None:
                result[column] = [faker_type(faker_=self.faker)
                                  for _ in range(n_values)]
                continue

            if faker_type.generation_id not in self.non_key_generation_registry:
                self.non_key_generation_registry[faker_type.generation_id] = set(
                )
            current_set = self.non_key_generation_registry[faker_type.generation_id]
            while len(current_set) < n_values:
                current_set.add(faker_type(faker_=self.faker.unique))

            percentage = random.randint(
                faker_type.reuse_percentage_min*100 // 1, faker_type.reuse_percentage_max*100 // 1) / 100

            rand_func = random.choices if faker_type.allow_duplicate_values else random.sample
            result[column] = rand_func(
                population=list(current_set), k=math.ceil(n_values * percentage))
            result[column] += [faker_type(faker_=self.faker if faker_type.allow_duplicate_values else self.faker.unique)
                               for _ in range(math.floor(n_values * (1-percentage)))]
            random.shuffle(result[column])

            # for _ in n_values:
        return result


class FakerType:

    def __init__(self, generation_id: str | None = None, reuse_percentage_min: float = .3, reuse_percentage_max: float = .8, allow_duplicate_values: bool = False):
        self.generation_id = generation_id
        self.reuse_percentage_min = reuse_percentage_min if reuse_percentage_min <= 1 and reuse_percentage_min >= 0 else 0
        self.reuse_percentage_max = reuse_percentage_max if reuse_percentage_max <= 1 and reuse_percentage_max >= 0 else 1
        self.allow_duplicate_values = allow_duplicate_values
        if self.reuse_percentage_min > self.reuse_percentage_max:
            self.reuse_percentage_min = self.reuse_percentage_max

    def register_in_manager(self, manager: FakerManager) -> Any:
        manager.register_faker_type(self)

    @abstractmethod
    def __call__(self, *, faker_: Faker, **kwds: Any) -> Any:
        pass


class FakerTextType(FakerType):
    def __call__(self, *, faker_: Faker, **kwds: Any) -> Any:
        return faker_.text()


class FakerIDType(FakerType):
    def __call__(self, *, faker_: Faker, **kwds: Any) -> Any:
        return faker_.uuid4()


faker_manager = FakerManager()

column_faker_instance = FakerIDType(generation_id="a")
column_faker_instance_2 = FakerIDType(
    generation_id="a")
column_faker_instance_3 = FakerIDType(
    generation_id="a", allow_duplicate_values=False)

# print(faker_manager.generate(n_values=10,
#   columns={"test": column_faker_instance, "test2": column_faker_instance_2}))
print(faker_manager.generate(n_values=20,
      columns={"test3": column_faker_instance_3, "test2": column_faker_instance_2}, as_records=True))
