"""backend URL Configuration"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.authtoken import views as auth_views
from telegrambot.webhook import telegram_webhook

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('api-auth/', include('rest_framework.urls')),
    path('api-token-auth/', auth_views.obtain_auth_token),
    path('webhook/telegram/', telegram_webhook, name='telegram_webhook'),
    path('payments/', include('payments.urls')),
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 