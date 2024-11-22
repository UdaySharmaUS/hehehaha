// script.js
document.getElementById('uploadButton').addEventListener('click', () => {
    const fileInput = document.getElementById('file');
    const file = fileInput.files[0];

    if (!file) {
        alert("Please upload a file.");
        return;
    }

    const formData = new FormData();
    formData.append('file', file);

    // Send file to the backend
    fetch('/upload', {
        method: 'POST',
        body: formData,
    })
        .then(response => response.json())
        .then(data => {
            // Display metadata
            const metadataDiv = document.getElementById('metadata');
            metadataDiv.innerHTML = `
                <p><strong>Title:</strong> ${data.metadata.Title || 'N/A'}</p>
                <p><strong>Author:</strong> ${data.metadata.Author || 'N/A'}</p>
                <p><strong>Creation Date:</strong> ${data.metadata['Creation Date'] || 'N/A'}</p>
            `;

            // Show download link
            const downloadLink = document.getElementById('downloadLink');
            downloadLink.href = data.pdf_url;
            downloadLink.style.display = 'block';

            // Show delete button
            const deleteButton = document.getElementById('deleteButton');
            deleteButton.style.display = 'block';
            deleteButton.addEventListener('click', () => deleteFile(data.file_path));
        })
        .catch(error => console.error("Error:", error));
});

function deleteFile(filePath) {
    fetch('/delete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ file_path: filePath }),
    })
        .then(response => response.json())
        .then(data => alert(data.message))
        .catch(error => console.error("Error:", error));
}
