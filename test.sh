#!/bin/sh
set -eu

TEST_SERVER_FILE="echo-server.js"

npm i ws
node tests/$TEST_SERVER_FILE &

python -m pytest

SERVER_PID=$(ps | grep $TEST_SERVER_FILE | grep node | awk '{print $1}')

echo "killing server process, pid=$SERVER_PID"
kill -9 "$SERVER_PID"
