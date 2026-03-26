from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import cloudinary.uploader


@csrf_exempt
def single_upload(request):
    if request.method == "POST":
        file = request.FILES.get("file")

        if not file:
            return JsonResponse(
                {"error": "No file provided"},
                status=400
            )

        result = cloudinary.uploader.upload(
            file,
            resource_type="auto"
        )

        return JsonResponse({
            "message": "Single upload successful",
            "file": {
                "url": result.get("secure_url"),
                "public_id": result.get("public_id"),
                "type": result.get("resource_type")
            }
        })

    return JsonResponse(
        {"error": "Invalid request method"},
        status=405
    )


@csrf_exempt
def multiple_upload(request):
    if request.method == "POST":
        files = request.FILES.getlist("files")

        if not files:
            return JsonResponse(
                {"error": "No files provided"},
                status=400
            )

        uploaded_files = []

        for file in files:
            result = cloudinary.uploader.upload(
                file,
                resource_type="auto"
            )

            uploaded_files.append({
                "url": result.get("secure_url"),
                "public_id": result.get("public_id"),
                "type": result.get("resource_type")
            })

        return JsonResponse({
            "message": "Multiple upload successful",
            "files": uploaded_files
        })

    return JsonResponse(
        {"error": "Invalid request method"},
        status=405
    )

