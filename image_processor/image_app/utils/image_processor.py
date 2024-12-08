from .image_filters import *
from .image_enhancements import *
from .utilities import *


def process_image(image_path, output_path, max_width=1200, max_height=1200,
                  brightness=0, contrast=0, saturation=1.0,
                  enhancements=None, filter_type=None):
    """
    Process the image with resizing, enhancements, and filter application.

    Args:
        image_path (str): Path to the input image file.
        output_path (str): Path to save the processed image.
        max_width (int): Maximum width for resizing the image.
        max_height (int): Maximum height for resizing the image.
        brightness (int): Brightness adjustment level. Defaults to 0.
        contrast (int): Contrast adjustment level. Defaults to 0.
        saturation (float): Saturation adjustment scale. Defaults to 1.0.
        enhancements (list of str): List of enhancements to apply.
        filter_type (str): Type of filter to apply.

    Returns:
        None: Saves the processed image to the specified output path.
    """
    img = cv2.imread(image_path)
    if img is None:
        print("Unable to read the image. Please check the path!")
        return

    # Resize the image
    resized_img = resize_image_proportionally(img, max_width, max_height)
    if enhancements:
        resized_img = enhance_image(resized_img, enhancements)
    if filter_type:
        processed_img = apply_filter(
            resized_img,
            filter_type,
            brightness,
            contrast,
            saturation)
    else:
        processed_img = resized_img

    # Save the processed image
    cv2.imwrite(output_path, processed_img)
    print(f"Processed image saved at {output_path}")
