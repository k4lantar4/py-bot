"""
URLs for V2Ray management.

This module contains URL patterns for:
- Server monitoring and health checks
- Traffic usage tracking
- Server management
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'monitoring', views.ServerMonitorViewSet, basename='monitoring')

urlpatterns = [
    path('', include(router.urls)),
] 