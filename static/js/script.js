let mediaRecorder;
let chunks = [];

// Start camera with noise reduction
navigator.mediaDevices.getUserMedia({
    video: true,
    audio: {
        noiseSuppression: true,
        echoCancellation: true,
        autoGainControl: true
    }
})
.then(function(stream) {

    document.getElementById("preview").srcObject = stream;

    mediaRecorder = new MediaRecorder(stream);

    mediaRecorder.ondataavailable = function(e) {
        chunks.push(e.data);
    };

    mediaRecorder.onstop = function() {

        let blob = new Blob(chunks, { type: 'video/webm' });

        let formData = new FormData();
        formData.append("video", blob, "video.webm");

        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(() => {
            window.location.href = "/results";
        });

    };
});

// Start recording
function startRecording() {
    chunks = [];
    if (mediaRecorder) {
        mediaRecorder.start();
        console.log("Recording started");
    } else {
        alert("Camera not ready");
    }
}

// Stop recording
function stopRecording() {
    if (mediaRecorder) {
        mediaRecorder.stop();
        console.log("Recording stopped");
    }
}