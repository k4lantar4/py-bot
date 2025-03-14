from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'notifications', views.NotificationViewSet, basename='notification')
router.register(r'settings', views.SettingViewSet, basename='setting')
router.register(r'user-settings', views.UserSettingViewSet, basename='user_setting')

urlpatterns = [
    # Notification management
    path('', include(router.urls)),
    
    # Notification actions
    path('notifications/<int:pk>/read/', views.NotificationReadView.as_view(), name='notification_read'),
    path('notifications/<int:pk>/unread/', views.NotificationUnreadView.as_view(), name='notification_unread'),
    path('notifications/<int:pk>/delete/', views.NotificationDeleteView.as_view(), name='notification_delete'),
    
    # Bulk notification actions
    path('notifications/read-all/', views.NotificationReadAllView.as_view(), name='notification_read_all'),
    path('notifications/delete-all/', views.NotificationDeleteAllView.as_view(), name='notification_delete_all'),
    
    # Notification preferences
    path('preferences/', views.NotificationPreferencesView.as_view(), name='notification_preferences'),
    path('preferences/update/', views.NotificationPreferencesUpdateView.as_view(), name='notification_preferences_update'),
    
    # Notification templates
    path('templates/', views.NotificationTemplateListView.as_view(), name='notification_templates'),
    path('templates/<int:pk>/', views.NotificationTemplateDetailView.as_view(), name='notification_template_detail'),
    path('templates/<int:pk>/preview/', views.NotificationTemplatePreviewView.as_view(), name='notification_template_preview'),
    
    # Notification channels
    path('channels/', views.NotificationChannelListView.as_view(), name='notification_channels'),
    path('channels/<str:channel>/test/', views.NotificationChannelTestView.as_view(), name='notification_channel_test'),
    
    # Notification history
    path('history/', views.NotificationHistoryView.as_view(), name='notification_history'),
    path('history/export/', views.NotificationHistoryExportView.as_view(), name='notification_history_export'),
] 