from flask import Flask, request, send_from_directory, render_template
import os
from datetime import datetime

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return {'error': 'No file part'}, 400
    file = request.files['file']
    if file.filename == '':
        return {'error': 'No selected file'}, 400
    filename = datetime.now().strftime('%Y-%m-%d_%H%M%S') + "_" + file.filename
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    return {'message': 'File uploaded successfully', 'filename': filename}

@app.route('/files/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    app.run()
