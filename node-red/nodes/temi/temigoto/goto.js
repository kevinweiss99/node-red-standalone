module.exports = function (RED) {
    const fs = require('fs');
    const fsp = require('fs').promises;
    const path = require('path');
    const EventEmitter = require('events');
    const { interruptHandling } = require("../interruptHelper");
    const mqtt = require("mqtt");

    const brokerConfig = {
        brokerurl: process.env.MQTT_BROKER_URL,
        username: process.env.MQTT_BROKER_USERNAME,
        password: process.env.MQTT_BROKER_PASSWORD
    };

    const gotoTopic = "temi/goto";
    const finishedTopic = "temi/goto/finished";
    const getLocationsTopic = "temi/get_locations";
    const locationsTopic = "temi/locations";

    const mqttClient = mqtt.connect(brokerConfig.brokerurl, {
        username: brokerConfig.username,
        password: brokerConfig.password
    });

    const locationsBus = new EventEmitter(); // emits 'updated' with { added, total }
    const filePath = () => path.join(RED.settings.userDir, "locations.json");
    let locationsCache = [];                 // latest in-memory view
    let mqttHandlerInstalled = false;        // install locations handler once
    let startupRefreshRequested = false;     // one refresh per runtime
    let writing = false;                     // simple write lock

    // Helpers functions
    async function loadExistingFile() {
        try {
            const data = await fsp.readFile(filePath(), "utf8");
            const arr = JSON.parse(data);
            return Array.isArray(arr) ? arr : [];
        } catch (_e) {
            return [];
        }
    }

    function makeKey(o, keyProp) {
        if (o && typeof o === "object") {
            if (o[keyProp] != null) return String(o[keyProp]);
            if (o.name != null) return String(o.name);
        }
        return JSON.stringify(o); // fallback
    }

    // async function mergeAndPersist(incoming, keyProp = "id") {
    //     if (!Array.isArray(incoming)) 
    //         return { added: 0, total: locationsCache.length };

    //     // Prime cache from disk on first use if empty
    //     if (locationsCache.length === 0) {
    //         locationsCache = await loadExistingFile();
    //     }

    //     const seen = new Set(locationsCache.map(l => makeKey(l, keyProp)));
    //     const additions = [];
    //     for (const item of incoming) {
    //         const k = makeKey(item, keyProp);
    //         if (!seen.has(k)) {
    //             seen.add(k);
    //             additions.push(item);
    //         }
    //     }
    //     if (additions.length === 0) {
    //         return { added: 0, total: locationsCache.length };
    //     }

    //     const merged = locationsCache.concat(additions);
    //     // Serialize writes to avoid interleaving
    //     while (writing) {
    //         await new Promise(r => setTimeout(r, 25));
    //     }
    //     writing = true;
    //     try {
    //         await fsp.writeFile(filePath(), JSON.stringify(merged, null, 2), "utf8");
    //         locationsCache = merged;
    //         return { added: additions.length, total: merged.length };
    //     } finally {
    //         writing = false;
    //     }
    // }
    async function replaceAndPersist(incoming) {
        if (!Array.isArray(incoming)) {
            return { replaced: false, total: locationsCache.length };
        }

        // Optional: enforce uniqueness inside the incoming list (by id/name) if needed.
        // For pure replacement without dedupe, just assign directly:
        const newList = incoming;

        // Serialize writes to avoid interleaving
        while (writing) {
            await new Promise(r => setTimeout(r, 25));
        }
        writing = true;
        try {
            await fsp.writeFile(filePath(), JSON.stringify(newList, null, 2), "utf8");
            locationsCache = newList;
            return { replaced: true, total: newList.length };
        } finally {
            writing = false;
        }
    }


    function requestLocationsUpdate(reason) {
        const note = reason ? ` (${reason})` : "";
        mqttClient.publish(getLocationsTopic, "update", err => {
            if (err) {
                RED.log.error("Error requesting locations update" + note + ": " + err.toString());
            } else {
                RED.log.info("Requested locations update" + note);
            }
        });
    }

    // Install a single MQTT handler for locations that all nodes share
    function ensureLocationsHandler(keyProp = "id") {
    if (mqttHandlerInstalled) return;
    mqttClient.subscribe(locationsTopic);
    mqttClient.on("message", async (topic, message) => {
        if (topic !== locationsTopic) return;
        try {
            const payload = JSON.parse(message.toString());
            const { replaced, total } = await replaceAndPersist(payload);
            if (replaced) {
                locationsBus.emit("updated", { added: 'replaced', total });
                RED.log.info(`Locations replaced: total=${total}`);
            } else {
                RED.log.debug("Locations payload not an array; no replacement performed");
            }
        } catch (e) {
            RED.log.warn("Failed to process locations payload: " + e.toString());
        }
    });
    mqttHandlerInstalled = true;
}


    // Wait for an update or timeout (used by HTTP admin)
    function waitForUpdate(ms = 800) {
        return new Promise(resolve => {
            let t = setTimeout(() => {
                cleanup();
                resolve(false);
            }, ms);
            function handler() {
                clearTimeout(t);
                cleanup();
                resolve(true);
            }
            function cleanup() {
                locationsBus.off("updated", handler);
            }
            locationsBus.on("updated", handler);
        });
    }

    function goto(config) {
        RED.nodes.createNode(this, config);
        const node = this;
        const { waitIfInterrupted, cleanup } = interruptHandling(node, mqttClient);

        const flow = node.context().flow;
        const global = node.context().global;

        const nodeFinishedTopic = `${finishedTopic}/${node.id}`;
        let currentDoneCallback = null;
        let shouldSendNextMessage = true;
        let firstUseRefreshRequested = false;

        // Ensure shared handler is active
        ensureLocationsHandler(config && config.keyProp || "id");

        // One refresh per runtime
        if (!startupRefreshRequested) {
            requestLocationsUpdate("startup");
            startupRefreshRequested = true;
        }

        // Subscribe only to this node's finished topic
        mqttClient.subscribe(nodeFinishedTopic);

        // Handle goto finished signal
        mqttClient.on('message', function (topic, message) {
            if (topic !== nodeFinishedTopic) return;
            const receivedMessage = message.toString();
            if (receivedMessage.trim().toLowerCase() !== "done") return;

            node.warn(`Node ${node.id} received done message - currentDoneCallback exists: ${!!currentDoneCallback}`);

            const cancelSignalActive = global.get("cancel_flow_signal") === true;
            if (cancelSignalActive) {
                node.warn("MQTT done received but flow is cancelled - not sending to next node");
                if (currentDoneCallback) {
                    currentDoneCallback();
                    currentDoneCallback = null;
                }
                return;
            }

            if (shouldSendNextMessage) {
                if (flow.get("interruption_requested") && !global.get("interruption_feedback")) {
                    global.set("interruption_feedback", true);
                    node.warn("Interruption feedback is sent");
                    flow.set("interruption_requested", false);
                }
                node.send({ payload: "Next node triggered", topic: gotoTopic });
                node.status({});
            } else {
                node.status({ fill: "red", shape: "ring", text: node.type + ".cancelled" });
            }

            if (currentDoneCallback) {
                currentDoneCallback();
                currentDoneCallback = null;
            }
        });

        // Node input
        this.on('input', async function (msg, send, done) {
            node.log("Goto node was triggered");
            node.status({ fill: "blue", shape: "dot", text: node.type + ".driving" });

            currentDoneCallback = done;
            shouldSendNextMessage = true;

            // Proactively refresh locations once per node on first use
            if (!firstUseRefreshRequested) {
                requestLocationsUpdate(`first-use:${node.id}`);
                firstUseRefreshRequested = true;
            }

            // Optional: small wait to allow quick refreshes to land
            // await waitForUpdate(300); // uncomment if you want to wait briefly

            // Cancel check
            const cancelSignalActive = global.get("cancel_flow_signal") === true;
            if (cancelSignalActive) {
                node.warn("Flow explicitly cancelled by global signal.");
                node.status({ fill: "red", shape: "cross", text: node.type + ".cancelled" });
                shouldSendNextMessage = false;
                if (currentDoneCallback) {
                    currentDoneCallback();
                    currentDoneCallback = null;
                }
                return;
            }

            // Interruption handling
            const wasInterrupted = await waitIfInterrupted();
            if (!wasInterrupted) {
                node.log("Flow is active.");
            }

            // Cancel check again after wait
            const cancelSignalAfterWait = global.get("cancel_flow_signal") === true;
            if (cancelSignalAfterWait) {
                node.warn("Flow explicitly cancelled by global signal after interruption check.");
                node.status({ fill: "red", shape: "cross", text: node.type + ".cancelled" });
                shouldSendNextMessage = false;
                if (currentDoneCallback) {
                    currentDoneCallback();
                    currentDoneCallback = null;
                }
                return;
            }

            // Send goto command
            const messageText = config.location || "No checkpoint specified";
            const messageObject = { text: messageText, id: node.id };
            const messageJSON = JSON.stringify(messageObject);

            mqttClient.publish(gotoTopic, messageJSON, function (err) {
                if (err) {
                    node.error("Error sending message: " + err.toString());
                    if (currentDoneCallback) {
                        currentDoneCallback(err);
                        currentDoneCallback = null;
                    }
                } else {
                    node.log("Message successfully sent: " + messageJSON);
                }
            });
        });

        // Cleanup
        this.on('close', function (done) {
            mqttClient.unsubscribe(nodeFinishedTopic);
            cleanup();
            currentDoneCallback = null;
            done();
        });
    }

    RED.nodes.registerType("temigoto", goto);

    // Admin endpoint to serve latest locations with optional fast refresh
    RED.httpAdmin.get("/temigoto/locations", RED.auth.needsPermission('temigoto.read'), async function (req, res) {
        try {
            // Trigger a refresh in the background
            requestLocationsUpdate("http-admin");

            // If we already have cache, return it immediately
            if (locationsCache.length > 0) {
                return res.json(locationsCache);
            }

            // Otherwise load from disk; optionally wait briefly for a fresh update
            const disk = await loadExistingFile();
            if (disk.length > 0) {
                locationsCache = disk;
                return res.json(disk);
            }

            // Wait a short time for an incoming update, then return whatever we have
            const gotUpdate = await waitForUpdate(600);
            if (gotUpdate && locationsCache.length > 0) {
                return res.json(locationsCache);
            }
            return res.json([]); // empty as last resort
        } catch (e) {
            RED.log.error(`Error serving locations: ${e.message}.`);
            res.status(500).send("Error retrieving locations.");
        }
    });
};
