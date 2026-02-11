document.addEventListener("DOMContentLoaded", function () {

    console.log("JS loaded");

    /* ---------------- STATE ---------------- */

    let mediaRecorder = null;
    let audioChunks = [];

    let audioContext = new (window.AudioContext || window.webkitAudioContext)();
    let audioUnlocked = false;

    let audioPlayer = new Audio();
    let audioQueue = [];
    let isPlaying = false;

    const startBtn = document.getElementById("start-record");
    const stopBtn = document.getElementById("stop-record");
    const status = document.getElementById("recording-status");
    const feedback = document.getElementById("voice-feedback");
    const form = document.getElementById("add-product-form");

    /* ---------------- ADD PRODUCT FORM ---------------- */

    if (form) {
        form.addEventListener("submit", async function (e) {
            e.preventDefault();

            const title = document.getElementById("title").value;
            const model = document.getElementById("model").value;
            const price = parseFloat(document.getElementById("price").value);

            const response = await fetch("/api/products/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    title: title,
                    model: model || null,
                    price: price
                })
            });

            if (response.ok) {
                location.reload();
            } else {
                alert("Failed to add product");
            }
        });
    }

    /* ---------------- START RECORDING ---------------- */

    startBtn.addEventListener("click", async () => {

        console.log("Start clicked");

        // Unlock audio context once
        if (!audioUnlocked) {
            await audioContext.resume();
            audioUnlocked = true;
            console.log("Audio unlocked");
        }

        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];

            mediaRecorder.ondataavailable = event => {
                if (event.data.size > 0) {
                    audioChunks.push(event.data);
                }
            };

            mediaRecorder.onstop = async () => {
                console.log("Recording stopped");

                const audioBlob = new Blob(audioChunks, { type: "audio/webm" });

                const formData = new FormData();
                formData.append("file", audioBlob, "command.webm");

                const response = await fetch("/voice/upload", {
                    method: "POST",
                    body: formData
                });

                const data = await response.json();
                console.log("Voice response:", data);

                // Queue backend TTS
                if (data.speech_url) {
                    audioQueue.push(data.speech_url);
                    playNextAudio();
                }

                // UI feedback
                if (data.result && data.result.message) {
                    feedback.innerText = data.result.message;
                } else {
                    feedback.innerText = "Command processed.";
                }

                status.innerText = "Recording finished ✔️";
            };

            mediaRecorder.start();
            status.innerText = "Recording...";
            feedback.innerText = "";
            startBtn.disabled = true;
            stopBtn.disabled = false;

            console.log("Recording started");

        } catch (error) {
            console.error("Microphone error:", error);
        }
    });

    /* ---------------- STOP RECORDING ---------------- */

    stopBtn.addEventListener("click", () => {

        console.log("Stop clicked");

        if (mediaRecorder && mediaRecorder.state !== "inactive") {
            mediaRecorder.stop();
        }

        startBtn.disabled = false;
        stopBtn.disabled = true;
    });

    /* ---------------- AUDIO QUEUE SYSTEM ---------------- */

    function playNextAudio() {

        if (audioQueue.length === 0 || isPlaying) return;

        isPlaying = true;

        const url = audioQueue.shift();

        // Create NEW Audio each time (important fix)
        const player = new Audio(url);

        player.onended = () => {
            isPlaying = false;
            playNextAudio();
        };

        player.onerror = () => {
            console.warn("Audio error");
            isPlaying = false;
            playNextAudio();
        };

        player.play().catch(err => {
            console.warn("Playback blocked:", err);
            isPlaying = false;
        });
    }

});
