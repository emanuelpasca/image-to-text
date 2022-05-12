from flask import Flask
from flask import request, jsonify, send_file
import os
from PIL import Image
import pytesseract
from flask_cors import CORS
from werkzeug.utils import secure_filename
import cv2

pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

app = Flask(__name__)
CORS(app)

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['img']
    user_folder = 'imgs'

    filename = secure_filename(file.filename)
    path = os.path.join(user_folder, filename)
    file.save(path)

    img = Image.open(path)

    result = pytesseract.image_to_string(img)

    #os.remove(path)

    return jsonify({'result': result})