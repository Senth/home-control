from typing import Any, Dict, Optional

from flask import abort, request


def get_json() -> Dict[str, Any]:
    body: Optional[Dict[str, Any]] = request.get_json(force=True)
    if not body:
        abort(400, "Not a json object")
    return body
