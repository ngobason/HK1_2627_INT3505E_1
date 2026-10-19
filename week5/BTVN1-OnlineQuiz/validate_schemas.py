from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import sys

try:
    from jsonschema import Draft202012Validator, FormatChecker
    from jsonschema.exceptions import SchemaError, ValidationError
except ImportError:
    print("Missing dependency: run  python -m pip install jsonschema", file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).resolve().parent
FILES = {
    "Quiz": ROOT / "schemas" / "quiz.schema.json",
    "Question": ROOT / "schemas" / "question.schema.json",
    "Attempt": ROOT / "schemas" / "attempt.schema.json",
}
DIALECT = "https://json-schema.org/draft/2020-12/schema"


def check_schema_resource(name: str, path: Path) -> None:
    with path.open(encoding="utf-8") as file:
        schema = json.load(file)

    if schema.get("$schema") != DIALECT:
        raise ValueError(f"$schema must be {DIALECT}")

    # (1) Check that the JSON Schema itself has valid structure and keywords.
    Draft202012Validator.check_schema(schema)

    # (2) Validate at least one actual instance using the schema.
    examples = schema.get("examples")
    if not isinstance(examples, list) or not examples:
        raise ValueError("Add at least one resource example to `examples`.")

    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    for index, value in enumerate(examples, 1):
        try:
            validator.validate(value)
        except ValidationError as exc:
            raise ValueError(f"example #{index} invalid: {exc.message}") from exc

    # (3) An intentionally invalid instance must be rejected.
    bad = deepcopy(examples[0])
    if name == "Quiz":
        bad["time_limit_minutes"] = 0
    elif name == "Question":
        bad["options"].pop("D")
    elif name == "Attempt":
        bad["status"] = "submitted"
        bad["score"] = None
    else:
        raise ValueError(f"Unknown schema: {name}")

    if validator.is_valid(bad):
        raise ValueError("negative test unexpectedly accepted an invalid value")

    print(f"[PASS] {name:<8} | valid schema | examples pass | invalid sample rejected")


def main() -> int:
    count = 0
    for name, path in FILES.items():
        try:
            check_schema_resource(name, path)
            count += 1
        except (OSError, ValueError, TypeError, json.JSONDecodeError, SchemaError, ValidationError) as exc:
            print(f"[FAIL] {name}: {exc}", file=sys.stderr)
    print(f"\nResult: {count}/{len(FILES)} schemas passed")
    return 0 if count == len(FILES) else 1


if __name__ == "__main__":
    sys.exit(main())
