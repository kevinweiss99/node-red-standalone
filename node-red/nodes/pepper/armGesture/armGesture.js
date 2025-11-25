module.exports = RED => {
    const http = require("http");

  function ArmGesture(config) {
        RED.nodes.createNode(this, config);
        const node = this;
        node.url = "http://172.30.36.198:5001/robot/motion/arm/fingerpoint";

        node.on("input", msg => {
            const data = JSON.stringify(msg.payload);
            const url = new URL(node.url);

            const req = http.request({
                hostname: url.hostname,
                port: url.port,
                path: url.pathname,
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Content-Length": Buffer.byteLength(data)
                }
            }, res => {
                let body = "";
                res.on("data", chunk => body += chunk);
                res.on("end", () => {
                    try { msg.payload = JSON.parse(body); } 
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