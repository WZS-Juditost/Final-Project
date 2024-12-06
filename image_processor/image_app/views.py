from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.http import JsonResponse, FileResponse
import os
import shutil
import imghdr
import json
from .utils.image_processor import process_image

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'media/uploads')
RESULT_FOLDER = os.path.join(BASE_DIR, 'media/results')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

def home(request):
    return render(request, 'index.html')

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
