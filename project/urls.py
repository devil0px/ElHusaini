"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('password_change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
    
    # Web URLs
    path('profile/', include('accounts.urls', namespace='web_accounts')),
    path('projects/', include('projects.urls', namespace='web_projects')),
    path('hr/', include('hr.urls', namespace='web_hr')),
    path('contracts/', include('contracts.urls', namespace='web_contracts')),
    path('inventory/', include('inventory.urls', namespace='web_inventory')),
    path('clients/', include('clients.urls', namespace='web_clients')),
    path('reports/', include('reports.urls', namespace='web_reports')),
    
    # API URLs
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/accounts/', include('accounts.urls', namespace='api_accounts')),
    path('api/projects/', include('projects.urls', namespace='api_projects')),
    path('api/hr/', include('hr.urls', namespace='api_hr')),
    path('api/contracts/', include('contracts.urls', namespace='api_contracts')),
    path('api/inventory/', include('inventory.urls', namespace='api_inventory')),
    path('api/clients/', include('clients.urls', namespace='api_clients')),
    path('api/reports/', include('reports.urls', namespace='api_reports')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
