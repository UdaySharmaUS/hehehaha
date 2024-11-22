

from flask import Flask, request, jsonify, send_file, render_template
from werkzeug.utils import secure_filename
from docx import Document
from docx2pdf import convert
import os
import pythoncom

# Initialize Flask app
app = Flask(__name__, static_folder='static', template_folder='templates')  # Fixed __name_
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['CONVERTED_FOLDER'] = 'converted'

# Ensure required directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['CONVERTED_FOLDER'], exist_ok=True)

# Route for serving the main HTML page
@app.route('/')
def index():
    return render_template('index.html')  # Assumes your HTML file is in the "templates" folder

# Route for handling file uploads and conversion
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    # Extract metadata
    metadata = get_metadata(file_path)

    # Convert to PDF
    pdf_path = os.path.join(app.config['CONVERTED_FOLDER'], f"{os.path.splitext(filename)[0]}.pdf")
    convert_to_pdf(file_path, pdf_path)

    return jsonify({
        'metadata': metadata,
        'pdf_url': f"/download/{os.path.basename(pdf_path)}",
        'file_path': pdf_path
    })

# Route for downloading the converted PDF
@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    file_path = os.path.join(app.config['CONVERTED_FOLDER'], filename)
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404
    return send_file(file_path, as_attachment=True)

# Route for deleting files
@app.route('/delete', methods=['POST'])
def delete_file():
    data = request.get_json()
    file_path = data.get('file_path')

    if os.path.exists(file_path):
        os.remove(file_path)
        return jsonify({'message': 'File deleted successfully'})
    return jsonify({'error': 'File not found'}), 404

# Function to extract metadata from a DOCX file
def get_metadata(file_path):
    doc = Document(file_path)
    core_props = doc.core_properties
    return {
        'Title': getattr(core_props, 'title', 'N/A'),
        'Author': getattr(core_props, 'author', 'N/A'),
        'Creation Date': str(getattr(core_props, 'created', 'N/A')),
    }

# # Function to convert DOCX to PDF
# def convert_to_pdf(docx_path, pdf_path):
#     # convert(docx_path, app.config['CONVERTED_FOLDER'])
#     convert(docx_path, pdf_path)


import pythoncom  # Import the module for initializing the COM environment
from docx2pdf import convert

def convert_to_pdf(docx_path, pdf_path):
    # Initialize the COM environment
    pythoncom.CoInitialize()
    try:
        # Use the docx2pdf library to convert the file
        convert(docx_path, pdf_path)
    finally:
        # Ensure the COM environment is uninitialized after processing
        pythoncom.CoUninitialize()

# Run Flask app
if __name__ == '__main__':
    app.run(debug=True)
