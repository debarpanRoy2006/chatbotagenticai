"""
URL configuration for agent_ai_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
# BACKEND/agent_ai_project/agent_ai_project/urls.py

import os
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.http import HttpResponse
from agent_app import views  # Import views from your app


def serve_react_app(request):
    """
    Serves the React SPA's index.html for the root URL.
    Falls back to the legacy Django template if the React build
    has not been compiled yet.
    """
    frontend_build_dir = getattr(settings, 'FRONTEND_BUILD_DIR', '')
    index_path = os.path.join(frontend_build_dir, 'index.html')

    if os.path.isfile(index_path):
        with open(index_path, 'r', encoding='utf-8') as f:
            return HttpResponse(f.read(), content_type='text/html; charset=utf-8')

    # Fallback: serve the legacy Django template
    return views.home_view(request)


urlpatterns = [
    path('', serve_react_app, name='home'),
    path('admin/', admin.site.urls),
    path('api/', include('agent_app.urls')),
]
