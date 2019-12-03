"""
Python3 websocket client for MarianNMT server
"""

import json
import sys

from time import sleep

from websocket import create_connection
from websocket._exceptions import (
    WebSocketTimeoutException,
    WebSocketPayloadException,
    WebSocketConnectionClosedException,
    WebSocketAddressException,
)

GENERIC_WEBSOCKET_ERROR_CODE = 469


def exponential_backoff(tries_so_far):
    """
    don't just hammer the server, wait in between retries
    the more retries, the longer the wait
    """
    print(f"backing off, tries so far: {tries_so_far}")
    MAX_BACKOFF_WAIT = 16
    sleep(min(2 ** tries_so_far, MAX_BACKOFF_WAIT))


class WebSocketError:
    def __init__(self, status_code=408, error_message="WebSocketTimeoutException"):
        self.status_code = status_code
        self.reason = error_message


class MarianClient:
    def __init__(
        self, HOST="localhost", PORT="5000", timeout=2, debug=False, retries=2
    ):
        self.debug = debug
        self.timeout = timeout
        self.retries = retries
        self.url = f"ws://{HOST}:{PORT}/translate"
        self.ws = create_connection(self.url, timeout=self.timeout)
        self.reset_connection_count = 0

    def __del__(self):
        """ clean up after yourself """
        if self.ws and self.ws.connected:
            self.ws.close()

    def _ws_healthy(self):
        connected = self.ws.connected
        has_sock = bool(self.ws.sock)
        return connected and has_sock

    def _check_connection(self):
        if not self._ws_healthy():
            print("No longer connected to Marian Server...")
            self.ws.close()
            self.ws = create_connection(self.url, timeout=self.timeout)
            self.reset_connection_count += 1
            print(
                f"Reconnected to {self.url} for the {self.reset_connection_count} time"
            )

    def _retry_count(self, retries_remaining):
        """
        Converts from retries_remaining to 'how many retries so far'
        """
        return self.retries - retries_remaining

    def _send_message(self, tokenized_sentence: str):
        success = False
        retries_remaining = self.retries
        # make sure we are still connected to the host
        # will raise if we can't connect, and we don't want to catch
        # since there is no hope if we can't connect
        self._check_connection()

        while (success == False) and (retries_remaining >= 0):
            self.ws.send(tokenized_sentence)
            try:
                r = self.ws.recv().rstrip()
                success = True
            except (
                WebSocketTimeoutException,
                WebSocketPayloadException,
                WebSocketConnectionClosedException,
                WebSocketAddressException,
                ConnectionResetError,
                BrokenPipeError,
            ) as e:
                r = WebSocketError(GENERIC_WEBSOCKET_ERROR_CODE, e)
                exponential_backoff(self._retry_count(retries_remaining))
                retries_remaining -= 1
        if success == False and retries_remaining <= 0:
            # we assume that if the message failed `retries_remaining` times,
            # then the connection is bad
            self.ws.connected = False

        return success, r

    def __call__(self, tokenized_sentence: str):

        success, r = self._send_message(tokenized_sentence)

        if self.debug:
            print(r.status_code, r.reason)

        if success:
            return True, r, (None, None)
        else:
            return False, None, (r.status_code, r.reason)
