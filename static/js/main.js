const fileInput = document.getElementById('fileInput');
const dropzone = document.getElementById('dropzone');
const filename = document.getElementById('filename');
const uploadBtn = document.getElementById('uploadBtn');
const status = document.getElementById('status');
const results = document.getElementById('results');
const originalImg = document.getElementById('originalImg');
const pixelatedImg = document.getElementById('pixelatedImg');

fileInput.addEventListener('change', () => {
  if (fileInput.files[0]) {
    filename.textContent = fileInput.files[0].name;
    uploadBtn.disabled = false;
    results.classList.remove('visible');
    status.textContent = '';
    status.className = '';
  }
});

dropzone.addEventListener('dragover', e => {
  e.preventDefault();
  dropzone.classList.add('drag-over');
});

dropzone.addEventListener('dragleave', () => {
  dropzone.classList.remove('drag-over');
});

dropzone.addEventListener('drop', e => {
  e.preventDefault();
  dropzone.classList.remove('drag-over');
  if (e.dataTransfer.files[0]) {
    fileInput.files = e.dataTransfer.files;
    filename.textContent = e.dataTransfer.files[0].name;
    uploadBtn.disabled = false;
    results.classList.remove('visible');
    status.textContent = '';
  }
});

uploadBtn.addEventListener('click', async () => {
  if (!fileInput.files[0]) return;

  uploadBtn.disabled = true;
  results.classList.remove('visible');
  status.className = '';
  status.innerHTML = '<span class="spinner"></span> UPLOADING & PROCESSING...';

  const formData = new FormData();
  formData.append('image', fileInput.files[0]);

  try {
    const res = await fetch('/upload', { method: 'POST', body: formData });
    const data = await res.json();

    if (!res.ok) {
      status.textContent = data.error || 'Something went wrong.';
      status.className = 'error';
    } else {
      status.textContent = 'DONE.';
      originalImg.src = data.original;
      pixelatedImg.src = data.pixelated;
      results.classList.add('visible');
    }
  } catch (err) {
    status.textContent = 'Network error. Is the Flask server running?';
    status.className = 'error';
  }

  uploadBtn.disabled = false;
});
