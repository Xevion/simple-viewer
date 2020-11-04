"""
helpers.py

Contains helper functions used as refactored shortcuts or in order to separate code for readability.
"""
from typing import Tuple

import cv2
from PIL import Image


def generate_thumbnail(path: str, output_path: str) -> None:
    """
    Helper function which completes the process of generating thumbnails for both pictures and videos.

    :param path: The absolute path to the file.
    :param output_path: The absolute path to the intended output thumbnail file.
    """
    file = cv2.VideoCapture(path)
    success, image = file.read()
    if success:
        img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        im_pil = Image.fromarray(img)

        # Resize, crop, thumbnail
        im_pil.thumbnail((300, 300))
        # im_pil.crop((0, 0, 200, 66))
        # im_pil.resize((200, 66))

        im_pil.save(output_path)


def get_resolution(path: str) -> Tuple[int, int]:
    """
    Retrieves the resolution of a image or video

    :return: A tuple containing two positive integers representing width and height
    """
    file = cv2.VideoCapture(path)
    return file.get(cv2.CAP_PROP_FRAME_WIDTH), file.get(cv2.CAP_PROP_FRAME_HEIGHT)
