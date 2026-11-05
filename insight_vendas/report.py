"""Gera um único HTML portável com JSON escapado e script fixo autorizado por hash."""

import base64
import hashlib
import json
from pathlib import Path


def render_html(data: dict) -> str:
    template = Path(__file__).with_name("template.html").read_text(encoding="utf-8")
    script = template.split('<script id="app">', 1)[1].split("</script>", 1)[0]
    digest = base64.b64encode(hashlib.sha256(script.encode()).digest()).decode()
    encoded = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    for char, escaped in (("<", "\\u003c"), (">", "\\u003e"), ("&", "\\u0026"), ("\u2028", "\\u2028"), ("\u2029", "\\u2029")):
        encoded = encoded.replace(char, escaped)
    return template.replace("__SCRIPT_HASH__", digest).replace("__DATA_JSON__", encoded)
