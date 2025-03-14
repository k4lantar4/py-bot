from django.urls import path, include
from . import views
from . import api

urlpatterns = [
    # Add a simple URL pattern for now
    path('api/', include('api.urls')),
    
    # Points related URLs
    path('api/points/balance/', api.get_points_balance, name='points_balance'),
    path('api/points/history/', api.get_points_history, name='points_history'),
    path('api/points/rules/', api.get_redemption_rules, name='points_rules'),
    path('api/points/redeem/', api.redeem_points, name='points_redeem'),
] 