import json
from json import JSONDecodeError
from typing import Any

import pytest
from _pytest.capture import CaptureFixture


def read_json_logs(capfd: CaptureFixture[str]) -> list[dict[Any, Any]]:
    """
    Хелпер для чтения из stdout. Используется в случае записи логов в формате JSON.
    """
    out, err = capfd.readouterr()
    assert err == "", f"stderror output:\n{err}"

    records = out.strip().split("\n")
    try:
        return [json.loads(record) for record in records]
    except JSONDecodeError as error:
        pytest.fail(
            "Invalid json log format. Change log format or read as plaint text.\n"
            f"log record: `{error.doc}`"
        )
