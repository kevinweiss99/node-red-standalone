module.exports = function (RED) {
    const axios = require("axios");
    try { require("dotenv").config(); } catch (e) {}


    function OpenAIChatNode(config) {
        RED.nodes.createNode(this, config);
        const node = this;

        const apiKey = process.env.OPENAI_API_KEY;
        const defaultPrompt = config.systemPrompt || "";

        node.on("input", async function (msg, send, done) {
            if (!apiKey) {
                const err = new Error("OPENAI API KEY missing");
                node.status({ fill:"red", shape:"ring", text:"No API-Key (.env)" });
                node.error(err.message, msg);
                msg.payload = "Error: " + err.message;
                send(msg);
                return done && done(err);
            }

            node.status({ fill: "blue", shape: "dot", text: "Requesting OpenAI Chat..." });

            const axios = require("axios");
            const userMessage = typeof msg.payload === "string" ? msg.payload : "";

            const systemPrompt = msg.systemPrompt || defaultPrompt;
            let history = Array.isArray(msg.history) ? [...msg.history] : [];

            if (systemPrompt && !history.some(m => m.role === "system")) {
                history.unshift({ role: "system", content: systemPrompt });
            }

            history.push({ role: "user", content: userMessage });

            try {
                const response = await axios.post(
                    "https://api.openai.com/v1/chat/completions",
                    { model: "gpt-4o", messages: history },
                    { headers: { Authorization: `Bearer ${apiKey}`, "Content-Type": "application/json" } }
                );

                const reply = response.data.choices[0].message.content;
                history.push({ role: "assistant", content: reply });

                msg.payload = reply;
                msg.history = history;

                send(msg);
                done && done();
            } catch (err) {
                node.error("OpenAI API error: " + err.message, msg);
                msg.payload = "Error: " + err.message;
                send(msg);
                done && done(err);
            } finally {
                node.status({});
            }
        });
    }

    RED.nodes.registerType("OpenAIChat", OpenAIChatNode);
};
