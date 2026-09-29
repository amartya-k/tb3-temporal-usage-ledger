"""Export text evidence with subscription credentials redacted before upload."""
import json
import os
from pathlib import Path

root = Path("evaluation")
destination = Path("evidence")
destination.mkdir(exist_ok=True)
secrets = [os.environ.get("CLAUDE_CODE_OAUTH_TOKEN", ""), os.environ.get("CODEX_AUTH_JSON", "")]
try:
    auth = json.loads(os.environ.get("CODEX_AUTH_JSON") or "{}")
except json.JSONDecodeError:
    auth = {}


def strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from strings(item)


secrets.extend(strings(auth))
secrets = sorted({value for value in secrets if len(value) > 12}, key=len, reverse=True)
manifest = {"redacted_files": [], "omitted_files": []}
for path in sorted(root.rglob("*")):
    if not path.is_file() or path.is_symlink():
        continue
    relative = str(path.relative_to(root))
    if path.stat().st_size > 64 * 1024 * 1024:
        manifest["omitted_files"].append(relative)
        continue
    try:
        contents = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        manifest["omitted_files"].append(relative)
        continue
    clean = contents
    for secret in secrets:
        clean = clean.replace(secret, "[REDACTED_CREDENTIAL]")
    if clean != contents:
        manifest["redacted_files"].append(relative)
    target = destination / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(clean)
(destination / "evidence-manifest.json").write_text(json.dumps(manifest, indent=2))
