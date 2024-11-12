from django.urls import path
from .views import TestView
from .html import CleanView

urlpatterns = [
    path('test/', TestView.as_view(), name='test'),
    path('clean/', CleanView.as_view(), name='clean-html'),
    path('clean/<str:html>', CleanView.as_view(), name='clean-html'),
]