import cv2

def resize_image_proportionally(image, max_width, max_height):
    """
    Resize the image proportionally to fit within max_width and max_height.

    Parameters:
    - image: The original image (numpy array).
    - max_width: The maximum allowed width.
    - max_height: The maximum allowed height.

    Returns:
    - resized_image: The resized image (numpy array).
    """
    # Get original dimensions
    original_height, original_width = image.shape[:2]

    # Calculate the aspect ratio
    aspect_ratio = original_width / original_height

    # Determine new dimensions
    if original_width > original_height:
        # Landscape orientation
        new_width = min(original_width, max_width)
        new_height = int(new_width / aspect_ratio)
    else:
        # Portrait orientation or square
        new_height = min(original_height, max_height)
        new_width = int(new_height * aspect_ratio)

    # Ensure dimensions fit within the max limits
    if new_width > max_width:
        new_width = max_width
        new_height = int(new_width / aspect_ratio)
    if new_height > max_height:
        new_height = max_height
        new_width = int(new_height * aspect_ratio)

    # Resize the image
    resized_image = cv2.resize(image, (new_width, new_height))

    return resized_image

# Test the function in the cartoonization pipeline
def cartoonize_image(image_path, output_path, max_width=1200, max_height=1200):
    # Read the input image
    img = cv2.imread(image_path)
    if img is None:
        print("Unable to read the image. Please check the path!")
        return

    # Resize the image proportionally for display
    resized_img = resize_image_proportionally(img, max_width, max_height)

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Use adaptive thresholding to detect edges
    edges = cv2.adaptiveThreshold(
        blurred, 255,
        cv2.ADAPTIVE_THRESH_MEAN_C,
        cv2.THRESH_BINARY,
        blockSize=9,
        C=2
    )

    # Apply bilateral filter to smooth colors while keeping edges sharp
    color = cv2.bilateralFilter(img, d=9, sigmaColor=75, sigmaSpace=75)

    # Combine the edges and the color image
    cartoon = cv2.bitwise_and(color, color, mask=edges)

    # Save the cartoonized image
    cv2.imwrite(output_path, cartoon)
    print(f"Cartoonized image saved at {output_path}")

    # Display the resized image and the cartoonized image
    resized_cartoon = resize_image_proportionally(cartoon, max_width, max_height)
    cv2.imshow("Resized Original Image", resized_img)
    cv2.imshow("Resized Cartoonized Image", resized_cartoon)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# Test the updated function
if __name__ == "__main__":
    input_path = "image/2.jpg"  # Replace with your input image path
    output_path = "output_cartoon.jpg"
    cartoonize_image(input_path, output_path)
