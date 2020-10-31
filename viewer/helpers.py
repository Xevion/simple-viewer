def get_mediatype(mimetype: str) -> str:
    """Simple media type categorization based on the given mimetype"""
    if mimetype is not None:
        if mimetype.startswith('image'):
            return 'image'
        elif mimetype.startswith('video'):
            return 'video'
    return 'file'
