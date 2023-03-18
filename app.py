from flask import Flask, request, jsonify, send_file, render_template
import qrcode
import os
from io import BytesIO
from PIL import Image
import numpy as np
import cv2

app = Flask(__name__)

@app.route('/qrcode', methods=['POST'])
def generate_qrcode():
    # Get the data from the request
    data = request.form['data']
    color = request.form['color']

    # Get the uploaded image from the request
    image_file = request.files.get('image')   

    # Generate the QR code image with white background
    qr = qrcode.QRCode(
        # version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        # box_size=10,
        # border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    # Apply the color mask to the QR code image
    qr_image = qr.make_image(fill_color=color, back_color='white')

    # Convert the white background to transparent
    qr_image = qr_image.convert("RGBA")
    datas = qr_image.getdata()
    newData = []
    for item in datas:
        if item[0] == 255 and item[1] == 255 and item[2] == 255:
            newData.append((255, 255, 255, 0))
        else:
            newData.append(item)
    qr_image.putdata(newData)

    # Resize the image to fit inside the QR code
    if image_file:
        image = Image.open(image_file) 
        qr_width, qr_height = qr_image.size
        image.thumbnail((qr_width * 0.3, qr_height * 0.3))

        # Calculate the position to place the image
        image_x = int((qr_width - image.width) / 2)
        image_y = int((qr_height - image.height) / 2)

        # Paste the image onto the QR code
        qr_image = qr_image.convert('RGBA')
        qr_image.paste(image, (image_x, image_y), mask=image)

    # Create an in-memory file-like object to hold the image data
    img_io = BytesIO()

    # Save the image data to the in-memory file-like object
    qr_image.save(img_io, 'png')
    qr_image.save('test.png')

    # Set the file position of the in-memory file-like object to the beginning
    img_io.seek(0)

    # Return the image as a Flask response with the appropriate MIME type
    response = send_file(img_io, mimetype='image/png')

    return response

@app.route('/readqrcode', methods=['POST'])
def read_qrcode():


    # Get the uploaded image from the request
    image_file = request.files.get('image')

    # Open the image file as a numpy array using OpenCV
    image = cv2.imdecode(np.fromstring(image_file.read(), np.uint8), cv2.IMREAD_UNCHANGED)

    # Decode the QR code data using OpenCV
    qr_decoder = cv2.QRCodeDetector()
    data, bbox, _ = qr_decoder.detectAndDecode(image)

    # Return the decoded data as JSON
    return jsonify({'data': data})

@app.route('/')
def home():
    return render_template('index.html')


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=True, host='0.0.0.0', port=port)
