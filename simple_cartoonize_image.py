import cv2
import numpy as np
from sklearn.cluster import MiniBatchKMeans

def kmeans_color_quantization(image, clusters=8, batch_size=100):
    data = image.reshape((-1, 3))
    kmeans = MiniBatchKMeans(n_clusters=clusters, batch_size=batch_size)
    labels = kmeans.fit_predict(data)
    centers = np.uint8(kmeans.cluster_centers_)
    
    quantized = centers[labels]
    quantized_image = quantized.reshape(image.shape)
    return quantized_image

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

def apply_background_blur(image, edges, blur_strength=15):
    mask = cv2.bitwise_not(edges)
    mask_colored = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
    blurred_background = cv2.GaussianBlur(image, (blur_strength, blur_strength), 0)
    blended = np.where(mask_colored == 0, blurred_background, image)
    return blended

def convert_to_black_and_white(image):
    """
    Convert the image to black and white (grayscale).
    """
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return cv2.cvtColor(gray_image, cv2.COLOR_GRAY2BGR)

def resize_image_proportionally(image, max_width, max_height):
    original_height, original_width = image.shape[:2]
    aspect_ratio = original_width / original_height

    if original_width > original_height:
        new_width = min(original_width, max_width)
        new_height = int(new_width / aspect_ratio)
    else:
        new_height = min(original_height, max_height)
        new_width = int(new_height * aspect_ratio)

    if new_width > max_width:
        new_width = max_width
        new_height = int(new_width / aspect_ratio)
    if new_height > max_height:
        new_height = max_height
        new_width = int(new_height * aspect_ratio)

    resized_image = cv2.resize(image, (new_width, new_height))
    return resized_image

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

def apply_filter(image, filter_type, brightness=0, contrast=0, saturation=1.0):
    """
    Apply various filters based on the filter_type parameter.
    Preprocess the image with brightness, contrast, and saturation adjustments.
    """
    # Adjust brightness, contrast, and saturation first
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
    
def remove_noise(image, h=10):
    """
    Remove noise from the image using Non-Local Means Denoising.
    h: Parameter controlling filter strength. Higher h removes more noise.
    """
    denoised = cv2.fastNlMeansDenoisingColored(image, None, h, h, 7, 21)
    return denoised

def sharpen_image(image):
    """
    Apply sharpening filter to the image.
    """
    kernel = np.array([[0, -1, 0],
                       [-1, 5, -1],
                       [0, -1, 0]])
    sharpened = cv2.filter2D(image, -1, kernel)
    return sharpened

def smooth_image(image, kernel_size=5):
    """
    Apply Gaussian blur to smooth the image.
    kernel_size: Size of the Gaussian kernel.
    """
    smoothed = cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)
    return smoothed

def equalize_color(image):
    """
    Apply histogram equalization to improve color balance.
    """
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    hsv[:, :, 2] = cv2.equalizeHist(hsv[:, :, 2])  # Equalize only the V channel
    balanced = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    return balanced


def enhance_image(image, enhancements):
    """
    Apply image enhancement operations in sequence.
    enhancements: List of enhancement operations, e.g., ['denoise', 'sharpen'].
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
    return image


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

def process_image(image_path, output_path, max_width=1200, max_height=1200,
                  brightness=0, contrast=0, saturation=1.0,
                  enhancements=None, filter_type=None):
    """
    Process the image with enhancements and filter application.
    """
    img = cv2.imread(image_path)
    if img is None:
        print("Unable to read the image. Please check the path!")
        return

    # Resize the image
    resized_img = resize_image_proportionally(img, max_width, max_height)

    # Apply enhancements
    if enhancements:
        resized_img = enhance_image(resized_img, enhancements)

    # Apply filter
    if filter_type:
        processed_img = apply_filter(resized_img, filter_type, brightness, contrast, saturation)
    else:
        processed_img = resized_img

    cv2.imwrite(output_path, processed_img)
    print(f"Processed image saved at {output_path}")

if __name__ == "__main__":
    input_path = "image/2.jpg"
    output_path_sepia = "output_sepia.jpg"
    output_path_sketch = "output_pencil_sketch.jpg"
    output_path_oil = "output_oil_painting.jpg"
    output_path_bw = "output_black_and_white.jpg"
    output_path_cartoon = "output_cartoon.jpg"

    process_image(input_path, output_path_sepia, filter_type="sepia")
    process_image(input_path, output_path_sketch, filter_type="pencil_sketch")
    process_image(input_path, output_path_oil, filter_type="oil_painting")
    process_image(input_path, output_path_bw, filter_type="black_and_white", brightness=20, contrast=10)
    process_image(input_path, output_path_cartoon, filter_type="cartoon", brightness=20, contrast=20, saturation=1.5)
