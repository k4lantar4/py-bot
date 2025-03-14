from django.contrib import admin
from django.urls import path
from django.utils.html import format_html
from django.urls import reverse

# Customize admin site
admin.site.site_header = 'MRJBot Administration'
admin.site.site_title = 'MRJBot Admin'
admin.site.index_title = 'Welcome to MRJBot Administration'

# Add monitoring link to admin index
class MRJBotAdminSite(admin.AdminSite):
    """Customized admin site for MRJBot"""
    
    def get_urls(self):
        urls = super().get_urls()
        # Add your custom URLs here
        return urls
    
    def index(self, request, extra_context=None):
        """Add monitoring dashboard link to admin index page"""
        extra_context = extra_context or {}
        extra_context['monitoring_url'] = reverse('monitoring_dashboard')
        return super().index(request, extra_context)
        
# Register the custom admin site
admin_site = MRJBotAdminSite(name='mrjbot_admin')
admin.site = admin_site 