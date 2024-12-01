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

def process_black_and_white(image, brightness=0, contrast=0):
    """
    Process the image to convert it to black and white.
    """
    adjusted = adjust_brightness_contrast(image, brightness, contrast)
    bw_image = convert_to_black_and_white(adjusted)
    return bw_image

def process_cartoonization(image, brightness=0, contrast=0, saturation=1.0):
    """
    Process the image to apply cartoonization effects.
    """

    adjusted_brightness_contrast = adjust_brightness_contrast(image, brightness, contrast)
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
    alpha = 0.8
    beta = 0.2
    cartoonized_img = cv2.addWeighted(blurred_background, alpha, edges_inv_colored, beta, 0)
    
    return cartoonized_img

def process_image(image_path, output_path, max_width=1200, max_height=1200,
                  brightness=0, contrast=0, saturation=1.0,
                  apply_cartoon=False, apply_bw=False):
    """
    Main function to process an image, applying optional cartoonization and/or black-and-white conversion.
    """
    img = cv2.imread(image_path)
    if img is None:
        print("Unable to read the image. Please check the path!")
        return


    resized_img = resize_image_proportionally(img, max_width, max_height)

    if apply_cartoon:
        processed_img = process_cartoonization(resized_img, brightness, contrast, saturation)
    else:
        processed_img = resized_img
    if apply_bw:
        processed_img = process_black_and_white(processed_img, brightness, contrast)

    cv2.imwrite(output_path, processed_img)
    print(f"Processed image saved at {output_path}")


if __name__ == "__main__":
    input_path = "image/2.jpg"
    output_path_bw = "output_black_and_white.jpg"
    output_path_cartoon = "output_cartoon.jpg"
    output_path_combined = "output_combined.jpg"

    process_image(input_path, output_path_bw, brightness=20, contrast=10, apply_bw=True)
    process_image(input_path, output_path_cartoon, brightness=30, contrast=20, saturation=1.5, apply_cartoon=True)
    process_image(input_path, output_path_combined, brightness=30, contrast=20, saturation=1.5,
                  apply_cartoon=True, apply_bw=True)

