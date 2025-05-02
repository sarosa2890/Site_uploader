
document.getElementById("uploadForm").addEventListener("submit", function(e) {
  e.preventDefault();
  const form = e.target;
  const fileInput = form.querySelector('input[type="file"]');
  const file = fileInput.files[0];

  if (!file) return alert("Please select a file.");

  const formData = new FormData();
  formData.append("file", file);

  const xhr = new XMLHttpRequest();
  xhr.open("POST", "/upload");

  xhr.upload.addEventListener("progress", function(e) {
    const percent = Math.round((e.loaded / e.total) * 100);
    document.getElementById("progressContainer").classList.remove("hidden");
    document.getElementById("progressBar").value = percent;
    document.getElementById("progressPercent").textContent = percent + "%";
  });

  xhr.onload = function() {
    if (xhr.status === 200) {
      const res = JSON.parse(xhr.responseText);
      const link = location.origin + res.url;
      document.getElementById("downloadLink").href = link;
      document.getElementById("downloadLink").textContent = link;
      document.getElementById("result").classList.remove("hidden");

      const qr = new QRious({
        element: document.getElementById("qrcode"),
        value: link,
        size: 150
      });
    } else {
      alert("Upload failed.");
    }
  };

  xhr.send(formData);
});

function copyLink() {
  const link = document.getElementById("downloadLink").href;
  navigator.clipboard.writeText(link).then(() => alert("Link copied!"));
}
