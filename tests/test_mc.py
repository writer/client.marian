"""
This test shouldn't be run directly with pytest
(unless you really get what's going on)

It is meant to be run by invoking client.marian/test.sh
that shell script spins up a websocket echo server with artificial latency
which this script talks to
"""

import pytest
from essential_generators import DocumentGenerator

from marian_client import MarianClient as MC


TESTS_TO_RUN = 20

gen = DocumentGenerator()

sentences = [gen.sentence() for _ in range(TESTS_TO_RUN)]

try:
    # intentionally cause timeouts and retries
    mc = MC(PORT=8080, timeout=1, retries=5)
except Exception as e:
    raise Exception(
        "you need a specifc WS running on localhost:8080 to run theses tests "
        "- you also need node.js, a version that supports await syntax"
    )


@pytest.mark.parametrize("sent", sentences)
def test_echo_consistency(sent):
    global mc
    succ, echoed, _ = mc(sent)
    assert sent == echoed, "Messages sent to echo server should come back the same"
