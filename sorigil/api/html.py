import requests
from bs4 import BeautifulSoup, Comment
from django.http import JsonResponse, HttpResponseRedirect
from rest_framework.views import APIView
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework import permissions
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.http import HttpResponse

class CleanView(APIView):
    permission_classes = [permissions.AllowAny]
    parser_classes = [FormParser, MultiPartParser]

    html_param = openapi.Parameter(
        'html_code',
        in_=openapi.IN_FORM,
        type=openapi.TYPE_STRING,
        description='Raw HTML code to clean and process',
        required=False,
    )
    file_param = openapi.Parameter(
        'html_file',
        in_=openapi.IN_FORM,
        type=openapi.TYPE_FILE,
        description='HTML file to clean and process',
        required=False,
    )

    @swagger_auto_schema(
        operation_description="Cleans and processes raw HTML provided in the body or as a file.",
        manual_parameters=[html_param, file_param],
        responses={
            200: openapi.Response(
                'Processed HTML',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'cleaned_html': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description='The cleaned HTML output'
                        ),
                        'filtered_html': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description='The filtered HTML output with core content'
                        )
                    }
                )
            ),
            400: 'Invalid input or no content found'
        }
    )
    def post(self, request):
        html_code = request.data.get('html_code', None)
        html_file = request.FILES.get('html_file', None)

        if not html_code and not html_file:
            return JsonResponse({'error': 'Either html_code or html_file must be provided'}, status=400)

        if html_file:
            try:
                html_code = html_file.read().decode('utf-8')
            except Exception as e:
                return JsonResponse({'error': f'Failed to read the uploaded file: {str(e)}'}, status=400)

        # BeautifulSoup으로 HTML 파싱
        soup = BeautifulSoup(html_code, 'html.parser')

        # 불필요한 태그 및 광고 제거
        for tag in soup(['style', 'script', 'head', 'meta', 'noscript', 'iframe', 'footer', 'aside']):
            tag.decompose()
        for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
            comment.extract()

        # 광고와 관련된 태그 제거 (class나 id 속성 기반)
        for ad_tag in soup.find_all(attrs={'class': lambda x: x and 'ad' in x.lower()}):
            ad_tag.decompose()
        for ad_tag in soup.find_all(attrs={'id': lambda x: x and 'ad' in x.lower()}):
            ad_tag.decompose()

        # 태그만 제거하고 내부 내용은 유지 (a, img 제외)
        for tag in soup.find_all():
            if tag.name not in ['img', 'a']:
                tag.unwrap()

        # 정제된 HTML 저장 (cleaned_html)
        cleaned_html = soup.prettify(formatter="html")

        # 핵심 콘텐츠 자동 필터링
        filtered_elements = []
        for tag in soup.find_all(['h1', 'h2', 'h3', 'p', 'img']):  # 제목, 본문, 이미지 필터링
            parent_html = tag.find_parent().prettify() if tag.find_parent() else tag.prettify()
            if parent_html not in filtered_elements:
                filtered_elements.append(parent_html)

        # 필터링된 요소들을 합쳐서 반환
        filtered_html = "\n".join(filtered_elements) if filtered_elements else "No matching elements found."


        return JsonResponse({
            'cleaned_html': cleaned_html[:100000],  # cleaned_html의 크기를 100KB로 제한
            'filtered_html': filtered_html[:100000]  # filtered_html의 크기를 100KB로 제한
        })
