import json
import sys

from websocket import create_connection
from websocket._exceptions import *


class WebSocketError:
    def __init__(self, status_code=408, error_message="WebSocketTimeoutException"):
        self.status_code = status_code
        self.reason = error_message


class MarianClient:
    def __init__(self, HOST="localhost", PORT="5000", timeout=2, debug=False):
        self.host = HOST
        self.port = PORT
        self.timeout = timeout
        self.debug = debug

    def _full_url(self):
        return f"ws://{self.host}:{self.port}/translate"

    def _send_message(self, tokenized_sentence: str):

        line = (
            tokenized_sentence.decode("utf-8")
            if sys.version_info < (3, 0)
            else tokenized_sentence
        )

        try:
            ws = create_connection(self._full_url(), timeout=2=self.timeout)
            ws.send(line)

        except:
            r = WebSocketError(101, "ConnectionFailed")
            success = False

            return success, r

        try:
            r = ws.recv().rstrip()
            success = True

        except WebSocketTimeoutException as e:
            """
            socket timeout during read/write data
            """
            r = WebSocketError(408, e)
            success = False

        except WebSocketPayloadException as e:
            """
            websocket payload is invalid
            """
            r = WebSocketError(407, e)
            success = False

        except WebSocketConnectionClosedException as e:
            """
            If remote host closed the connection 
            or some network error happened
            """
            r = WebSocketError(406, e)
            success = False

        except WebSocketAddressException as e:
            """
            websocket address info cannot be found
            """
            r = WebSocketError(405, e)
            success = False

        except Exception as e:
            r = WebSocketError(404, e)
            success = False

        finally:
            ws.close()

        return success, r

    def __call__(self, tokenized_sentence: str):

        success, r = self._send_message(tokenized_sentence)

        if self.debug:
            print(r.status_code, r.reason)

        if success:
            return success, r, (None, None)
        else:
            return success, None, (r.status_code, r.reason)
