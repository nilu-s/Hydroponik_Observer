from __future__ import annotations

import csv
import io
import zipfile
from typing import Iterable


def write_csv_to_zip_stream(
    zf: zipfile.ZipFile,
    name: str,
    rows: Iterable[dict],
    headers: list[str],
) -> None:
    with zf.open(name, "w") as handle:
        with io.TextIOWrapper(handle, encoding="utf-8", newline="") as output:
            writer = csv.DictWriter(output, fieldnames=headers)
            writer.writeheader()
            for row in rows:
                writer.writerow({key: row.get(key) for key in headers})
