from typing import Any, Dict, Union
from ...config import config
import requests
import json


logger = config.logger


class Api:
    @staticmethod
    def put(path: str, body: Dict[str, Any]) -> None:
        jsonBody = json.dumps(body)
        logger.debug(f"jsonBody: {jsonBody}")
        response = requests.put(Api._url(path), json=body)
        if response.status_code != 200:
            logger.warning(f"response.status_code: {response.status_code}")
            logger.warning(f"response.json: {response.json()}")

    @staticmethod
    def get(path: str) -> Union[Dict[str, Any], None]:
        response = requests.get(Api._url(path))
        if response.ok:
            return response.json()

    @staticmethod
    def _url(path: str) -> str:
        url = f"http://{config.hue.host}/api/{config.hue.username}{path}"
        logger.debug(f"URL: {url}")
        return url
