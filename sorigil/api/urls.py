from django.urls import path
from .html import CleanView

urlpatterns = [
    path('clean/', CleanView.as_view(), name='clean-html'),
]