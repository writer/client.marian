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


class WebSocketError:
    def __init__(self, status_code=408, error_message="WebSocketTimeoutException"):
        self.status_code = status_code
        self.reason = error_message


class MarianClient:
    def __init__(
        self,
        HOST=None,
        PORT=None,
        url=None,
        timeout=None,
        retries=None,
        connection_retries=10,
        max_wait_time_between_connection_attempts=300,
        debug=False,
    ):
        self.debug = debug

        if retries is not None:
            # we use this as if it is 0-indexed
            # but humans will enter a value that is 1-indexed
            retries += 1

        if timeout is None and retries is None:
            timeout = 30
            retries = 3
        elif timeout is not None and retries is None:
            retries = max(int(timeout / 2) - 2, 2)
        elif retries is not None and timeout is None:
            timeout = 30
        print(f"setting timeout={timeout}sec, retries={retries}")
        self.timeout = timeout
        self.retries = retries

        if url:
            if HOST or PORT:
                print("If url is set, HOST and PORT are ignored")
            self.url = url
        else:
            if not HOST:
                HOST = "localhost"
            if not PORT:
                PORT = 8080
            self.url = f"ws://{HOST}:{PORT}/translate"

        self.reset_connection_count = 0
        CONNECTED_TO_MARIAN = False
        while (
            self.reset_connection_count < connection_retries and not CONNECTED_TO_MARIAN
        ):
            try:
                self.ws = create_connection(self.url, timeout=self.timeout)
                CONNECTED_TO_MARIAN = True
            except ConnectionRefusedError:
                print("Can't connect to Marian Server")
                print(
                    f"Will try to connect {connection_retries - self.reset_connection_count} more times, with exponentially increasing time between"
                )
                self.exponential_backoff(
                    self.reset_connection_count,
                    MAX_BACKOFF_WAIT=max_wait_time_between_connection_attempts,
                )
                self.reset_connection_count += 1
                print("trying to connect to Marian server again...")

        # if we can't connect after that long, actually fail
        if not hasattr(self, "ws"):
            raise ConnectionRefusedError("Can't connect to Marian Server")

    def __del__(self):
        """ clean up after yourself """
        if hasattr(self, "ws") and self.ws.connected:
            self.ws.close()

    def exponential_backoff(self, tries_so_far, MAX_BACKOFF_WAIT=None):
        """
        don't just hammer the server, wait in between retries
        the more retries, the longer the wait
        """
        print(f"backing off, tries so far: {tries_so_far}")
        if MAX_BACKOFF_WAIT is None:
            MAX_BACKOFF_WAIT = self.timeout + 4  # just in case add some buffer
        sleep(min(2 ** tries_so_far, MAX_BACKOFF_WAIT))

    def _ws_healthy(self):
        if not self.ws:
            return False
        connected = self.ws.connected
        has_sock = bool(self.ws.sock)
        return connected and has_sock

    def _reconnect(self):
        if self.ws:
            self.ws.close()
        # don't wrap create_connection in try/catch
        # we want to die if we can't connect
        self.ws = create_connection(self.url, timeout=self.timeout)
        self.reset_connection_count += 1
        print(
            f"Reconnected to {self.url}. Reconnection count: {self.reset_connection_count}"
        )

    def _check_connection(self):
        if not self._ws_healthy():
            print("No longer connected to Marian Server...")
            self._reconnect()

    def _retry_count(self, retries_remaining):
        """
        Converts from retries_remaining to 'how many retries so far'
        """
        return self.retries - retries_remaining

    def _send_message(self, tokenized_sentence: str):
        success = False
        r = None
        tries_remaining = self.retries
        # make sure we are still connected to the host
        # will raise if we can't connect, and we don't want to catch
        # since there is no hope if we can't connect
        self._check_connection()

        try:
            self.ws.send(tokenized_sentence)
        except (
            WebSocketConnectionClosedException,
            WebSocketAddressException,
            ConnectionResetError,
            BrokenPipeError,
        ) as e:
            print(e)
            self.ws.connected = False
            return False, WebSocketError(GENERIC_WEBSOCKET_ERROR_CODE, e)

        while (success == False) and (tries_remaining > 0):
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
                success = False
                r = WebSocketError(GENERIC_WEBSOCKET_ERROR_CODE, e)
                tries_remaining -= 1
                if tries_remaining > 0:
                    self.exponential_backoff(self._retry_count(tries_remaining))

        if success == False and tries_remaining <= 0:
            # we assume that if the message failed `tries_remaining` times,
            # then the connection is bad
            self.ws.connected = False

        assert r is not None, "If r isn't set by here, we didn't send a request"
        return success, r

    def __call__(self, tokenized_sentence: str):

        success, r = self._send_message(tokenized_sentence)

        if self.debug and r is not None:
            print(r.status_code, r.reason)

        if success:
            return True, r, (None, None)
        else:
            return False, None, (r.status_code, r.reason)
