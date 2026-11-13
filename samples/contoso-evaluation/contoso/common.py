import hashlib
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT_SCHEMA = "contoso.offline-evaluation/1"


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def number(value):
    return type(value) in (int, float) and math.isfinite(value)


def assert_finite(value):
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("Non-finite numbers are not evidence")
    if isinstance(value, dict):
        for child in value.values():
            assert_finite(child)
    elif isinstance(value, list):
        for child in value:
            assert_finite(child)


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON key: " + key)
        result[key] = value
    return result


def _invalid_constant(value):
    raise ValueError("Invalid JSON numeric constant: " + value)


def parse_json(text):
    value = json.loads(
        text, object_pairs_hook=_unique_object, parse_constant=_invalid_constant
    )
    assert_finite(value)
    return value


def read_json(path):
    return parse_json(Path(path).read_text(encoding="utf-8"))


def write_json(path, value):
    assert_finite(value)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    partial = path.with_name(path.name + ".partial")
    partial.write_text(
        json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    partial.replace(path)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def implementation_digest():
    hasher = hashlib.sha256()
    paths = [ROOT / "run.py", ROOT / "gate.py"] + sorted((ROOT / "contoso").glob("*.py"))
    for path in paths:
        hasher.update(str(path.relative_to(ROOT)).encode("utf-8") + b"\0")
        hasher.update(path.read_bytes() + b"\0")
    return hasher.hexdigest()
