const socket = io({
    extraHeaders: {
        "serviceName": "Debug-Website"
    },
    reconnectionDelay: 5000
});

const attributes = [
    "connection_type",
    "BatteryChargeChanged",
    "temperature",
    "tts_volume",
    "esp_connection",
    "camera_status"
];

attributes.forEach(attribute => {
    socket.on("/update/" + attribute, args => {
        document.getElementById(attribute).innerHTML = args;
    });
})

socket.on("/update/camera", args => {
    const arrayBufferView = new Uint8Array(args.img_bytearray);
    const blob = new Blob([arrayBufferView], { type: "image/png" });
    const urlCreator = window.URL || window.webkitURL;
    const imageUrl = urlCreator.createObjectURL(blob);
    const imageId = document.getElementById("current_img");
    imageId.src = imageUrl;
})

const volumeSlider = document.getElementById("volumeSlider");
socket.on("/robot/output/volume", args => {
    volumeSlider.value = args;
});

socket.on("/update/connection_type", args => {
    if (args != "Disconnected") {
        return;
    }

    if (document.getElementById("easter_eggs").value != "True") {
        return;
    }

    // definitely not a rick roll
    window.open("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
});

volumeSlider.onchange = () => {
    socket.emit("/robot/output/volume", volumeSlider.value)
}

function stopServices() {
    socket.emit("/robot/face/stop");
    socket.emit("/robot/qr/stop");
    socket.emit("/robot/speech-recognition/stop");
}

const textInput = document.getElementById("textInput");
textInput.addEventListener("keypress", function (event) {
    if (event.key === "Enter") {
        sayText();
    }
});

function sayText() {
    socket.emit("/robot/tts/say", [textInput.value, "German", false]);
    textInput.value = "";
}
