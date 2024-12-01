import cv2
import numpy as np

def kmeans_color_quantization(image, clusters=8):
    data = image.reshape((-1, 3))
    data = np.float32(data)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
    _, labels, centers = cv2.kmeans(data, clusters, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
    centers = np.uint8(centers)
    quantized = centers[labels.flatten()]
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

def cartoonize_image(image_path, output_path, max_width=1200, max_height=1200,
                     brightness=0, contrast=0, saturation=1.0):
    img = cv2.imread(image_path)
    if img is None:
        print("Unable to read the image. Please check the path!")
        return

    resized_img = resize_image_proportionally(img, max_width, max_height)

    # Adjust brightness, contrast, and saturation
    adjusted_brightness_contrast = adjust_brightness_contrast(resized_img, brightness, contrast)
    adjusted_saturation = adjust_saturation(adjusted_brightness_contrast, saturation)

    gamma_corrected = adjust_gamma(adjusted_saturation, gamma=1.5)
    gray = cv2.cvtColor(gamma_corrected, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, threshold1=50, threshold2=150)

    color = cv2.bilateralFilter(gamma_corrected, d=9, sigmaColor=120, sigmaSpace=120)
    quantized = kmeans_color_quantization(color, clusters=20)
    blurred_background = apply_background_blur(quantized, edges, blur_strength=21)

    edges_inv = cv2.bitwise_not(edges)
    edges_inv_colored = cv2.cvtColor(edges_inv, cv2.COLOR_GRAY2BGR)

    alpha = 0.8  # Weight for the color image
    beta = 0.2   # Weight for the edges
    cartoon = cv2.addWeighted(blurred_background, alpha, edges_inv_colored, beta, 0)

    cv2.imwrite(output_path, cartoon)
    print(f"Enhanced cartoonized image saved at {output_path}")

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

# Test the cartoonization function
if __name__ == "__main__":
    input_path = "image/2.jpg"
    output_path = "enhanced_output_cartoon.jpg"
    cartoonize_image(input_path, output_path, brightness=30, contrast=20, saturation=1.5)
