import mimetypes
import os
import uuid
from datetime import datetime

import jsonfield
from django.db import models
from django.urls import reverse
from easy_thumbnails.alias import aliases

from viewer import helpers

if not aliases.get('small'):
    aliases.set('small', {'size': (150, 80), 'crop': True})


class ServedDirectory(models.Model):
    """
    A reference to a specific directory on the host machine for hosting files.

    A regex pattern is stored for filtering files in the directory down to what is intended.
    A recursive option is also stored, in case the user wishes to serve files in directories below the one specified.
    The regex pattern can be turned on or off using the boolean field.
    The regex pattern can be matched against the file path (False), or just the filename (True).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    path = models.CharField('Directory Path', max_length=260)

    recursive = models.BooleanField('Files Are Matched Recursively', default=False)
    regex_pattern = models.CharField('RegEx Matching Pattern', max_length=100, default='')
    regex = models.BooleanField('Directory RegEx Option', default=False)
    match_filename = models.BooleanField('RegEx Matches Against Filename', default=True)
    known_subdirectories = jsonfield.JSONField('Tracked Subdirectories JSON', default=[])

    lastModified = models.DateTimeField(auto_now=True)
    lastRefreshed = models.DateTimeField()
    initialCreation = models.DateTimeField(auto_now_add=True)

    def refresh(self):
        """Refresh the directory listing to see if any new files have appeared and add them to the list."""
        # TODO: Implement separate recursive file matching implementation
        # TODO: Implement RegEx filtering step
        directories = []
        filenames = os.listdir(self.path)

        for i, filename in enumerate(filenames):
            file_path = os.path.join(self.path, filename)

            if os.path.isfile(file_path):
                # Check if the file has been entered before
                file: File
                file = self.files.filter(filename__exact=filename).first()

                if file is None:
                    # create the file entry
                    file = File.create(full_path=file_path, parent=self)
                    file.save()
                else:
                    file.refresh()
            else:
                # directory found, remember it
                directories.append(file_path)

        # Dump subdirectories found
        self.known_subdirectories = directories

    def __str__(self):
        return self.path


class ImageDimensions(models.Model):
    """
    A simple model for storing the dimensions of a specific image. A tuple, in essence.
    """

    x = models.PositiveIntegerField()
    y = models.PositiveIntegerField()


class File(models.Model):
    """
    A File object of course represents a singular File inside the directory.
    This table stores all the required metadata and paths to ensure
    """

    path = models.CharField('Full Filepath', max_length=300)
    filename = models.CharField('Filename', max_length=160)
    mediatype = models.CharField('Mediatype', max_length=30)
    directory = models.ForeignKey(ServedDirectory, on_delete=models.CASCADE, related_name='files')
    thumbnail = models.CharField('Thumbnail Filename', max_length=160, null=True, default=None)

    lastModified = models.DateTimeField(auto_now=True)
    initialCreation = models.DateTimeField(auto_now_add=True)

    fileLastModified = models.DateTimeField()
    lastRefreshed = models.DateTimeField()
    size = models.OneToOneField(ImageDimensions, on_delete=models.CASCADE)
    thumbnailSize = models.OneToOneField(ImageDimensions, on_delete=models.CASCADE)

    @classmethod
    def create(cls, full_path: str, parent: ServedDirectory) -> 'File':
        """Simple shortcut for creating a File database entry with just the path."""
        return File(
            path=full_path,
            filename=os.path.basename(full_path),
            mediatype=File.get_mediatype(full_path),
            directory=parent
        )

    def refresh(self) -> None:
        """Refresh this file's metadata"""

        if not self.thumbnail:
            self.generate_thumbnail()

        # Check the fileLastModified
        fileLastModified = datetime.fromtimestamp(os.path.getmtime(self.path))
        if fileLastModified != self.fileLastModified:
            self.generate_thumbnail()

    def get_url(self, directory: ServedDirectory) -> str:
        """Retrieve the direct URL for a given file."""
        return reverse('file', args=(directory.id, self.filename))

    def delete_thumbnail(self) -> None:
        if self.thumbnail:
            try:
                os.remove(os.path.join(self.thumbs_dir, self.thumbnail))
                self.thumbnail = None
                self.save()
            except FileNotFoundError:
                pass

    @property
    def thumbnail_static_path(self):
        """Used for accessing the thumbnail via the static URL"""
        return f'/thumbnails/{self.thumbnail}'

    @property
    def thumbs_dir(self):
        """A string path to the directory containing thumbnails."""
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'thumbnails')

    def generate_thumbnail(self, regenerate=False) -> None:
        #  TODO: Add django-background-task scheduling

        self.delete_thumbnail()

        thumb_file = f'{uuid.uuid4()}.jpeg'
        self.thumbnail = thumb_file

        # Generate thumbnail
        try:
            helpers.generate_thumbnail(self.path, os.path.join(self.thumbs_dir, self.thumbnail))
        except Exception:
            print(f'Could not thumbnail: {self.filename}')
            self.delete_thumbnail()

        self.save()

    @staticmethod
    def get_mediatype(path) -> str:
        """Simple media type categorization based on the given path."""
        if os.path.exists(path):
            if os.path.isdir(path):
                return 'folder'
            mimetype = mimetypes.guess_type(path)[0]
            if mimetype is not None:
                if mimetype.startswith('image'):
                    return 'image'
                elif mimetype.startswith('video'):
                    return 'video'
            return 'file'
        return 'unknown'

    def __str__(self) -> str:
        return self.filename
