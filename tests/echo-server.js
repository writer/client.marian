const WebSocket = require('ws');

const wss = new WebSocket.Server({ port: 8080 });

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

