import re
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin

class CSRFExemptMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Check if the request path matches any CSRF exempt patterns
        for pattern in getattr(settings, 'CSRF_EXEMPT_URLS', []):
            if re.match(pattern, request.path):
                setattr(request, '_dont_enforce_csrf_checks', True)
                break
        return None
