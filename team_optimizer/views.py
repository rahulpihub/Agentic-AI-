from django.http import JsonResponse

def test_connection(request):
    return JsonResponse({"message": "React ↔ Django connected successfully!"})
