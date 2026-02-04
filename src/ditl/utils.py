from typing import Any

from ditl.exceptions import ProgrammingError


def columnar_dictionary_to_records(values: dict[str, list[Any]]) -> list[dict[str, Any]]:
    lens = {k: len(v) for k, v in values.items()}
    first_len = lens[list(values.keys())[0]]
    if any(lens[k] != first_len for k in lens):
        raise ProgrammingError(
            "Can only convert columnar to records, if all columns have the same length!")
    return [{key: values[key][i] for key in values.keys()} for i in range(first_len)]
