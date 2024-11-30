from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from django.core.files.base import ContentFile
import requests
import os
import base64

# 환경 변수에서 Hugging Face API 토큰 가져오기
API_TOKEN = os.getenv('HUGGING_FACE_API')

# 공통 함수: 이미지 파일을 Base64로 인코딩
def encode_image(file):
    return base64.b64encode(file.read()).decode("utf-8")

# 공통 함수: Hugging Face API 호출
def query_huggingface_api(image_data, model_url):
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    payload = {"inputs": {"image": image_data}}
    
    try:
        response = requests.post(model_url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

# 1. `/content-voice` - 콘텐츠 음성 안내 API
class ContentVoiceAPI(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        file = request.FILES.get('image')
        if not file:
            return Response({"error": "No image file provided."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 이미지 파일 인코딩 및 Hugging Face API 호출
            image_data = encode_image(file)
            result = query_huggingface_api(
                image_data, 
                "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-large"
            )

            if 'error' in result:
                return Response({"error": result['error']}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response({"caption": result}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# 2. `/voice-command` - 음성 명령 처리 API
class VoiceCommandAPI(APIView):
    def post(self, request, *args, **kwargs):
        command = request.data.get('command')
        if not command:
            return Response({"error": "No command provided."}, status=status.HTTP_400_BAD_REQUEST)

        # 명령어 매핑 및 처리
        command_map = {
            "login": "로그인 페이지로 이동",
            "search": "검색 기능 활성화",
            "home": "홈 페이지로 이동"
        }
        response = command_map.get(command.lower(), "Unknown command")
        return Response({"response": response}, status=status.HTTP_200_OK)

# 3. `/dynamic-content-updates` - 동적 콘텐츠 업데이트 감지 API
class DynamicContentUpdatesAPI(APIView):
    def post(self, request, *args, **kwargs):
        # 요청에서 JSON 데이터 가져오기
        content = request.data.get('content')

        if not content:
            return Response({"error": "No content provided."}, status=status.HTTP_400_BAD_REQUEST)

        # 요청된 content 값을 그대로 반환
        return Response({"content": content}, status=status.HTTP_200_OK)

# 4. `/form-labels` - 폼 필드 레이블 생성 API
class FormLabelsAPI(APIView):
    def post(self, request, *args, **kwargs):
        form_fields = request.data.get('form_fields', [])
        if not form_fields:
            return Response({"error": "No form fields provided."}, status=status.HTTP_400_BAD_REQUEST)

        # AI 레이블 생성 (예제)
        generated_labels = {field: f"Label for {field}" for field in form_fields}
        return Response({"labels": generated_labels}, status=status.HTTP_200_OK)

# 5. `/tts-settings` - TTS 설정 API
class TTSSettingsAPI(APIView):
    def post(self, request, *args, **kwargs):
        speed = request.data.get('speed', 'normal')
        volume = request.data.get('volume', 'medium')
        
        # TTS 설정 저장 로직 (예제)
        settings = {"speed": speed, "volume": volume}
        return Response({"settings": settings}, status=status.HTTP_200_OK)

# 6. `/alt-text` - 이미지 대체 텍스트 생성 API
class AltTextAPI(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        file = request.FILES.get('image')
        if not file:
            return Response({"error": "No image file provided."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 이미지 파일 인코딩 및 Hugging Face API 호출
            image_data = encode_image(file)
            result = query_huggingface_api(
                image_data, 
                "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-large"
            )

            if 'error' in result:
                return Response({"error": result['error']}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response({"alt_text": result}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
