from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import os
import cv2
import base64
import numpy as np
from simple_cartoonize_image import apply_filter

app = Flask(__name__)
socketio = SocketIO(app)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return render_template('index_realtime.html')

@socketio.on('apply_filter')
def handle_filter(data):
    """
    Handle the filter application request.
    """
    # Decode the image data
    img_data = data.get('image')
    filter_type = data.get('filter')
    brightness = int(data.get('brightness', 0))
    contrast = int(data.get('contrast', 0))
    saturation = float(data.get('saturation', 1.0))

    # Convert the base64 string back to an image
    img_bytes = base64.b64decode(img_data.split(',')[1])
    img_array = np.frombuffer(img_bytes, dtype=np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

    # Apply the selected filter
    if filter_type:
        processed_img = apply_filter(img, filter_type, brightness, contrast, saturation)
    else:
        processed_img = img

    # Encode the processed image back to base64
    _, buffer = cv2.imencode('.jpg', processed_img)
    processed_img_base64 = base64.b64encode(buffer).decode('utf-8')

    # Send the processed image back to the client
    emit('filtered_image', {'image': f"data:image/jpeg;base64,{processed_img_base64}"})

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
