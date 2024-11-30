from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from django.http import HttpResponse
import re
from .serializers import CleanedHTMLSerializer

# 오류 응답을 위한 Serializer 정의
class ErrorSerializer(serializers.Serializer):
    error = serializers.CharField()

class CleanView(APIView):
    permission_classes = []  # 인증 필요 없음
    parser_classes = [MultiPartParser, FormParser]  # 파일 업로드 처리

    # Swagger에서 파일 파라미터 정의
    html_file_param = openapi.Parameter(
        'html_file',
        in_=openapi.IN_FORM,
        type=openapi.TYPE_FILE,
        description='Upload HTML file to clean and process',
        required=True
    )

    @swagger_auto_schema(
        operation_description="Upload an HTML file to clean and process.",
        manual_parameters=[html_file_param],
        responses={
            200: CleanedHTMLSerializer,
            400: openapi.Response('Invalid input or no content found', ErrorSerializer)
        }
    )
    def post(self, request):
        # 파일 받아오기
        html_file = request.FILES.get('html_file', None)

        if not html_file:
            return Response({'error': 'html_file parameter must be provided'}, status=400)

        try:
            # 파일을 읽어 HTML 코드로 변환
            html_code = html_file.read().decode('utf-8')
        except Exception as e:
            return Response({'error': f'Failed to read the uploaded file: {str(e)}'}, status=400)

        # HTML 전처리 (특정 부분 삭제)
        cleaned_html = self.remove_square_brackets(html_code)

        # 텍스트 파일로 응답
        if 'download' in request.query_params:  # 다운로드 요청이 있으면 텍스트 파일로 응답
            response = HttpResponse(
                cleaned_html,
                content_type='text/plain',
            )
            response['Content-Disposition'] = 'attachment; filename="cleaned_html.txt"'
            return response

        return Response({
            'cleaned_html': cleaned_html[:100000],  # cleaned_html의 크기를 100KB로 제한
        })

    def remove_square_brackets(self, html_code):
        # 정규 표현식을 사용해 대괄호 [] 안의 내용 제거
        cleaned_html = re.sub(r'\[.*?\]', '', html_code)
        return cleaned_html
