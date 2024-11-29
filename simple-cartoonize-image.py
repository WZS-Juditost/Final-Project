import cv2
import numpy as np

def cartoonize_image(image_path, output_path):
    # Read the input image
    img = cv2.imread(image_path)
    if img is None:
        print("Unable to read the image. Please check the path!")
        return

    # Resize the image for faster processing
    img = cv2.resize(img, (600, 600))

    # Convert the image to grayscale
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

    # Display the original and cartoonized images
    cv2.imshow("Original Image", img)
    cv2.imshow("Cartoonized Image", cartoon)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# Test the function
if __name__ == "__main__":
    input_path = "input.jpg"  # Replace with the path to your input image
    output_path = "output_cartoon.jpg"
    cartoonize_image(input_path, output_path)
