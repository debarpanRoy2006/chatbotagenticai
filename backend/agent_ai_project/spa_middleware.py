"""
SPA Fallback Middleware for the Antigravity Runtime.

Serves the React frontend's index.html for any request that:
  1. Is not an API route (/api/...)
  2. Is not an admin route (/admin/...)
  3. Is not a static file (/static/...)
  4. Does not have a file extension (e.g., .js, .css, .png)
  5. Is a GET request

This enables client-side routing (React Router) without producing
Django 404s for frontend-only paths.
"""

import os
import re
from django.conf import settings
from django.http import HttpResponse


class SPAFallbackMiddleware:
    """
    Middleware that catches unresolved GET requests and serves
    the React SPA's index.html so the client-side router can
    take over.
    """

    # Routes that should NEVER be intercepted by the SPA fallback.
    BYPASS_PREFIXES = ('/api/', '/admin/', '/static/')

    # Pattern matching URLs that look like static file requests.
    FILE_EXTENSION_RE = re.compile(r'\.[a-zA-Z0-9]{1,10}$')

    def __init__(self, get_response):
        self.get_response = get_response
        self.index_html_content = None

    def _load_index_html(self):
        """Lazily load the React build's index.html into memory."""
        if self.index_html_content is not None:
            return self.index_html_content

        frontend_build_dir = getattr(settings, 'FRONTEND_BUILD_DIR', None)
        if not frontend_build_dir:
            return None

        index_path = os.path.join(frontend_build_dir, 'index.html')
        if os.path.isfile(index_path):
            with open(index_path, 'r', encoding='utf-8') as f:
                self.index_html_content = f.read()
            return self.index_html_content
        return None

    def __call__(self, request):
        response = self.get_response(request)

        # Only intercept 404 GET requests that aren't API/admin/static.
        if (
            response.status_code == 404
            and request.method == 'GET'
            and not any(request.path.startswith(p) for p in self.BYPASS_PREFIXES)
            and not self.FILE_EXTENSION_RE.search(request.path)
        ):
            html = self._load_index_html()
            if html:
                return HttpResponse(html, content_type='text/html; charset=utf-8')

        return response
