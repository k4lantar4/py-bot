from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'chat'

router = DefaultRouter()
router.register(r'sessions', views.LiveChatSessionViewSet, basename='chat-session')
router.register(r'messages', views.LiveChatMessageViewSet, basename='chat-message')
router.register(r'operators', views.LiveChatOperatorViewSet, basename='chat-operator')
router.register(r'ratings', views.LiveChatRatingViewSet, basename='chat-rating')

urlpatterns = [
    path('', include(router.urls)),
]

# WebSocket URL patterns are defined in routing.py 