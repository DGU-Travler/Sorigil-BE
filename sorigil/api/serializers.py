from rest_framework import serializers

class CleanedHTMLSerializer(serializers.Serializer):
    html_file = serializers.FileField()

class CaptioningSerializer(serializers.Serializer):
    api_caption = serializers.CharField()

class ErrorSerializer(serializers.Serializer):
    error = serializers.CharField()