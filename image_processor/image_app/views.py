from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.http import JsonResponse, FileResponse
import os
import shutil
import imghdr
import json
from .utils.image_processor import process_image
import subprocess
from django.shortcuts import render
from django.http import JsonResponse
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'media/uploads')
RESULT_FOLDER = os.path.join(BASE_DIR, 'media/results')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

def home(request):
    return render(request, 'index.html')

def style_transfer_page(request):
    return render(request, 'style_transfer.html')

def cartoonize(request):
    if request.method == 'POST':
        if 'image' not in request.FILES:
            return JsonResponse({"error": "No image uploaded"}, status=400)

        file = request.FILES['image']
        if not file.name:
            return JsonResponse({"error": "No image selected"}, status=400)

        input_path = os.path.join(UPLOAD_FOLDER, file.name)
        with open(input_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        if not imghdr.what(input_path):
            os.remove(input_path)
            return JsonResponse({"error": "Uploaded file is not a valid image"}, status=400)

        filter_type = request.POST.get('filter', '')
        brightness = int(request.POST.get('brightness', 0))
        contrast = int(request.POST.get('contrast', 0))
        saturation = float(request.POST.get('saturation', 1.0))

        enhancements = request.POST.get('enhancements', '[]')
        enhancements = json.loads(enhancements)

        output_path = os.path.join(RESULT_FOLDER, f"processed_{file.name}")

        try:
            process_image(input_path, output_path, brightness=brightness, contrast=contrast,
                          saturation=saturation, enhancements=enhancements, filter_type=filter_type)

            return FileResponse(open(output_path, 'rb'), content_type='image/jpeg',
                                as_attachment=True, filename=f"processed_{file.name}")
        except Exception as e:
            return JsonResponse({"error": f"Failed to process image: {str(e)}"}, status=500)
    return JsonResponse({"error": "Invalid request method"}, status=405)

STYLE_OUTPUT_DIR = os.path.join(BASE_DIR, 'media/style_results')
os.makedirs(STYLE_OUTPUT_DIR, exist_ok=True)

def style_transfer(request):
    if request.method == 'POST':
        if 'content_image' not in request.FILES or 'style_image' not in request.FILES:
            return JsonResponse({"error": "Content and style images are required"}, status=400)
        
        content_file = request.FILES['content_image']
        style_file = request.FILES['style_image']
        
        content_path = os.path.join(UPLOAD_FOLDER, f"content_{content_file.name}")
        style_path = os.path.join(UPLOAD_FOLDER, f"style_{style_file.name}")
        output_path = os.path.join(STYLE_OUTPUT_DIR, f"styled_{content_file.name}")
        
        with open(content_path, 'wb+') as destination:
            for chunk in content_file.chunks():
                destination.write(chunk)
        
        with open(style_path, 'wb+') as destination:
            for chunk in style_file.chunks():
                destination.write(chunk)

        try:
            subprocess.run([
                'python', 'neural-style-pt/neural_style.py',
                '-content_image', content_path,
                '-style_image', style_path,
                '-output_image', output_path,
                '-image_size', '512',
                '-num_iterations', '500'
            ], check=True)
            
            return JsonResponse({"result_image": f"/media/style_results/styled_{content_file.name}"})
        except subprocess.CalledProcessError as e:
            return JsonResponse({"error": "Failed to process style transfer", "details": str(e)}, status=500)
    else:
        return JsonResponse({"error": "Invalid request method"}, status=405)