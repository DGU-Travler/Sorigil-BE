from rest_framework import serializers
from bs4 import BeautifulSoup


class CaptioningSerializer(serializers.Serializer):
    api_caption = serializers.CharField()

class ErrorSerializer(serializers.Serializer):
    error = serializers.CharField()

class HTMLFileSerializer(serializers.Serializer):
    html_file = serializers.FileField()