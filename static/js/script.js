let mediaRecorder;
let chunks = [];

navigator.mediaDevices.getUserMedia({ video: true, audio: true })
.then(stream => {
    document.getElementById("preview").srcObject = stream;

    mediaRecorder = new MediaRecorder(stream);

    mediaRecorder.ondataavailable = e => chunks.push(e.data);

    mediaRecorder.onstop = () => {
        let blob = new Blob(chunks, { type: 'video/webm' });

        let formData = new FormData();
        formData.append("video", blob, "video.webm");

        fetch('/upload', { method: 'POST', body: formData })
        .then(() => window.location.href = "/results");
    };
});

function startRecording() {
    chunks = [];
    mediaRecorder.start();
}

function stopRecording() {
    mediaRecorder.stop();
}