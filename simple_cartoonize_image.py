import cv2
import numpy as np

def kmeans_color_quantization(image, clusters=8):
    """
    Apply K-means clustering to reduce the number of colors in the image.

    Parameters:
    - image: The input image.
    - clusters: Number of clusters (color groups).

    Returns:
    - quantized_image: The color-quantized image.
    """
    # Convert image to 2D array
    data = image.reshape((-1, 3))
    data = np.float32(data)

    # Apply K-means clustering
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
    _, labels, centers = cv2.kmeans(data, clusters, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)

    # Recreate the quantized image
    centers = np.uint8(centers)
    quantized = centers[labels.flatten()]
    quantized_image = quantized.reshape(image.shape)
    return quantized_image

def adjust_gamma(image, gamma=1.0):
    """
    Apply gamma correction to adjust brightness and contrast.

    Parameters:
    - image: Input image.
    - gamma: Gamma value (default=1.0). Lower values darken the image, higher values brighten it.

    Returns:
    - gamma_corrected: Gamma-corrected image.
    """
    inv_gamma = 1.0 / gamma
    table = np.array([(i / 255.0) ** inv_gamma * 255 for i in np.arange(256)]).astype("uint8")
    return cv2.LUT(image, table)

def apply_background_blur(image, edges, blur_strength=15):
    """
    Apply Gaussian blur to the background based on edge detection.
    """
    mask = cv2.bitwise_not(edges)  # Invert edges to create mask
    mask_colored = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)  # Convert mask to 3 channels
    blurred_background = cv2.GaussianBlur(image, (blur_strength, blur_strength), 0)
    blended = np.where(mask_colored == 0, blurred_background, image)
    return blended

def cartoonize_image(image_path, output_path, max_width=1200, max_height=1200):
    img = cv2.imread(image_path)
    if img is None:
        print("Unable to read the image. Please check the path!")
        return

    resized_img = resize_image_proportionally(img, max_width, max_height)
    gamma_corrected = adjust_gamma(resized_img, gamma=1.5)
    gray = cv2.cvtColor(gamma_corrected, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, threshold1=50, threshold2=150)
    # edges = thicken_edges(edges, kernel_size=2)
    color = cv2.bilateralFilter(gamma_corrected, d=9, sigmaColor=120, sigmaSpace=120)
    quantized = kmeans_color_quantization(color, clusters=20)
    blurred_background = apply_background_blur(quantized, edges, blur_strength=21)

    # Invert edges to make them white on black background
    edges_inv = cv2.bitwise_not(edges)
    edges_inv_colored = cv2.cvtColor(edges_inv, cv2.COLOR_GRAY2BGR)

    # Blend the quantized image and the inverted edges
    alpha = 0.8  # Weight for the color image
    beta = 0.2   # Weight for the edges
    cartoon = cv2.addWeighted(blurred_background, alpha, edges_inv_colored, beta, 0)
    # cartoon_sharpened = sharpen_image(cartoon)
    # cartoon = blend_with_original(cartoon, cartoon_sharpened, alpha=0.6)
    # cartoon = normalize_brightness(cartoon)

    cv2.imwrite(output_path, cartoon)
    print(f"Enhanced cartoonized image saved at {output_path}")
    # cv2.imshow("Resized Original Image", resized_img)
    # cv2.imshow("Enhanced Cartoonized Image", cartoon)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

# Helper function: Resize proportionally
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
    cartoonize_image(input_path, output_path)

def thicken_edges(edges, kernel_size=3):
    """
    Thicken the edges using dilation.
    """
    kernel = np.ones((kernel_size, kernel_size), np.uint8)
    thickened_edges = cv2.dilate(edges, kernel, iterations=1)
    return thickened_edges

def sharpen_image(image, strength=1.0):
    """
    Apply a softer sharpening effect to the image.
    
    Parameters:
    - image: Input image.
    - strength: Strength of the sharpening effect (default=1.0). Lower values produce softer sharpening.

    Returns:
    - sharpened: Sharpened image.
    """
    kernel_sharpening = np.array([[0, -1, 0],
                                  [-1, 4 + strength, -1],
                                  [0, -1, 0]])
    sharpened = cv2.filter2D(image, -1, kernel_sharpening)
    return sharpened

def blend_with_original(image, sharpened, alpha=0.7):
    """
    Blend the sharpened image with the original image for softer sharpening.
    
    Parameters:
    - image: Original image.
    - sharpened: Sharpened image.
    - alpha: Weight of the sharpened image (default=0.7).

    Returns:
    - blended: Final blended image.
    """
    blended = cv2.addWeighted(image, 1 - alpha, sharpened, alpha, 0)
    return blended

def normalize_brightness(image):
    """
    Normalize brightness to avoid overexposure.
    
    Parameters:
    - image: Input image.

    Returns:
    - normalized: Brightness-normalized image.
    """
    normalized = cv2.normalize(image, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)
    return normalized