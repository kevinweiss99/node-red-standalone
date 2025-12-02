module.exports = RED => {
    const got = require("got");

    function ShowImageNode(config) {
        RED.nodes.createNode(this, config);
        const node = this;
        const endpoint = "http://172.30.36.198:5001/robot/presentation/show_slide";
        node.on("input", async msg => {
            try {
                const response = await got.post(endpoint, {
                    json: { url: config.url },
                    responseType: "json",
                    timeout: 5000
                });

                node.send({ payload: response.body });

                node.status({ fill: "green", shape: "dot", text: "OK" });

            } catch (err) {
                node.status({ fill: "red", shape: "ring", text: "POST failed" });
                node.error(err);

                node.send({ payload: null, error: err });
            }
        });
    }

    RED.nodes.registerType("Show Dual Presentation", ShowImageNode);
};
