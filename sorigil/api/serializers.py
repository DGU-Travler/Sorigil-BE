from rest_framework import serializers

class CleanedHTMLSerializer(serializers.Serializer):
    html_file = serializers.FileField()
class FindDivSerializer(serializers.Serializer):
    html_code = serializers.CharField()
    search_term = serializers.CharField()

class CaptioningSerializer(serializers.Serializer):
    api_caption = serializers.CharField()

class ErrorSerializer(serializers.Serializer):
    error = serializers.CharField()