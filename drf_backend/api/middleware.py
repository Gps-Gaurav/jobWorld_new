from django.utils.deprecation import MiddlewareMixin

class RequestLoggingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        print("Request Path:", request.path)