import json
import os
from jsonschema import validate, ValidationError


def _default_v1_schema_path() -> str:
    """
    Resolve the canonical v1 schema path from inside the package.

    Repo layout:
      - schema/kivai-intent-v1.schema.json      (canonical)
      - kivai_sdk/validator.py                  (this file)

    From kivai_sdk/ -> go up 1 level to repo root, then /schema/...
    """
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    return os.path.join(repo_root, "schema", "kivai-intent-v1.schema.json")


def load_schema(schema_path: str | None = None) -> dict:
    if schema_path is None:
        schema_path = _default_v1_schema_path()

    with open(schema_path, "r", encoding="utf-8") as file:
        return json.load(file)


def validate_command(payload: dict, schema_path: str | None = None) -> tuple[bool, str]:
    """
    Validates a payload against the Kivai JSON Schema.

    Default: Kivai Intent v1 (schema/kivai-intent-v1.schema.json)

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
