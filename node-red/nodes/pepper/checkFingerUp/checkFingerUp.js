module.exports = RED => {
    const socket = require("../connection").socket;
    const ConnectionHelper = require("../connectionHelper");
    const EventPubSub = require('node-red-contrib-base/eventPubSub');
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

        node.path = "/robot/camera/finger_up";

        const ch = new ConnectionHelper(socket, node);

        ch.socket.on(node.path, data => {
            const msg = { payload: data };
            node.send(msg);
        });

        node.on("input", msg => {
            ch.emit(null, node.path);
        });

        events.subscribe(EventPubSub.RESET_NODE_STATE, () => {
            resetNodeState(ch);
        });
    }

    RED.nodes.registerType("CheckForFingerUp", CheckFingerUp);
}
