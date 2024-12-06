"""
main.py
-------
Main script to handle user input and invoke image processing functions.

Author: Zesheng Wang
Date: 2024-12-02
"""
from image_filters import *
from image_enhancements import *
from utilities import *

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

    resized_img = resize_image_proportionally(img, max_width, max_height)
    if enhancements:
        resized_img = enhance_image(resized_img, enhancements)
    if filter_type:
        processed_img = apply_filter(resized_img, filter_type, brightness, contrast, saturation)
    else:
        processed_img = resized_img

    cv2.imwrite(output_path, processed_img)
    print(f"Processed image saved at {output_path}")

if __name__ == "__main__":
    input_path = "image/2.jpg"
    output_path_cartoon = "output_cartoon.jpg"

    process_image(
        input_path, output_path_cartoon, filter_type="cartoon",
        brightness=20, contrast=20, saturation=1.5
    )
