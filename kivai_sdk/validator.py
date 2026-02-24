from __future__ import annotations

import json
import os
from typing import Any

from jsonschema import ValidationError, validate

try:
    # Python 3.9+
    from importlib import resources as importlib_resources
except Exception:  # pragma: no cover
    importlib_resources = None  # type: ignore


def _repo_root_schema_path() -> str:
    """
    Repo layout:
      - schema/kivai-intent-v1.schema.json      (canonical in-repo location)
      - kivai_sdk/validator.py                  (this file)

    From kivai_sdk/ -> go up 1 level to repo root, then /schema/...
    """
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    return os.path.join(repo_root, "schema", "kivai-intent-v1.schema.json")


def _package_schema_path() -> str | None:
    """
    Installed package layout:
      - kivai_sdk/schema/kivai-intent-v1.schema.json

    Returns a filesystem path when possible; otherwise None.
    """
    if importlib_resources is None:
        return None

    try:
        p = importlib_resources.files("kivai_sdk").joinpath(
            "schema/kivai-intent-v1.schema.json"
        )
        with importlib_resources.as_file(p) as local_path:
            return str(local_path)
    except Exception:
        return None


def _default_v1_schema_path() -> str:
    # Prefer packaged schema (pip install safe). Fallback to repo-root schema.
    return _package_schema_path() or _repo_root_schema_path()


def load_schema(schema_path: str | None = None) -> dict[str, Any]:
    if schema_path is None:
        schema_path = _default_v1_schema_path()

    with open(schema_path, "r", encoding="utf-8") as file:
        return json.load(file)


def validate_command(
    payload: dict[str, Any], schema_path: str | None = None
) -> tuple[bool, str]:
    """
    Validates a payload against the Kivai JSON Schema.

    Default: Kivai Intent v1.
      - Packaged install: kivai_sdk/schema/kivai-intent-v1.schema.json
      - Repo fallback: schema/kivai-intent-v1.schema.json

    Legacy schemas can still be validated by passing schema_path explicitly.
    """
    try:
        schema = load_schema(schema_path)
        validate(instance=payload, schema=schema)
        return True, "✅ Payload is valid!"
    except FileNotFoundError:
        return False, "❌ Validation failed: schema file not found"
    except ValidationError as e:
        return False, f"❌ Validation failed: {e.message}"
