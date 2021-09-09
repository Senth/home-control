import json
from typing import Any, Dict, Union

import requests
from tealprint import TealPrint

from ...config import config


class Api:
    @staticmethod
    def put(path: str, body: Dict[str, Any]) -> None:
        jsonBody = json.dumps(body)
        TealPrint.debug(f"jsonBody: {jsonBody}")
        response = requests.put(Api._url(path), json=body)
        if response.status_code != 200:
            TealPrint.warning(f"response.status_code: {response.status_code}")
            TealPrint.warning(f"response.json: {response.json()}")

    @staticmethod
    def get(path: str) -> Union[Dict[str, Any], None]:
        response = requests.get(Api._url(path))
        if response.ok:
            return response.json()

    @staticmethod
    def _url(path: str) -> str:
        url = f"http://{config.hue.host}/api/{config.hue.username}{path}"
        TealPrint.debug(f"URL: {url}")
        return url
