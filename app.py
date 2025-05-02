import os
import base64
from flask import Flask, request, send_from_directory, jsonify, render_template, send_file
from werkzeug.utils import secure_filename
from datetime import datetime
import qrcode
from io import BytesIO
from PIL import Image, ImageDraw

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'zip', 'rar', 'mp4', 'mp3'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'message': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        timestamp = datetime.now().strftime('%Y-%m-%d_%H%M%S')
        filename = secure_filename(f"{timestamp}_{file.filename}")
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        encoded = base64.urlsafe_b64encode(filename.encode()).decode()
        return jsonify({
            'filename': filename,
            'message': 'File uploaded successfully',
            'download_url': f"/d/{encoded}",
            'qr_url': f"/qr/{encoded}"
        })

    return jsonify({'message': 'File type not allowed'}), 400


@app.route('/d/<encoded>')
def download_encoded(encoded):
    try:
        filename = base64.urlsafe_b64decode(encoded.encode()).decode()
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
    except Exception:
        return jsonify({'error': 'Invalid or corrupted link'}), 400


@app.route('/qr/<encoded>')
def qr_code(encoded):
    try:
        url = request.host_url.rstrip('/') + f"/d/{encoded}"
        qr = qrcode.make(url)
        qr = qr.convert("RGBA")

        # Создаём круглую маску
        width, height = qr.size
        mask = Image.new('L', (width, height), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, width, height), fill=255)

        result = Image.new('RGBA', (width, height))
        result.paste(qr, (0, 0), mask=mask)

        buffer = BytesIO()
        result.save(buffer, format="PNG")
        buffer.seek(0)

        return send_file(buffer, mimetype='image/png')

    except Exception as e:
        return f"QR Code Error: {e}", 400


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
