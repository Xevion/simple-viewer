import os
from typing import Tuple, List


def extra_listdir(path: str) -> List[Tuple[str, str]]:
    """
    Helper function used for identifying file media type for every file in a given directory, extending os.listdir

    :param path: The path to the directory.
    :return: A list of tuples, each containing two strings, the file or directory name, and the media type.
    """
    return [(file, get_all_mediatype(file, path)) for file in os.listdir(path)]


def get_all_mediatype(head: str, tail: str) -> str:
    """
    A extra media type function supporting directories on top of files.

    :param head: The head of the path, usually the directory name or filename at the very end.
    :param tail: The rest of the path, everything that comes before the head.
    :return: A media type in string form.
    """
    if os.path.isfile(os.path.join(tail, head)):
        return get_file_mediatype(head)
    return "folder"


def get_file_mediatype(mimetype: str) -> str:
    """Simple media type categorization based on the given mimetype"""
    if mimetype is not None:
        if mimetype.startswith('image'):
            return 'image'
        elif mimetype.startswith('video'):
            return 'video'
    return 'file'
