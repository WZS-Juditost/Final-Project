"""
utilities.py
------------
Utility functions for shared operations across various image processing tasks.

Author: Zesheng Wang
Date: 2024-12-02
"""
import cv2
import numpy as np
from sklearn.cluster import MiniBatchKMeans

def kmeans_color_quantization(image, clusters=8, batch_size=4096):
    """
    Reduce the number of colors in the image using k-means clustering.

    Args:
        image (numpy.ndarray): The input image in BGR format.
        clusters (int): Number of color clusters.
        batch_size (int): Batch size for MiniBatchKMeans.

    Returns:
        numpy.ndarray: The quantized image with reduced colors.
    """
    data = image.reshape((-1, 3))
    kmeans = MiniBatchKMeans(n_clusters=clusters, batch_size=batch_size, n_init=3)
    labels = kmeans.fit_predict(data)
    centers = kmeans.cluster_centers_.astype("uint8")
    
    quantized = centers[labels]
    quantized_image = quantized.reshape(image.shape)
    return quantized_image

def apply_background_blur(image, edges, blur_strength=15):
    """
    Blur the background of the image while keeping edges intact.

    Args:
        image (numpy.ndarray): The input image in BGR format.
        edges (numpy.ndarray): Edge map of the image.
        blur_strength (int): Strength of the Gaussian blur for the background.

    Returns:
        numpy.ndarray: The image with a blurred background.
    """
    mask = cv2.bitwise_not(edges)
    mask_colored = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
    blurred_background = cv2.GaussianBlur(image, (blur_strength, blur_strength), 0)
    blended = np.where(mask_colored == 0, blurred_background, image)
    return blended

def resize_image_proportionally(image, max_width, max_height):
    """
    Resize the image to fit within the specified maximum dimensions.

    Args:
        image (numpy.ndarray): The input image in BGR format.
        max_width (int): Maximum allowed width for the resized image.
        max_height (int): Maximum allowed height for the resized image.

    Returns:
        numpy.ndarray: The resized image with preserved aspect ratio.
    """
    original_height, original_width = image.shape[:2]
    aspect_ratio = original_width / original_height

    # Determine new dimensions while maintaining aspect ratio
    if original_width > original_height:
        new_width = min(original_width, max_width)
        new_height = int(new_width / aspect_ratio)
    else:
        new_height = min(original_height, max_height)
        new_width = int(new_height * aspect_ratio)

    # Adjust dimensions
    if new_width > max_width:
        new_width = max_width
        new_height = int(new_width / aspect_ratio)
    if new_height > max_height:
        new_height = max_height
        new_width = int(new_height * aspect_ratio)

    resized_image = cv2.resize(image, (new_width, new_height))
    return resized_image