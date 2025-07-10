import time
import logging

logger = logging.getLogger("django")

class RequestLogMiddleware:
    """
    Har request/response ka time aur path log karta hai.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()
        response = self.get_response(request)
        duration = time.time() - start_time

        logger.info(f"{request.method} {request.path} completed in {duration:.2f}s")
        return response
