from pathlib import Path
import os
import logging
import requests
from PIL import Image
import base64
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from .serializers import CaptioningSerializer, ErrorSerializer

# Initialize logger
logger = logging.getLogger(__name__)

# Load environment variables
BASE_DIR = Path(__file__).resolve().parent.parent
API_TOKEN = os.getenv("HUGGING_FACE_API")

# 이미지 파일을 Base64로 변환하는 함수
def encode_image(file):
    return base64.b64encode(file.read()).decode("utf-8")

# Hugging Face API 호출 함수
def query_huggingface_api(file):
    API_URL = "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-large"
    headers = {"Authorization": f"Bearer {API_TOKEN}"}

    # 업로드된 파일을 Base64로 변환
    image_data = encode_image(file)

    # API 요청 데이터
    payload = {
        "inputs": {
            "image": image_data
        }
    }

    try:
        # Hugging Face API 호출
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()  # 상태 코드 확인
        result = response.json()
        print(result)

        # API 응답 데이터 확인
        if isinstance(result, list) and 'generated_text' in result[0]:
            return result[0]['generated_text']
        elif 'error' in result:
            logger.error(f"Hugging Face API error: {result['error']}")
            return {"error": result['error']}
        else:
            logger.error("Unexpected response format from Hugging Face API.")
            return {"error": "Unexpected response format from Hugging Face API."}
    except requests.exceptions.RequestException as e:
        logger.error(f"Request to Hugging Face API failed: {e}")
        return {"error": str(e)}
    except Exception as e:
        logger.exception("Unexpected error during Hugging Face API request.")
        return {"error": "Unexpected error during Hugging Face API request."}

# Django REST Framework API View
class CaptioningAPIView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    @swagger_auto_schema(
        operation_description="Generate caption for the uploaded image",
        manual_parameters=[
            openapi.Parameter(
                'image', openapi.IN_FORM, description="Upload image file",
                type=openapi.TYPE_FILE, required=True
            )
        ],
        responses={
            200: CaptioningSerializer,
            400: openapi.Response("Bad Request", ErrorSerializer),
            500: openapi.Response("Internal Server Error", ErrorSerializer)
        }
    )
    def post(self, request, *args, **kwargs):
        try:
            # 업로드된 파일 가져오기
            file = request.FILES.get('image')
            if not file:
                logger.warning("No image file provided in the request.")
                return Response({"error": "No image file provided."}, status=400)
            
            try:
                # PIL로 이미지 유효성 확인
                Image.open(file).convert('RGB')
            except Exception as e:
                logger.error(f"Image processing error: {e}")
                return Response({"error": "Invalid image file."}, status=400)

            # Hugging Face API 호출
            api_caption = query_huggingface_api(file)

            if isinstance(api_caption, dict) and 'error' in api_caption:
                logger.error(f"Hugging Face API returned an error: {api_caption['error']}")
                return Response({"error": api_caption['error']}, status=500)

            # 결과 반환
            return Response({
                "api_caption": api_caption
            }, status=200)
        except Exception as e:
            logger.exception("Unexpected error in CaptioningAPIView.")
            return Response({"error": "Internal Server Error"}, status=500)
