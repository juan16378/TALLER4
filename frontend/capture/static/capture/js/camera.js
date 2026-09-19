/**
 * Captura de camara via getUserMedia. La integracion con los endpoints de
 * reconocimiento facial se anade en un paso posterior.
 */
(function () {
  "use strict";

  const video = document.getElementById("video");
  const canvas = document.getElementById("canvas");
  const btnRegister = document.getElementById("btn-register");
  const btnRecognize = document.getElementById("btn-recognize");
  const resultBox = document.getElementById("result");

  async function startCamera() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: 360, height: 270 },
        audio: false,
      });
      video.srcObject = stream;
    } catch (err) {
      resultBox.textContent = "No se pudo acceder a la camara: " + err.message;
    }
  }

  function captureFrameAsBase64() {
    const ctx = canvas.getContext("2d");
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    return canvas.toDataURL("image/jpeg", 0.9);
  }

  btnRegister.addEventListener("click", () => {
    captureFrameAsBase64();
    resultBox.textContent = "Foto capturada (pendiente de enviar al backend).";
  });

  btnRecognize.addEventListener("click", () => {
    captureFrameAsBase64();
    resultBox.textContent = "Foto capturada (pendiente de enviar al backend).";
  });

  startCamera();
})();
