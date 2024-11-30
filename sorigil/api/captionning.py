from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from PIL import Image
import easyocr
import numpy as np
import base64
import io
import requests
import os
from dotenv import load_dotenv


class AnalyzeImageView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    @swagger_auto_schema(
        operation_description="이미지 업로드 후 OCR 및 Hugging Face 모델을 통해 분석 결과를 반환합니다.",
        manual_parameters=[
            openapi.Parameter(
                'image',
                openapi.IN_FORM,
                description="업로드할 이미지 파일",
                type=openapi.TYPE_FILE,
                required=True,
            )
        ],
        responses={
            200: openapi.Response(
                description="이미지 분석 결과",
                examples={
                    "application/json": {
                        "ocr_text": "추출된 텍스트",
                        "generated_caption": "생성된 캡션"
                    }
                },
            ),
            400: "이미지가 업로드되지 않았습니다.",
        },
    )
    def post(self, request, *args, **kwargs):
        if 'image' not in request.FILES:
            return Response({"error": "이미지가 업로드되지 않았습니다."}, status=status.HTTP_400_BAD_REQUEST)

        image_file = request.FILES['image']

        # 1. OCR 처리
        reader = easyocr.Reader(['en', 'ko'])
        image = Image.open(image_file).convert('RGB')
        ocr_result = reader.readtext(np.array(image))
        ocr_text = ' '.join([res[1] for res in ocr_result])

        # 2. Hugging Face API 호출
        try:
            load_dotenv()
            api_token = os.getenv("HUGGING_FACE_API")
            API_URL = "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-large"
            headers = {"Authorization": f"Bearer {api_token}"}

            # Base64로 인코딩
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            image_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

            payload = {
                "inputs": {
                    "image": image_base64
                }
            }

            response = requests.post(API_URL, headers=headers, json=payload)
            if response.status_code == 200:
                generated_caption = response.json()[0].get("generated_text", "캡션 생성 실패")
            else:
                generated_caption = f"Hugging Face API 오류: {response.text}"

        except Exception as e:
            generated_caption = f"Hugging Face API 호출 실패: {str(e)}"

        # 결과 반환
        return Response({
            "ocr_text": ocr_text,
            "generated_caption": generated_caption
        }, status=status.HTTP_200_OK)