module.exports = RED => {
    const socket = require("../connection").socket;
    const ConnectionHelper = require("../connectionHelper");
    const EventPubSub = require('node-red-contrib-base/eventPubSub');
    const events = new EventPubSub();

    function ArmGesture(config) {
        RED.nodes.createNode(this, config);
        const node = this;
        const ch = new ConnectionHelper(socket, node);
        let waitingNode = null;

        node.on("input", msg => {
            waitingNode = msg;
            node.status({ fill: "blue", shape: "dot", text: `Performing ${config.movement} with ${config.hand} hand` });

            const path = `/robot/motion/arm_${config.hand.toLowerCase()}_${config.movement.toLowerCase()}`;
            ch.emit(path);

            ch.socket.once(`${path}/finished`, () => {
                if (waitingNode) {
                    node.send(waitingNode);
                    waitingNode = null;
                    node.status({});
                }
            });
        });

        events.subscribe(EventPubSub.RESET_NODE_STATE, () => {
            waitingNode = null;
            node.status({});
        });
    }

    RED.nodes.registerType("ArmGesture", ArmGesture);
};
