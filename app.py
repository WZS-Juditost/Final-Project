from flask import Flask, request, render_template, send_file
import cv2
import numpy as np
import os
from simple_cartoonize_image import cartoonize_image  # 导入你写好的卡通化函数

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
RESULT_FOLDER = "results"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESULT_FOLDER'] = RESULT_FOLDER

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/cartoonize', methods=['POST'])
def cartoonize():
    if 'image' not in request.files:
        return "No image uploaded", 400

    file = request.files['image']
    if file.filename == '':
        return "No image selected", 400

    # Get additional parameters
    brightness = int(request.form.get('brightness', 0))
    contrast = int(request.form.get('contrast', 0))
    saturation = float(request.form.get('saturation', 1.0))

    input_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(input_path)

    output_path = os.path.join(app.config['RESULT_FOLDER'], f"cartoon_{file.filename}")

    # Pass parameters to cartoonize_image
    cartoonize_image(input_path, output_path, brightness=brightness, contrast=contrast, saturation=saturation)

    return send_file(output_path, mimetype='image/jpeg')

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
