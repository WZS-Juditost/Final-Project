import cv2
import numpy as np

def apply_cartoon_filter(image):

    downsampled = cv2.pyrDown(image)
    for _ in range(3):
        downsampled = cv2.bilateralFilter(downsampled, d=9, sigmaColor=75, sigmaSpace=75)
    upsampled = cv2.pyrUp(downsampled)
    upsampled = cv2.resize(upsampled, (image.shape[1], image.shape[0]))
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.medianBlur(gray, 7)
    edges = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_MEAN_C, 
                                  cv2.THRESH_BINARY, blockSize=9, C=2)

    cartoon = cv2.bitwise_and(upsampled, upsampled, mask=edges)
    
    return cartoon

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


if __name__ == "__main__":

    image = cv2.imread("image/2.jpg")
    image = resize_image_proportionally(image, 1200, 1200)
    cartoon_image = apply_cartoon_filter(image)
    cv2.imshow("Original Image", image)
    cv2.imshow("Cartoon Image", cartoon_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
