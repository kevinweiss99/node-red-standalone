module.exports = RED => {
    const http = require("http");
    function CheckFingerUp(config) {
        RED.nodes.createNode(this, config);
        const node = this;
        node.url = "http://172.30.36.198:5001/robot/camera/finger_up";
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
