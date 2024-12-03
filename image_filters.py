"""
image_filters.py
----------------
Contains functions to apply various image filters like sepia, pencil sketch, oil painting, etc.

Author: Zesheng Wang
Date: 2024-12-02
"""
import cv2
import numpy as np
from image_enhancements import *
from utilities import *

def apply_sepia(image):
    """Apply a sepia tone to the image."""
    kernel = np.array([[0.272, 0.534, 0.131],
                       [0.349, 0.686, 0.168],
                       [0.393, 0.769, 0.189]])
    sepia_image = cv2.transform(image, kernel)
    sepia_image = np.clip(sepia_image, 0, 255).astype(np.uint8)
    return sepia_image

def apply_pencil_sketch(image):
    """Convert the image to a pencil sketch."""
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    inverted = cv2.bitwise_not(gray_image)
    blurred = cv2.GaussianBlur(inverted, (21, 21), 0)
    inverted_blurred = cv2.bitwise_not(blurred)
    sketch_image = cv2.divide(gray_image, inverted_blurred, scale=256.0)
    return cv2.cvtColor(sketch_image, cv2.COLOR_GRAY2BGR)

def apply_oil_painting(image, size=7, dyn_ratio=1):
    """Apply an oil painting effect to the image."""
    oil_painting = cv2.xphoto.oilPainting(image, size, dyn_ratio)
    return oil_painting

def convert_to_black_and_white(image):
    """
    Convert the image to black and white (grayscale).
    """
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return cv2.cvtColor(gray_image, cv2.COLOR_GRAY2BGR)

def process_cartoonization(image):
    """
    Process the image to apply cartoonization effects.
    """
    gamma_corrected = adjust_gamma(image, gamma=1.5)
    gray = cv2.cvtColor(gamma_corrected, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, threshold1=50, threshold2=150)
    color = cv2.bilateralFilter(gamma_corrected, d=9, sigmaColor=120, sigmaSpace=120)
    quantized = kmeans_color_quantization(color, clusters=20)
    blurred_background = apply_background_blur(quantized, edges, blur_strength=21)
    edges_inv = cv2.bitwise_not(edges)
    edges_inv_colored = cv2.cvtColor(edges_inv, cv2.COLOR_GRAY2BGR)
    alpha = 0.8
    beta = 0.2
    cartoonized_img = cv2.addWeighted(blurred_background, alpha, edges_inv_colored, beta, 0)

    return cartoonized_img

def apply_filter(image, filter_type, brightness=0, contrast=0, saturation=1.0):
    """
    Apply various filters based on the filter_type parameter.
    Preprocess the image with brightness, contrast, and saturation adjustments.
    """
    adjusted_image = adjust_brightness_contrast(image, brightness, contrast)
    adjusted_image = adjust_saturation(adjusted_image, saturation)

    if filter_type == "sepia":
        return apply_sepia(adjusted_image)
    elif filter_type == "pencil_sketch":
        return apply_pencil_sketch(adjusted_image)
    elif filter_type == "oil_painting":
        return apply_oil_painting(adjusted_image)
    elif filter_type == "black_and_white":
        return convert_to_black_and_white(adjusted_image)
    elif filter_type == "cartoon":
        return process_cartoonization(adjusted_image)
    else:
        return adjusted_image
