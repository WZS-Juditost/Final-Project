from flask import Flask, request, send_file, render_template
import os
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

@app.route('/cartoonize', methods=['POST'])
def cartoonize():
    if 'image' not in request.files:
        return "No image uploaded", 400

    file = request.files['image']
    if file.filename == '':
        return "No image selected", 400

    # Save uploaded file
    input_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(input_path)

    # Get processing options from form
    apply_cartoon = request.form.get('cartoonize', 'false').lower() == 'true'
    apply_bw = request.form.get('black_and_white', 'false').lower() == 'true'
    brightness = int(request.form.get('brightness', 0))
    contrast = int(request.form.get('contrast', 0))
    saturation = float(request.form.get('saturation', 1.0))

    # Define output path
    output_path = os.path.join(app.config['RESULT_FOLDER'], f"processed_{file.filename}")

    # Process the image with the updated function
    process_image(input_path, output_path, brightness=brightness, contrast=contrast, saturation=saturation,
                  apply_cartoon=apply_cartoon, apply_bw=apply_bw)

    return send_file(output_path, mimetype='image/jpeg')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
