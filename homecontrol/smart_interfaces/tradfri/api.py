from time import sleep
from typing import Any, Callable, List, Union

from pytradfri.api.libcoap_api import APIFactory
from pytradfri.command import Command
from pytradfri.error import RequestTimeout

from ...config import config


class Api:
    _api_factory: APIFactory
    _api: Callable

    @staticmethod
    def init():
        Api._api_factory = APIFactory(
            host=config.tradfri.host,
            psk_id=config.tradfri.identity,
            psk=config.tradfri.key,
        )
        Api._api = Api._api_factory.request

    @staticmethod
    def execute(
        command: Command, execute_response: bool = False, max_tries: int = 10
    ) -> Union[Any, List[Any]]:
        """Try executing the command several times

        Args:
            command (Command): The command to execute
            execute_response (bool, optional): If we want to execute the response command as well. Defaults to False.
            max_tries (int, optional): Maximum number of tries. Defaults to 10.

        Returns:
            Union[Any, List[Any]]: [description]
        """
        try_count = 1
        while True:
            try:
                response = Api._api(command)
                if execute_response:
                    response = Api._api(response)

                if isinstance(response, list):
                    return response
                else:
                    return response
            except RequestTimeout:
                try_count += 1
                config.logger.info(
                    f"try_several_times() Failed to run command, trying again... (try #{try_count})"
                )
                sleep(1)

                if try_count > max_tries:
                    raise

    @staticmethod
    def seconds_to_tradfri(seconds: float) -> int:
        """Convert seconds to measured time in tradfri (100ms)

        Args:
            seconds (float): Number of seconds

        Returns:
            int: Time measured in tradfri
        """
        return int(seconds * 10)
