from .image_filters import *
from .image_enhancements import *
from .utilities import *

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