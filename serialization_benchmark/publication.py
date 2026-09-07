from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import cast

import pyperf


_PRIVATE_ENVIRONMENT_FIELDS = frozenset({"hostname", "python_executable"})


class RawResultPublicationError(ValueError):
    """Raised when a raw pyperf result cannot be safely published."""


def sanitize_raw_result(path: Path) -> None:
    """Remove private host fields, validate, and atomically replace a pyperf result."""
    temporary_path: Path | None = None
    try:
        raw_data = cast(object, json.loads(path.read_text(encoding="utf-8")))
        sanitized = _without_private_environment_fields(raw_data)
        if not isinstance(sanitized, dict):
            raise RawResultPublicationError("pyperf result root must be a JSON object")

        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as temporary_file:
            json.dump(
                sanitized,
                temporary_file,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            )
            temporary_file.write("\n")
            temporary_path = Path(temporary_file.name)

        pyperf.BenchmarkSuite.load(str(temporary_path))
        temporary_path.replace(path)
    except RawResultPublicationError:
        raise
    except (
        AttributeError,
        json.JSONDecodeError,
        KeyError,
        OSError,
        TypeError,
        ValueError,
    ) as error:
        raise RawResultPublicationError(f"could not sanitize {path}: {error}") from error
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()


def _without_private_environment_fields(value: object) -> object:
    if isinstance(value, dict):
        mapping = cast(dict[str, object], value)
        return {
            key: _without_private_environment_fields(item)
            for key, item in mapping.items()
            if key not in _PRIVATE_ENVIRONMENT_FIELDS
        }
    if isinstance(value, list):
        return [_without_private_environment_fields(item) for item in value]
    return value
