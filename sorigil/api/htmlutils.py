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
                print(len(content))
                try:
                    system_prompt = """
                    너는 제공된 html 코드를 간결하고 이해하기 쉽게 바꿔주는 역할을 수행해.
                    각 라인에는 'www.' 또는 'https:'가 포함되어 있으며, 이 라인과 그 전후 라인이 있어
                    이걸 통해서 해당 링크가 어떤 내용을 담고 있는지 알 수 있어야 해.
                    링크와 그에 해당하는 정보를 남겨줘. 모든 링크에 대해 해줘야해
                    형식은 ex) "https://www.google.com" - "구글" 이런식으로 제공해줘.
                    """
                    messages = [{"role": "system", "content": system_prompt.strip()},
                                {"role": "user", "content": content.strip()}]
                    get_response = openai.ChatCompletion.create(
                        model="gpt-4o-mini",  # 사용하려는 모델 이름
                        messages=messages
                    )
                    PostProcessing_html = get_response.choices[0].message.content.strip()
                except Exception as e:
                    PostProcessing_html = f"GPT-4 API 호출 실패:{str(e)}"
                
                return Response({'processed_html': PostProcessing_html}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
