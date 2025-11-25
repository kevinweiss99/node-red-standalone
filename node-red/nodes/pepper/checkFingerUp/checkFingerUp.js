module.exports = RED => {
    const socket = require("../connection").socket;
    const ConnectionHelper = require("../connectionHelper");
    const EventPubSub = require('node-red-contrib-base/eventPubSub');
    const http = require("http");
    let lastReset = 0;

    const events = new EventPubSub();

    function resetNodeState(ch) {
        if (lastReset + 100 > Date.now()) {
            return;
        }

        lastReset = Date.now();
        ch.emit(null, "/robot/camera/finger_up");
    }

    function CheckFingerUp(config) {
        RED.nodes.createNode(this, config);
        const node = this;
        node.url = "http://172.30.36.198:5001/robot/camera/finger_up"; // adjust URL

        node.on("input", msg => {
            http.get(node.url, res => {
                let data = "";
                res.on("data", chunk => data += chunk);
                res.on("end", () => {
                    try {
                        msg.payload = JSON.parse(data);
                        node.send(msg);
                    } catch (err) {
                        node.error("Invalid JSON: " + err.message);
                    }
                });
            }).on("error", err => {
                node.error("Failed to fetch /robot/camera/finger_up: " + err.message);
            });
        });
    }

    RED.nodes.registerType("CheckForFingerUp", CheckFingerUp);
}
