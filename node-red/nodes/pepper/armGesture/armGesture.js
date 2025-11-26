module.exports = RED => {
    const http = require("http");

  function ArmGesture(config) {
        RED.nodes.createNode(this, config);
        const node = this;
        node.url = "http://172.30.36.198:5001/robot/motion/arm/fingerpoint";
        node.movement = config.movement;
        node.hand = config.hand;
        node.on("input", msg => {
            json_input = {"hand":node.hand}
            const data = JSON.stringify(json_input);
            const req = http.request({
                hostname: "172.30.36.198",
                port: "5001",
                path: `/robot/motion/arm/${node.movement}`,
                method: "POST",
                headers: {
                    'Content-Type': 'application/json',
                    'Content-Length': Buffer.byteLength(data)
                }
            }, res => {
                let body = "exception";
                res.on("data", chunk => body += chunk);
                res.on("end", () => {
                    try { msg.payload = data
                        } 
                    catch { msg.payload = body; }
                    node.send(msg);
                });
            });

            req.on("error", err => node.error("Request failed: " + err.message));
            req.write(data);
            req.end();
        });
    }

    RED.nodes.registerType("ArmGesture", ArmGesture);
}