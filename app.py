import os
from flask import Flask, request, send_from_directory, render_template, jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'  # Папка для загрузки файлов
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'txt', 'pdf'}  # Разрешенные форматы

# Функция для проверки допустимых расширений
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Главная страница
@app.route('/')
def index():
    return render_template('index.html')  # Возвращаем HTML страницу с формой

# Загрузка файла
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)  # Защищаем имя файла
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # Отправляем информацию о файле на фронтэнд
        return jsonify({
            'message': 'File uploaded successfully',
            'filename': filename,
            'file_url': f'/files/{filename}'  # Ссылка на файл
        }), 200
    else:
        return jsonify({'error': 'Invalid file type'}), 400

# Скачивание файла
@app.route('/files/<filename>')
def download_file(filename):
    try:
        # Проверяем путь и обрабатываем скачивание файла
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
    except FileNotFoundError:
        return jsonify({'error': 'File not found'}), 404

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True, host='0.0.0.0', port=80)
