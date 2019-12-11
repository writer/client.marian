/*
 * This NodeJS file starts a websocket echo server
 * You don't need to manually invoke this
 * Just run the tests by running client.marian/test.sh
 * It will start this server and run pytests
 *
 * If this doesn't work, and you are debugging, first make sure you have
 * nodejs version 10 or higher installed on your machine
 */

const WebSocket = require('ws');

const wss = new WebSocket.Server({ port: 8080 });

console.log("Echo websocket running at port 8080")

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

wss.on('connection', function connection(ws) {
    ws.on('message', async function incoming(message) {
        rando = Math.random()
        // wait for 0-11s, but more often closer to 0
        await sleep(11000 * rando * rando)
        console.log(message);
        ws.send(message);
    });

    console.log('new connection');
});

