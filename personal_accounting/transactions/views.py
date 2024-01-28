from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from .models import Document

def document_download_view(request, document_id):
    document = get_object_or_404(Document, id=document_id)
    file_path = document.file.path
    with open(file_path, 'rb') as file:
        response = HttpResponse(file.read(), content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{document.file.name}"'
        return response
