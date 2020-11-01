import mimetypes
import os
from typing import List, Tuple

from django.urls import reverse

from viewer.models import ServedDirectory


class File:
    def __init__(self, head, tail):
        self.filename = head
        self.fullpath = os.path.join(tail, head)
        self.mediatype = self.get_mediatype()

    def get_url(self, directory: ServedDirectory) -> str:
        return reverse('file', args=(directory.id, self.filename))

    def get_mediatype(self) -> str:
        """Simple media type categorization based on the given mimetype"""
        if os.path.exists(self.fullpath):
            if os.path.isdir(self.fullpath):
                return 'folder'
            mimetype = mimetypes.guess_type(self.filename)[0]
            if mimetype is not None:
                if mimetype.startswith('image'):
                    return 'image'
                elif mimetype.startswith('video'):
                    return 'video'
            return 'file'
        return 'unknown'

    def __str__(self) -> str:
        return self.filename


def extra_listdir(path: str) -> List[File]:
    """
    Helper function used for identifying file media type for every file in a given directory, extending os.listdir

    :param path: The path to the directory.
    :return: A list of tuples, each containing two strings, the file or directory name, and the media type.
    """
    files = []
    for file in os.listdir(path):
        files.append(File(file, path))
    return files


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
