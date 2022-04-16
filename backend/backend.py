from flask import Flask
from flask import request, jsonify, send_file
import os
from PIL import Image
import pytesseract
from flask_cors import CORS

pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

app = Flask(__name__)
CORS(app)

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files.get('img')
    user_folder = 'imgs'

    filename = os.path.join(user_folder, "file")
    file.save(filename)

    img = Image.open(filename)

    return jsonify({'result': pytesseract.image_to_string(img)})