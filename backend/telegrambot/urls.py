from django.urls import path
from . import views

app_name = 'telegrambot'

urlpatterns = [
    path('webhook/', views.telegram_webhook, name='webhook'),
    path('send-message/', views.send_message, name='send_message'),
    path('broadcast/', views.broadcast_message, name='broadcast'),
] 