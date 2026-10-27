import time
import logging
from .mongo import save_request_log

logger = logging.getLogger('website.request_logger')


class RequestLoggingMiddleware:
    """
    Middleware that records HTTP method, path, response status, duration, and IP address.
    Logs to Python standard logger and stores in MongoDB / in-memory analytics log.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.perf_counter()

        # Capture client IP
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0].strip()
        else:
            ip_address = request.META.get('REMOTE_ADDR', '127.0.0.1')

        response = self.get_response(request)

        duration_ms = (time.perf_counter() - start_time) * 1000

        # Don't clutter logs with static file requests
        if not request.path.startswith('/static/'):
            log_line = f"[{request.method}] {request.path} -> {response.status_code} ({duration_ms:.2f}ms) from {ip_address}"
            if response.status_code >= 500:
                logger.error(log_line)
            elif response.status_code >= 400:
                logger.warning(log_line)
            else:
                logger.info(log_line)

            # Persist to Mongo/memory
            try:
                save_request_log(
                    method=request.method,
                    path=request.path,
                    status_code=response.status_code,
                    duration_ms=duration_ms,
                    ip_address=ip_address
                )
            except Exception as e:
                logger.debug(f"Could not persist request log: {e}")

        return response
