from pytradfri.command import Command
from pytradfri.api.libcoap_api import APIFactory
from pytradfri.error import RequestTimeout
from typing import Any, List
from time import sleep
from ..config import config

_api_factory = APIFactory(
    host=config.tradfri.host, psk_id=config.tradfri.identity, psk=config.tradfri.key
)
api = _api_factory.request


def try_several_times(
    command: Command, execute_response: bool = False, max_tries: int = 10
) -> List[Any]:
    """Try executing the command several times

    Args:
        command (Command): The command to execute
        execute_response (bool, optional): If we want to execute the response command as well. Defaults to False.
        max_tries (int, optional): Maximum number of tries. Defaults to 10.

    Returns:
        List[Any]: [description]
    """
    try_count = 1
    while True:
        try:
            response = api(command)
            if execute_response:
                response = api(response)

            if isinstance(response, list):
                return response
            else:
                return [response]
        except RequestTimeout:
            try_count += 1
            config.logger.info(
                f"try_several_times() Failed to run command, trying again... (try #{try_count})"
            )
            sleep(1)

            if try_count > max_tries:
                raise