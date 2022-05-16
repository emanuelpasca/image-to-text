from flask import Flask
from flask import request, jsonify, send_file
import os
from PIL import Image
import pytesseract
from flask_cors import CORS
from werkzeug.utils import secure_filename
import cv2
import numpy as np

# ------------------------------------------------------------------------------------------

pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

# ------------------------------------------------------------------------------------------


def noise_removal(image):  # scoate pixelii care nu corespund textului
    import numpy as np
    kernel = np.ones((1, 1), np.uint8)
    image = cv2.dilate(image, kernel, iterations=1)
    kernel = np.ones((1, 1), np.uint8)
    image = cv2.erode(image, kernel, iterations=1)
    image = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
    image = cv2.medianBlur(image, 3)
    return (image)


def thin_font(image):  # face caracterele mai subtiri pentru a fi mai usor de recunoscut de OCR
    image = cv2.bitwise_not(image)  # convertim background-ul la negru si fontul la alb
    kernel = np.ones((2, 2), np.uint8)
    image = cv2.erode(image, kernel, iterations=1)
    image = cv2.bitwise_not(image)  # convertim background-ul inapoi la alb si fontul la negru
    return (image)

def thick_font(image):  # face caracterele mai groase
    import numpy as np
    image = cv2.bitwise_not(image)
    kernel = np.ones((2,2),np.uint8)
    image = cv2.dilate(image, kernel, iterations=1) # expandeaza pixelii
    image = cv2.bitwise_not(image)
    return (image)


def getSkewAngle(cvImage) -> float:
    # Pregatim imaginea, o facem gri si o bluram
    newImage = cvImage.copy()
    gray = cv2.cvtColor(newImage, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (9, 9), 0)
    thresh = cv2.threshold(
        blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    # Expandam pixelii pentru a uni textul in paragrafe
    # Utilizam un kernel mai mare pe axa X pentru a imbina caracterele intro-o singura linie, anuland spatiile.
    # Folosim kernel mai mic  pe axa Y pentru a separa diferite block-uri de text
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (30, 5))
    dilate = cv2.dilate(thresh, kernel, iterations=2)

    # Gasim contururile caracterelor
    contours, hierarchy = cv2.findContours(
        dilate, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    for c in contours:
        rect = cv2.boundingRect(c)
        x, y, w, h = rect
        cv2.rectangle(newImage, (x, y), (x+w, y+h), (0, 255, 0), 2)

    largestContour = contours[0]
    print(len(contours))
    minAreaRect = cv2.minAreaRect(largestContour)
    cv2.imwrite("temp/boxes.jpg", newImage)
    # Determinam unghiul de rotire.
    angle = minAreaRect[-1]
    if angle < -45:
        angle = 90 + angle
    return -1.0 * angle

# Rotim imaginea in jurul centrului
def rotateImage(cvImage, angle: float):
    newImage = cvImage.copy()
    (h, w) = newImage.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    newImage = cv2.warpAffine(
        newImage, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return newImage

def deskew(cvImage):
    angle = getSkewAngle(cvImage)
    return rotateImage(cvImage, -1.0 * angle)


# ------------------------------------------------------------------------------------------

app = Flask(__name__)
CORS(app)


@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['img']
    user_folder = 'imgs'

    filename = secure_filename(file.filename)
    path = os.path.join(user_folder, filename)
    file.save(path)

    # binarization
    grayImg = cv2.imread(path, 0)

    # Noise removal
    no_noise = noise_removal(grayImg)
    cv2.imwrite(path, no_noise)

    # Dilation and Erosion
    eroded_image = thick_font(no_noise)
    cv2.imwrite(path, eroded_image)

    img = Image.open(path)

    result = pytesseract.image_to_string(img)

    if result == "":
        # Deskew image
        new = cv2.imread(path)
        fixed = deskew(new)
        cv2.imwrite(path, fixed)

        img2 = Image.open(path)
        result = pytesseract.image_to_string(img2)

        os.remove(path)

        return jsonify({'result': result})

    os.remove(path)

    return jsonify({'result': result})

# ------------------------------------------------------------------------------------------
