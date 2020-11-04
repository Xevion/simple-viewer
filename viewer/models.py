import mimetypes
import os
import uuid
from datetime import datetime
from typing import Tuple

import humanize
import jsonfield
from django.db import models
from django.urls import reverse
from django.utils import timezone

from viewer import helpers


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
    lastRefreshed = models.DateTimeField(default=timezone.now)
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
        self.save()

    def __str__(self) -> str:
        return self.path


class ImageResolution(models.Model):
    """
    A simple model for storing the dimensions of a specific image. A tuple, in essence.
    """

    x = models.PositiveIntegerField()
    y = models.PositiveIntegerField()

    def set(self, size: Tuple[int, int]) -> None:
        """Sets the X and Y attributes"""
        self.x, self.y = size
        self.save()

    def __str__(self) -> str:
        return f'{self.x} x {self.y}'


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
    lastRefreshed = models.DateTimeField(default=timezone.now)

    fileLastModified = models.DateTimeField(null=True, default=None)
    size = models.PositiveIntegerField(null=True)
    resolution = models.OneToOneField(ImageResolution, on_delete=models.CASCADE, related_name='file', null=True)
    thumbnailResolution = models.OneToOneField(ImageResolution, on_delete=models.CASCADE, related_name='real_file', null=True)

    @classmethod
    def create(cls, full_path: str, parent: ServedDirectory, refresh: bool = True) -> 'File':
        """
        Simple shortcut for creating a File database entry with just the path.
        Refreshes the file after creation.
        """
        file = File(
            path=full_path,
            filename=os.path.basename(full_path),
            mediatype=File.get_mediatype(full_path),
            directory=parent
        )
        if refresh:
            file.refresh()
        return file

    def refresh(self) -> None:
        """Refresh this file's metadata"""
        self.lastRefreshed = timezone.now()

        fileLastModified = datetime.fromtimestamp(os.path.getmtime(self.path))
        updated = fileLastModified != self.fileLastModified
        self.fileLastModified = fileLastModified

        # thumbnail regeneration logic
        if self.mediatype == 'image' or self.mediatype == 'video':
            # if the file modification time changed, regenerate it
            if updated:
                self.generate_thumbnail(regenerate=True)
            # if the thumbnail hasn't been generated, attempt to generate it
            elif not self.thumbnail:
                self.generate_thumbnail()

        if updated:
            self.resolution.set(helpers.get_resolution(self.path))
            self.thumbnailResolution.set(helpers.get_resolution(self.__thumbs_path))
            self.size = os.path.getsize(self.path)

        self.save()

    def get_url(self, directory: ServedDirectory) -> str:
        """Retrieve the direct URL for a given file."""
        return reverse('file', args=(directory.id, self.filename))

    def delete_thumbnail(self) -> None:
        """Delete the thumbnail for this File if it exists and forget the filename."""
        if self.thumbnail:
            try:
                os.remove(self.__thumbs_path)
            except FileNotFoundError:
                pass
            finally:
                self.thumbnail = None
                self.save()

    @property
    def human_size(self) -> str:
        """returns a human readable interpretation of the size of this file"""
        return humanize.naturalsize(self.size)

    @property
    def thumbnail_static_path(self) -> str:
        """Used for accessing the thumbnail via the static URL"""
        return f'/thumbnails/{self.thumbnail}'

    @property
    def __thumbs_dir(self) -> str:
        """A string path to the directory containing thumbnails."""
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'thumbnails')

    @property
    def __thumbs_path(self) -> str:
        """A string path to the thumbnail file."""
        if self.thumbnail:
            return os.path.join(self.__thumbs_dir, self.thumbnail)

    def generate_thumbnail(self, regenerate=False) -> None:
        """
        Generates a new thumbnail for a given image or video file.
        Will not generate thumbnails if the thumbnail already exists.

        :param regenerate: Generate the thumbnail even if the thumbnail already exists.
        """
        #  TODO: Add django-background-task scheduling

        # Only generate again if regenerate is True, make sure to delete old thumbnail file
        if self.thumbnail:
            if not regenerate:
                return
            else:
                self.delete_thumbnail()

        # Name the thumbnail a random UUID and remember it
        thumb_file = f'{uuid.uuid4()}.jpeg'
        self.thumbnail = thumb_file

        # Generate thumbnail
        try:
            helpers.generate_thumbnail(self.path, self.__thumbs_path)
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
