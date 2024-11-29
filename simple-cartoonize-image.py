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
    color = cv2.bilateralFilter(gamma_corrected, d=9, sigmaColor=120, sigmaSpace=120)
    quantized = kmeans_color_quantization(color, clusters=20)

    # Invert edges to make them white on black background
    edges_inv = cv2.bitwise_not(edges)
    edges_inv_colored = cv2.cvtColor(edges_inv, cv2.COLOR_GRAY2BGR)

    # Blend the quantized image and the inverted edges
    alpha = 0.8  # Weight for the color image
    beta = 0.2   # Weight for the edges
    cartoon = cv2.addWeighted(quantized, alpha, edges_inv_colored, beta, 0)

    cv2.imwrite(output_path, cartoon)
    print(f"Enhanced cartoonized image saved at {output_path}")
    cv2.imshow("Resized Original Image", resized_img)
    cv2.imshow("Enhanced Cartoonized Image", cartoon)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

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
