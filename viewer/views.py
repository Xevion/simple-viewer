import os

from django.http import FileResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse

from viewer.helpers import extra_listdir
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
        context = {
            'title': f'Browse - {os.path.dirname(dir.path)}',
            'files': extra_listdir(dir.path),
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


def add(request):
    context = {'title': 'Add New Directory'}
    if 'path' in request.GET.keys():
        context['path_prefill'] = request.GET['path']
    return render(request, 'add.html', context)


def submit_new(request):
    try:
        s = ServedDirectory(
            path=request.POST['path'],
            regex_pattern=request.POST.get('regex'),
            regex=request.POST.get('regex') is not None,
            match_filename=request.POST.get('match_filename', False),
            recursive=request.POST.get('recursive', False)
        )
        if not os.path.isdir(request.POST['path']):
            raise ValueError('A invalid Directory was specified in the request.')
        s.save()
    except KeyError:
        return render(request, 'message.html', status=403,
                      context={'title': 'Invalid Options',
                               'message': 'The POST request you sent did not have the options required to complete '
                                          'the request.'})
    except ValueError:
        return render(request, 'message.html', status=400,
                      context={'title': 'Invalid Directory',
                               'message': 'The directory you specified was not a valid directory, either it doesn\'t '
                                          'exist or it isn\'t a directory.'})
    return HttpResponseRedirect(reverse('browse', args=(s.id,)))
