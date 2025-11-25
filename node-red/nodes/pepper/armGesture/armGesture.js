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
            node.status({ fill: "blue", shape: "dot", text: `Performing ${config.movement} with ${config.hand}` });

            // Neuer, korrekter Pfad (passend zum Python-Server)
            const path = `/robot/motion/arm/${config.movement.toLowerCase()}`;

            // Hand-Parameter wird mitgesendet
            ch.emit(path, { hand: config.hand === "Left" ? "LHand" : "RHand" });

            // Auf Abschluss warten
            ch.socket.once(`/motion/arm/${config.movement.toLowerCase()}/finished`, () => {
                if (waitingNode) {
                    node.send(waitingNode);
                    waitingNode = null;
                    node.status({});
                }
            });
        });

        // Reset falls Node neu initialisiert wird
        events.subscribe(EventPubSub.RESET_NODE_STATE, () => {
            waitingNode = null;
            node.status({});
        });
    }

    RED.nodes.registerType("ArmGesture", ArmGesture);
};
