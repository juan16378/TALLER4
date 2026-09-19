/**
 * Captura de camara via getUserMedia y consumo de los endpoints de
 * reconocimiento facial expuestos por las vistas de Django, que a su vez
 * reenvian la imagen al backend FastAPI.
 */
(function () {
  "use strict";

  const video = document.getElementById("video");
  const canvas = document.getElementById("canvas");
  const btnRegister = document.getElementById("btn-register");
  const btnRecognize = document.getElementById("btn-recognize");
  const resultBox = document.getElementById("result");

  function getCsrfToken() {
    const input = document.querySelector('input[name="csrfmiddlewaretoken"]');
    return input ? input.value : "";
  }

  function showResult(text, isError) {
    resultBox.textContent = text;
    resultBox.style.color = isError ? "#b91c1c" : "#166534";
  }

  async function startCamera() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: 360, height: 270 },
        audio: false,
      });
      video.srcObject = stream;
    } catch (err) {
      showResult("No se pudo acceder a la camara: " + err.message, true);
    }
  }

  function captureFrameAsBase64() {
    const ctx = canvas.getContext("2d");
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    return canvas.toDataURL("image/jpeg", 0.9);
  }

  async function postImage(url, imageBase64) {
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCsrfToken(),
      },
      body: JSON.stringify({ image_base64: imageBase64 }),
    });
    const data = await response.json();
    return { status: response.status, data };
  }

  btnRegister.addEventListener("click", async () => {
    showResult("Registrando rostro...", false);
    const image = captureFrameAsBase64();
    try {
      const { status, data } = await postImage("/capture/api/register-face/", image);
      if (status === 200 && data.ok) {
        showResult(`${data.detail} (muestras: ${data.total_samples})`, false);
      } else {
        showResult(data.error || "No se pudo registrar el rostro.", true);
      }
    } catch (err) {
      showResult("Error de red: " + err.message, true);
    }
  });

  btnRecognize.addEventListener("click", async () => {
    showResult("Analizando rostro...", false);
    const image = captureFrameAsBase64();
    try {
      const { status, data } = await postImage("/capture/api/recognize-face/", image);
      if (status === 200 && data.ok) {
        showResult(data.message, !data.matched);
      } else {
        showResult(data.error || "No se pudo reconocer el rostro.", true);
      }
    } catch (err) {
      showResult("Error de red: " + err.message, true);
    }
  });

  startCamera();
})();
