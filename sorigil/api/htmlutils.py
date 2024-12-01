from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import FindDivSerializer
from bs4 import BeautifulSoup
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class FindElementsAPIView(APIView):
    @swagger_auto_schema(
        operation_description="HTML 코드와 검색어를 받아 해당 검색어를 포함하는 모든 HTML 요소를 반환합니다.",
        request_body=FindDivSerializer,
        responses={
            200: openapi.Response(
                description="성공적으로 HTML 요소를 찾았습니다.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'elements': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_STRING, description='찾은 HTML 요소의 문자열')
                        )
                    }
                )
            ),
            404: openapi.Response(
                description="검색어를 포함하는 HTML 요소를 찾을 수 없습니다.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING, description='에러 메시지')
                    }
                )
            ),
            400: openapi.Response(
                description="잘못된 입력입니다.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'html_code': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING)),
                        'search_term': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING)),
                    }
                )
            ),
        }
    )
    def post(self, request, format=None):
        serializer = FindDivSerializer(data=request.data)
        if serializer.is_valid():
            html_code = serializer.validated_data['html_code']
            search_term = serializer.validated_data['search_term']

            soup = BeautifulSoup(html_code, 'html.parser')

            # 검색어가 포함된 모든 요소 찾기
            matching_elements = []
            for element in soup.find_all(True):  # 모든 태그 탐색
                if search_term in element.get_text():
                    matching_elements.append(str(element))

            if matching_elements:
                return Response({'elements': matching_elements}, status=status.HTTP_200_OK)
            else:
                return Response({'error': '해당 검색어를 포함하는 HTML 요소를 찾을 수 없습니다.'},
                                status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
