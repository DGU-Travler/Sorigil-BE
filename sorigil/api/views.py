import requests
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from urllib.parse import unquote

@csrf_exempt
def proxy_image(request):
    image_url = unquote(request.GET.get('url'))
    response = requests.get(image_url, stream=True)
    return HttpResponse(response.content, content_type=response.headers['Content-Type'])