from .executor import Executor
import logging
import json
import socket


logger = logging.getLogger(__name__)


class SocketServer:
    @staticmethod
    def run():
        logger.debug("SocketServer.run() Starting server")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind(("localhost", 10200))
            sock.listen(10)
            while True:
                try:
                    conn, address = sock.accept()
                    with conn:
                        logger.debug("SocketServer.run() Connected by " + str(address))
                        json_string = conn.recv(4096)
                        data = json.loads(json_string)
                        logger.debug("SocketServer.run() Json: " + str(data))
                        executor = Executor(data)
                        return_val = executor.execute()

                        # Send the return value if one exists
                        if return_val:
                            conn.sendall(json.dumps(return_val).encode())

                except (Exception, RuntimeError) as e:
                    logger.exception(
                        "SocketServer.run() Error parsing json or running command "
                        + repr(e)
                    )
