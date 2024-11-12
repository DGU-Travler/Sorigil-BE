from django.http import JsonResponse
from bs4 import BeautifulSoup, Comment
from rest_framework import permissions
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from urllib.parse import unquote




class CleanView(APIView):
    permission_classes = [permissions.AllowAny]
    parser_classes = [FormParser, MultiPartParser]

    origin_html = openapi.Parameter(
        'html_code',
        in_=openapi.IN_FORM,
        type=openapi.TYPE_STRING,
        description='HTML code to clean',
        required=True,
    )

    @swagger_auto_schema(
        operation_description="Removes unwanted tags and comments from provided HTML code",
        manual_parameters=[origin_html],
        responses={
            200: openapi.Response(
                'Cleaned HTML',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'cleaned_html': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description='The cleaned HTML output'
                        )
                    }
                )
            ),
            400: 'No HTML content provided'
        }
    )
    def post(self, request):
        html_code = request.data.get('html_code', '')
        if not html_code:
            return JsonResponse({'error': 'No HTML content provided'}, status=400)

        html_code = unquote(html_code)

        soup = BeautifulSoup(html_code, 'html.parser')
        for tag in soup(['style', 'script', 'head', 'meta', 'noscript', 'iframe']):
            tag.decompose()
        for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
            comment.extract()
        for tag in soup.find_all():
            if not tag.get_text(strip=True):
                tag.decompose()

        cleaned_html = str(soup)
        return JsonResponse({'cleaned_html': cleaned_html})
