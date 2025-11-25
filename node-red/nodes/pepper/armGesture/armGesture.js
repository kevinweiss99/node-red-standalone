module.exports = RED => {
    const socket = require("../connection").socket;
    const ConnectionHelper = require("../connectionHelper");
    const EventPubSub = require('node-red-contrib-base/eventPubSub');

    const events = new EventPubSub();

    function ActivateArmGesture(config) {
        RED.nodes.createNode(this, config);
        const node = this;

        // Bewegungspfad bestimmen
        if (config.movement === "FingerPoint") {
            node.path = "/robot/motion/arm/fingerpoint";
        } else {
            node.path = "/robot/motion/arm/thumbup";
        }

        let waitingNode = null;
        const ch = new ConnectionHelper(socket, node);

        node.on("input", msg => {
            waitingNode = msg;
            node.status({ fill: "blue", shape: "dot", text: node.type + ".moving" });
            // Hand-Parameter senden (RHand oder LHand)
            const hand = config.hand === "Left" ? "LHand" : "RHand";
            ch.emit(node.path, { hand: hand });
        });

        // Listener für FingerPoint oder ThumbUp
        if (config.movement === "FingerPoint") {
            ch.socket.on("/motion/arm/fingerpoint/finished", () => {
                if (!waitingNode) return;
                node.send(waitingNode);
                waitingNode = null;
                node.status({});
            });
        } else {
            ch.socket.on("/motion/arm/thumbup/finished", () => {
                if (!waitingNode) return;
                node.send(waitingNode);
                waitingNode = null;
                node.status({});
            });
        }

        // Reset bei Neustart
        events.subscribe(EventPubSub.RESET_NODE_STATE, () => {
            waitingNode = null;
            node.status({});
        });
    }

    RED.nodes.registerType("ArmGesture", ActivateArmGesture);
};
