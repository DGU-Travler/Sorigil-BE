from django.urls import path
from .captionning import AnalyzeImageView
from .htmlutils import FindElementsAPIView
from .api import ContentVoiceAPI, VoiceCommandAPI, DynamicContentUpdatesAPI, FormLabelsAPI, TTSSettingsAPI, AltTextAPI
app_name = 'api'

urlpatterns = [
    path('find/', FindElementsAPIView.as_view(), name='clean-html'),
    path('analyze/', AnalyzeImageView.as_view(), name='analyze'),
    path('content-voice/', ContentVoiceAPI.as_view(), name='content-voice'),
    path('voice-command/', VoiceCommandAPI.as_view(), name='voice-command'),
    path('dynamic-content-updates/', DynamicContentUpdatesAPI.as_view(), name='dynamic-content-updates'),
    path('form-labels/', FormLabelsAPI.as_view(), name='form-labels'),
    path('tts-settings/', TTSSettingsAPI.as_view(), name='tts-settings'),
    path('alt-text/', AltTextAPI.as_view(), name='alt-text'),
]