# client.marian

A client for interacting with Marian-NMT websocket server (see [MarianNMT](https://marian-nmt.github.io/)).

## How it wokrs

Grammatical Error Correction consists of 4 repositories: `service.gec`, `library.gec`, `library.marian`, `'client.marian`:

- `service.gec` (QAI based REST service) imports `library.marian`
- `library.marian` calls `service.marian` via `client.marian`
- `service.marian` (C++ websocket server), fed with sentences, corrects them

In case tomorrow a better model is released...

- `service.gec` just instantize different `Grammar` object
- `library.marian` just changes calls/tokenization steps to call ...
- `service.marian` which is the main subject of change.

## Usage

```python
from marian_client import MarianClient

host = "0.0.0.0" 
port = "5000"

mc = MarianClient(PORT=port, HOST=host)

tokenized_sentence = "Alice like cats ."

success, corrected_sentence, error_info = mc(tokenized_sentence)

if success:
    print(corrected_sentence)
else:
    print(f"Call to MarianClient failed with error code {error_info[0]} and message {error_info[1]}")

```

## Installation

`pip install marian-client`

## License

Unlicensed.
