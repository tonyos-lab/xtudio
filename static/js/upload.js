// xtudio — upload.js
// File upload drag & drop handler for requirements upload

'use strict';

(function initUpload() {
    const uploadArea = document.getElementById('upload-area');
    const fileInput  = document.getElementById('file-input');
    const fileList   = document.getElementById('file-list');
    const errorEl    = document.getElementById('upload-error');

    if (!uploadArea || !fileInput) return;

    const ALLOWED_EXT = ['.pdf', '.docx', '.doc', '.txt', '.md'];
    const MAX_BYTES   = 10 * 1024 * 1024; // 10MB

    function clearError() {
        if (errorEl) { errorEl.textContent = ''; errorEl.style.display = 'none'; }
    }

    function showError(msg) {
        if (errorEl) { errorEl.textContent = msg; errorEl.style.display = ''; }
    }

    function formatSize(bytes) {
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
        return (bytes / 1024 / 1024).toFixed(1) + ' MB';
    }

    function getExt(name) {
        return name.slice(name.lastIndexOf('.')).toLowerCase();
    }

    function renderFileList(files) {
        if (!fileList) return;
        fileList.innerHTML = '';
        Array.from(files).forEach(function (file) {
            const ext = getExt(file.name);
            const valid = ALLOWED_EXT.includes(ext) && file.size <= MAX_BYTES;
            const item = document.createElement('div');
            item.style.cssText = 'display:flex; align-items:center; gap:8px; padding:6px 0; border-bottom:1px solid var(--border); font-size:0.8rem;';
            item.innerHTML =
                '<span style="color:' + (valid ? 'var(--success)' : 'var(--danger)') + '">&#9679;</span>' +
                '<span style="color:var(--text); font-family:var(--mono);">' + file.name + '</span>' +
                '<span style="color:var(--text-3); margin-left:auto;">' + formatSize(file.size) + '</span>';
            fileList.appendChild(item);
        });
    }

    function validateFiles(files) {
        clearError();
        const errors = [];
        Array.from(files).forEach(function (file) {
            const ext = getExt(file.name);
            if (!ALLOWED_EXT.includes(ext)) {
                errors.push(file.name + ': unsupported file type (' + ext + ')');
            } else if (file.size > MAX_BYTES) {
                errors.push(file.name + ': exceeds 10MB limit (' + formatSize(file.size) + ')');
            }
        });
        if (errors.length) { showError(errors.join(' · ')); return false; }
        return true;
    }

    // File input change
    fileInput.addEventListener('change', function () {
        if (fileInput.files.length) {
            validateFiles(fileInput.files);
            renderFileList(fileInput.files);
        }
    });

    // Drag events
    uploadArea.addEventListener('dragover', function (e) {
        e.preventDefault();
        uploadArea.classList.add('drag-over');
    });

    uploadArea.addEventListener('dragleave', function () {
        uploadArea.classList.remove('drag-over');
    });

    uploadArea.addEventListener('drop', function (e) {
        e.preventDefault();
        uploadArea.classList.remove('drag-over');
        const dt = e.dataTransfer;
        if (dt && dt.files.length) {
            // Assign dropped files to input
            try {
                const dataTransfer = new DataTransfer();
                Array.from(dt.files).forEach(function (f) { dataTransfer.items.add(f); });
                fileInput.files = dataTransfer.files;
            } catch (err) {
                // DataTransfer not supported in all browsers — fall back silently
            }
            validateFiles(dt.files);
            renderFileList(dt.files);
        }
    });
})();
