from pathlib import Path
import sys

try:
    import yaml
except ImportError:
    raise SystemExit("Cài dependency: python -m pip install pyyaml")

ROOT = Path(__file__).resolve().parent
spec = yaml.safe_load((ROOT / "openapi.yaml").read_text(encoding="utf-8"))


def check(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)
    print(f"[PASS] {message}")


def resolve(ref: str):
    assert ref.startswith("#/"), f"Chỉ hỗ trợ local $ref: {ref}"
    cur = spec
    for component in ref[2:].split("/"):
        cur = cur[component.replace("~1", "/").replace("~0", "~")]
    return cur


def walk(node):
    if isinstance(node, dict):
        if "$ref" in node:
            check(resolve(node["$ref"]) is not None, f"Resolved {node['$ref']}")
        for value in node.values():
            walk(value)
    elif isinstance(node, list):
        for value in node:
            walk(value)


expected = {
    ("/auth/login", "post"): ([], {"200", "400", "401", "429"}),
    ("/auth/refresh", "post"): ([], {"200", "401", "403", "429"}),
    ("/posts/{id}", "get"): (["posts:read"], {"200", "400", "401", "403", "404", "429"}),
}
check(spec.get("openapi") == "3.0.3", "OpenAPI version 3.0.3")
all_ops = {(p, m) for p, path in spec["paths"].items() for m in path if m in {"get", "post", "put", "patch", "delete"}}
check(all_ops == set(expected), "Chính xác 3 endpoint theo yêu cầu")
for (path, method), (scopes, statuses) in expected.items():
    operation = spec["paths"][path][method]
    check(operation.get("x-required-scopes") == scopes, f"{method.upper()} {path}: đúng scope")
    check(set(operation["responses"]) == statuses, f"{method.upper()} {path}: đủ HTTP status")
    check("security" in operation, f"{method.upper()} {path}: có khai báo security")
walk(spec)
check("SecurityAudit.md" in [p.name for p in ROOT.iterdir()], "Có SecurityAudit.md")
print("\nRESULT: OpenAPI exercise checks PASSED")
