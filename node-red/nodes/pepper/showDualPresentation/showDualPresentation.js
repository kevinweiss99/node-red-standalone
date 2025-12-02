module.exports = RED => {
    const got = require("got");

    function ShowImageNode(config) {
        RED.nodes.createNode(this, config);
        const node = this;
        const endpoint = "http://172.30.36.198:5001/robot/presentation/show_slide";
        node.on("input", async msg => {
            got.post(endpoint, {
                json: { url: config.url }
            }).catch(err => {
                node.error(err);
            });
            node.send(msg);
        });
    }

    RED.nodes.registerType("Show Dual Presentation", ShowImageNode);
};
