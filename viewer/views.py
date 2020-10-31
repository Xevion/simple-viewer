import mimetypes
import os

from django.http import FileResponse
from django.shortcuts import render, get_object_or_404

from viewer.helpers import get_mediatype
from viewer.models import ServedDirectory


def index(request):
    """Index view for the simple-viewer project."""
    directories = ServedDirectory.objects.all()
    context = {'title': 'Index',
               'directories': directories}
    return render(request, 'index.html', context)


def browse(request, directory_id):
    dir = get_object_or_404(ServedDirectory, id=directory_id)

    if os.path.isdir(dir.path):
        files = [
            (file, get_mediatype(mimetypes.guess_type(file)[0])) for file in os.listdir(dir.path)
        ]
        context = {
            'title': f'Browse - {os.path.dirname(dir.path)}',
            'files': files,
            'directory': dir
        }
        return render(request, 'browse.html', context)
    else:
        context = {
            'title': 'Invalid Directory',
            'message': 'The path this server directory points to {}.'.format(
                'exists, but is not a directory' if os.path.exists(dir.path) else 'does not exist'
            )
        }
        return render(request, 'message.html', context, status=500)


def file(request, directory_id, file):
    dir = get_object_or_404(ServedDirectory, id=directory_id)
    if os.path.isdir(dir.path):
        path = os.path.join(dir.path, file)
        if os.path.exists(path):
            return FileResponse(open(path, 'rb'))
        else:
            context = {
                'title': 'Invalid File',
                'message': 'The file requested from this directory was not found on the server.'
            }
            return render(request, 'message.html', context, status=500)
    context = {
        'title': 'Invalid Directory',
        'message': 'The path this server directory points to {}.'.format(
            'exists, but is not a directory' if os.path.exists(dir.path) else 'does not exist'
        )
    }
    return render(request, 'message.html', context, status=500)
