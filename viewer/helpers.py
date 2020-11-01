"""
helpers.py

Contains helper functions used as refactored shortcuts or in order to separate code for readability.
"""
import cv2
from PIL import Image


def generate_thumbnail(path: str, output_path: str) -> None:
    """
    Helper function which completes the process of generating thumbnails for both pictures and videos.

    :param path: The absolute path to the file.
    :param output_path: The absolute path to the intended output thumbnail file.
    """
    vidcap = cv2.VideoCapture(path)
    success, image = vidcap.read()
    if success:
        img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        im_pil = Image.fromarray(img)

        # Resize, crop, thumbnail
        im_pil.thumbnail((300, 300))
        # im_pil.crop((0, 0, 200, 66))
        # im_pil.resize((200, 66))

        im_pil.save(output_path)
