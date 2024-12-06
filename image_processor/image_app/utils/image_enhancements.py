"""
image_enhancements.py
---------------------
Provides functions for enhancing image quality, including brightness, contrast,
noise removal, sharpening, and automatic optimization.

Author: Zesheng Wang
Date: 2024-12-02
"""
import cv2
import numpy as np

def adjust_gamma(image, gamma=1.0):
    inv_gamma = 1.0 / gamma
    table = np.array([(i / 255.0) ** inv_gamma * 255 for i in np.arange(256)]).astype("uint8")
    return cv2.LUT(image, table)

def adjust_brightness_contrast(image, brightness=0, contrast=0):
    beta = brightness
    alpha = 1 + (contrast / 100.0)
    adjusted = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
    return adjusted

def adjust_saturation(image, saturation_scale=1.0):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    hsv[:, :, 1] = cv2.multiply(hsv[:, :, 1], saturation_scale)
    saturated_image = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    return saturated_image

def remove_noise(image, h=10):
    """
    Remove noise from the image using Non-Local Means Denoising.
    h: Parameter controlling filter strength..
    """
    denoised = cv2.fastNlMeansDenoisingColored(image, None, h, h, 7, 21)
    return denoised

def sharpen_image(image):
    """
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, threshold1=50, threshold2=150)
    edges_inv = cv2.bitwise_not(edges)
    denoised = cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)
    kernel = np.array([[0, -0.5, 0],
                       [-0.5, 3, -0.5],
                       [0, -0.5, 0]])
    sharpened = cv2.filter2D(denoised, -1, kernel)
    mask = cv2.cvtColor(edges_inv, cv2.COLOR_GRAY2BGR) / 255.0
    final_image = cv2.addWeighted(image, 0.7, sharpened, 0.3, 0) * mask + image * (1 - mask)
    final_image = np.clip(final_image, 0, 255).astype(np.uint8)
    return final_image

def smooth_image(image, kernel_size=5):
    """
    Apply Gaussian blur to smooth the image.
    kernel_size: Size of the Gaussian kernel.
    """
    smoothed = cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)
    return smoothed

def equalize_color(image):
    """
    """
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    hsv[:, :, 2] = clahe.apply(hsv[:, :, 2])
    hsv[:, :, 1] = cv2.multiply(hsv[:, :, 1], 0.9)
    balanced = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    return balanced

def enhance_image(image, enhancements):
    """
    Apply image enhancement operations in sequence.
    enhancements: List of enhancement operations.
    """
    for enhancement in enhancements:
        if enhancement == "denoise":
            image = remove_noise(image)
        elif enhancement == "sharpen":
            image = sharpen_image(image)
        elif enhancement == "smooth":
            image = smooth_image(image)
        elif enhancement == "color_balance":
            image = equalize_color(image)
        elif enhancement == "auto_optimize":
            image = auto_optimize_image(image)
    return image

def auto_optimize_image(image):
    optimized_image = equalize_color(image)
    result_channels = []
    for channel in cv2.split(optimized_image):
        normalized = cv2.normalize(channel, None, 0, 255, cv2.NORM_MINMAX)
        result_channels.append(normalized)
    optimized_image = cv2.merge(result_channels)
    hsv = cv2.cvtColor(optimized_image, cv2.COLOR_BGR2HSV)
    mask = hsv[:, :, 2] > 220
    hsv[:, :, 2][mask] = 220
    optimized_image = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    optimized_image = cv2.fastNlMeansDenoisingColored(optimized_image, None, 10, 10, 7, 21)
    kernel = np.array([[0, -0.3, 0],
                       [-0.3, 2, -0.3],
                       [0, -0.3, 0]])
    sharpened = cv2.filter2D(optimized_image, -1, kernel)
    optimized_image = cv2.addWeighted(optimized_image, 0.8, sharpened, 0.2, 0)
    return optimized_image