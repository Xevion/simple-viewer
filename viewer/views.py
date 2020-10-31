from django.shortcuts import render

from django.http import HttpResponse

def index(request):
    """Index view for the simple-viewer project."""
    return HttpResponse('Hello, World.')
