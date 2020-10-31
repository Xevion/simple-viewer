import uuid

from django.db import models


class ServedDirectory(models.Model):
    """
    A reference to a specific directory on the host machine for hosting files.

    A regex pattern is stored for filtering files in the directory down to what is intended.
    A recursive option is also stored, in case the user wishes to serve files in directories below the one specified.
    The regex pattern can be turned on or off using the boolean field.
    The regex pattern can be matched against the file path (False), or just the filename (True).
    """

    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, unique=True)
    path = models.CharField('Directory Path', max_length=260)
    recursive = models.BooleanField('Files Are Matched Recursively', default=False)
    regex_pattern = models.CharField('RegEx Matching Pattern', max_length=100, default=None)
    regex = models.BooleanField('Directory RegEx Option', default=False)
    match_filename = models.BooleanField('RegEx Matches Against Filename', default=True)

    def __str__(self):
        return self.path
