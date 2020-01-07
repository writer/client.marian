# Marian Client

A client for interacting with [Marian-NMT](https://github.com/marian-nmt/marian) websocket server (see [MarianNMT](https://marian-nmt.github.io/)).

Marian is a state of the art Neural Machine Translation framework written in C++. Eventually, someone should write Python bindings (not it!). Until then, the recommended way of communicating with Marian is via [WebSockets](https://websocket.org/aboutwebsocket.html). The authors of Marian provide an example of doing this [with this script](https://github.com/marian-nmt/marian-dev/blob/master/scripts/server/client_example.py). If you need Python2 support, you should look at that script.

What this project contributes beyond the above script:

* Persistent connection - This keeps a connection open between Marian Server and Python. This saves a few hundred ms per call, which is significant
* Encapsulation - just import a class, instantiate, and call. Don't think about websockets at all
* Timeout, retries, and error handling - websockets are not the most reliable. Connections fail, timeouts happen. Just pass a value for `timeout` and `retries` when you instantiate `MarianClient` and this will just be handled for you.

## Installation

```sh
pip install marian-client
```

## Usage

```python
from marian_client import MarianClient

# These are the default values:
host = "localhost"
port = "8080"

# or give the fully qualified URL
url = "ws://my.marian.server.ip/translate"

# Default values
timeout = 30  # measured in seconds - you may want to make this much lower
retries = 3  # amount of times to retry on error. backs off exponentially.

debug = False  # set to True for a little more info on errors

mc = MarianClient(PORT=port, HOST=host, timeout=timeout, retries=retries, debug=debug)
# or if you want to specify url
# mc = MarianClient(url, timeout=timeout, retries=retries, debug=debug)

# if you just want all the default values, and marian-server is running locally:
# mc = MarianClient()

tokenized_sentence = "Alice like cats ."

success, corrected_sentence, error_info = mc(tokenized_sentence)

if success:
    print(corrected_sentence)
else:
    print(f"Call to MarianClient failed with error code {error_info[0]} and message {error_info[1]}")

# If marian-server is sert up and working, this prints
# >>> "Alice likes cats ."
```

## Notes

* When instantiating a `MarianClient` instance, if we receive a `ConnectionRefusedError`, we attempt to reconnect `connection_retries` times, with exponential backoff, maxing out at `max_wait_time_between_connection_attempts`.
* This means in the default case, if Marian Server is unavailable, we will try to connect, wait 1 second, try to connect again, wait 2 seconds, try to connect again, wait 4 seconds, ... then 8, 16, 32, 64, 128, 256, 300, then actually fail, for a total wait time of 811 seconds.

## License

Like Marian, this package is released under the MIT license.

## Credits

This package was made by the NLP team at [Qordoba](https://qordoba.com/). If you are using it, and interested in working on NLP, maybe reach out to [Sam](mailto:sam.havens@qordoba.com?subject=NLP%20Team%20Application)?

Thanks to [Marcin Junczys-Dowmunt](https://github.com/emjotde) and the rest of the awesome authors of Marian!
