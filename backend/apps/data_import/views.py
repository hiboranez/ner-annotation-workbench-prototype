import os

from django.core.files.storage import default_storage
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def upload_data(request):
    if request.method == "POST" and request.FILES.get('file'):
        file = request.FILES['file']
        file_name = file.name
        file_path = os.path.join('uploads', file_name)

        # Save the file to a location on the server
        with default_storage.open(file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        # You can add more logic here to parse and analyze the uploaded file

        return JsonResponse({"message": f"File {file_name} uploaded successfully"})
    return JsonResponse({"error": "No file provided"}, status=400)
