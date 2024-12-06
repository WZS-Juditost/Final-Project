"""
image_filters.py
----------------
Contains functions to apply various image filters like sepia, pencil sketch, oil painting, etc.

Author: Zesheng Wang
Date: 2024-12-02
"""
import cv2
import numpy as np
from .image_enhancements import *
from .utilities import *

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

def apply_hdr_effect(image):
    """
    Apply HDR effect to the image.
    """
    image = remove_noise(image)
    hdr = cv2.detailEnhance(image, sigma_s=12, sigma_r=0.15)
    return hdr

def apply_dslr_blur(image, focus_area=None, blur_strength=21):
    """
    Apply DSLR-like blur effect with a circular focus area and gradual blur transitions.
    
    focus_area: A tuple (cx, cy, r) defining the center (cx, cy) and radius (r) of the focus area.
    blur_strength: Strength of the Gaussian blur applied to the background.
    """
    height, width = image.shape[:2]
    if focus_area is None:
        focus_area = (width // 2, height // 2, min(width, height) // 4)

    cx, cy, radius = focus_area
    mask = np.zeros((height, width), dtype=np.uint8)
    cv2.circle(mask, (cx, cy), radius, 255, -1)
    blurred_mask = cv2.GaussianBlur(mask, (2 * blur_strength + 1, 2 * blur_strength + 1), 0)
    normalized_mask = blurred_mask.astype(np.float32) / 255.0
    blurred_image = cv2.GaussianBlur(image, (blur_strength, blur_strength), 0)
    sharp_focus = image.astype(np.float32) * normalized_mask[..., None]
    blurred_background = blurred_image.astype(np.float32) * (1 - normalized_mask[..., None])
    final_image = sharp_focus + blurred_background
    final_image = np.clip(final_image, 0, 255).astype(np.uint8)

    return final_image

def apply_glitch_effect(image, intensity=10):
    """
    Apply a glitch effect to the image.
    intensity: How many rows/columns to shift for the glitch.
    """
    height, width = image.shape[:2]
    glitch_image = image.copy()

    for i in range(0, height, intensity):
        shift = np.random.randint(-intensity, intensity)
        glitch_image[i:i+intensity, :] = np.roll(image[i:i+intensity, :], shift, axis=1)
    
    return glitch_image

def apply_pixelation(image, pixel_size=10):
    """
    Apply pixelation effect to the image.
    pixel_size: Size of each pixel block.
    """
    height, width = image.shape[:2]
    small_image = cv2.resize(image, (width // pixel_size, height // pixel_size), interpolation=cv2.INTER_NEAREST)
    pixelated_image = cv2.resize(small_image, (width, height), interpolation=cv2.INTER_NEAREST)
    return pixelated_image

def apply_filter(image, filter_type, brightness=0, contrast=0, saturation=1.0):
    """
    Apply various filters based on the filter_type parameter.
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
    elif filter_type == "hdr":
        return apply_hdr_effect(adjusted_image)
    elif filter_type == "dslr_blur":
        return apply_dslr_blur(adjusted_image)
    elif filter_type == "glitch":
        return apply_glitch_effect(adjusted_image)
    elif filter_type == "pixelation":
        return apply_pixelation(adjusted_image)
    else:
        return adjusted_image

