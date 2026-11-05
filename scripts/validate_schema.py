#!/usr/bin/env python3
"""
Validate debts.json against expected schema before dispatch.

Schema (JSON Schema):
{
  "type": "array",
  "items": {
    "type": "object",
    "properties": {
      "account_id": {"type": "string"},
      "document_id": {"type": "string"},
      "violation_type": {"type": "string"},
      "action_deadline": {"type": "string", "format": "date-time"},
      "status": {"type": "string"},
      "notes": {"type": "string"}
    },
    "required": ["account_id", "document_id", "violation_type", "action_deadline", "status"]
  }
}
"""

import json
import sys
from jsonschema import validate, ValidationError
from pathlib import Path

def load_schema() -> dict:
    """Hard-code schema inline for simplicity."""
    return {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "account_id": {"type": "string"},
                "document_id": {"type": "string"},
                "violation_type": {"type": "string"},
                "action_deadline": {"type": "string", "format": "date-time"},
                "status": {"type": "string"},
                "notes": {"type": "string"},
            },
            "required": [
                "account_id",
                "document_id",
                "violation_type",
                "action_deadline",
                "status",
            ],
        },
    }

def load_data(path: str = "data/debts.json") -> list:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def validate(data: list) -> bool:
    try:
        validate(data, load_schema())
        return True
    except ValidationError as e:
        print(f"Schema validation FAILED: {e.message}", file=sys.stderr)
        return False

def main() -> int:
    data = load_data()
    ok = validate(data)
    return 1 if not ok else 0

if __name__ == "__main__":
    sys.exit(main())
