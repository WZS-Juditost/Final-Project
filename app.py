from flask import Flask, request, send_file, jsonify, render_template
import os
import shutil
import imghdr
import json
from simple_cartoonize_image import process_image

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

@app.route('/convert', methods=['POST'])
def cartoonize():
    if 'image' not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "No image selected"}), 400

    input_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(input_path)

    if not imghdr.what(input_path):
        os.remove(input_path)
        return jsonify({"error": "Uploaded file is not a valid image"}), 400

    filter_type = request.form.get('filter', '')
    brightness = int(request.form.get('brightness', 0))
    contrast = int(request.form.get('contrast', 0))
    saturation = float(request.form.get('saturation', 1.0))

    # Parse enhancements
    enhancements = request.form.get('enhancements', '[]')
    enhancements = json.loads(enhancements)

    output_path = os.path.join(app.config['RESULT_FOLDER'], f"processed_{file.filename}")

    try:
        process_image(input_path, output_path, brightness=brightness, contrast=contrast,
                      saturation=saturation, enhancements=enhancements, filter_type=filter_type)

        return send_file(output_path, mimetype='image/jpeg', as_attachment=True, 
                         download_name=f"processed_{file.filename}")
    except Exception as e:
        return jsonify({"error": f"Failed to process image: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
