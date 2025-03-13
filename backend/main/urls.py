from django.urls import path, include
from . import views

urlpatterns = [
    # Add a simple URL pattern for now
    path('api/', include('api.urls')),
] 