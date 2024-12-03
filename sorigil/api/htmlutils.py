# api/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import HTMLFileSerializer
import re
import openai
import os
from dotenv import load_dotenv
class ProcessHTMLView(APIView):
    """
    HTML 파일을 처리하여 'www.' 또는 'https:'가 포함된 라인과 그 전후 라인을 남기고,
    남은 HTML에서 [, ], \ 문자를 제거합니다.
    """

    def post(self, request, format=None):
        serializer = HTMLFileSerializer(data=request.data)
        if serializer.is_valid():
            html_file = serializer.validated_data['html_file']
            search_term = serializer.validated_data['search_term']
            try:
                # 파일을 문자열로 읽기
                content = html_file.read().decode('utf-8')
                lines = content.splitlines()
                total_lines = len(lines)
                '''
                # 'www.' 또는 'https:' 패턴
                pattern = re.compile(r'(www\.|https?:)', re.IGNORECASE)

                # 링크가 있는 라인 번호 저장
                link_line_indices = set()
                for idx, line in enumerate(lines):
                    if pattern.search(line):
                        link_line_indices.add(idx)

                # 남겨야 할 라인 번호 계산 (링크 라인과 그 전후 라인)
                keep_line_indices = set()
                for idx in link_line_indices:
                    keep_line_indices.add(idx)
                    if idx - 1 >= 0:
                        keep_line_indices.add(idx - 1)
                    if idx + 1 < total_lines:
                        keep_line_indices.add(idx + 1)

                # 남겨진 라인들을 모아서 새로운 HTML 생성
                kept_lines = [lines[idx] for idx in sorted(keep_line_indices)]

                # [, ], \ 문자 제거
                cleaned_lines = [re.sub(r'[\[\]\\]', '', line) for line in kept_lines]
                processed_html = '\n'.join(cleaned_lines)

                '''
                load_dotenv()
                openai.api_key = os.getenv("GPT_API")
                try:
                    system_prompt = f"""
                    Find all HTML elements related to the term "{search_term}". Include elements that:
                    - Contain "{search_term}" in their inner text.
                    - Have an attribute (like `id`, `class`, `name`, or `data-*`) that includes "{search_term}".
                    Return the tag name, attributes, and inner text for each matching element.
                    'https://www. 와 같이 링크가 포함된 라인은 특히 중요합니다.'
                    코멘트는 따로 달지 마세요. 호출한 것만 해주면 됩니다.
                    """
                    messages = [{"role": "system", "content": system_prompt.strip()},
                                {"role": "user", "content": content.strip()}]
                    get_response = openai.ChatCompletion.create(
                        model="gpt-4o-mini",  # 사용하려는 모델 이름
                        messages=messages
                    )
                    processed_data = get_response.choices[0].message.content.strip()
                except Exception as e:
                    processed_data = f"GPT-4 API 호출 실패:{str(e)}"
                
                return Response({'processed_data': processed_data}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
