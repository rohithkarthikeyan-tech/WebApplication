import os
import time
import logging
import requests

logger = logging.getLogger('website.services')

DEFAULT_FALLBACK_INSIGHTS = [
    {
        'quote': 'Simplicity is prerequisite for reliability.',
        'author': 'Edsger W. Dijkstra',
        'domain': 'Software Engineering'
    },
    {
        'quote': 'First, solve the problem. Then, write the code.',
        'author': 'John Johnson',
        'domain': 'Computer Science'
    },
    {
        'quote': 'Errors should never pass silently. Unless explicitly silenced.',
        'author': 'Tim Peters, The Zen of Python',
        'domain': 'Python Philosophy'
    },
    {
        'quote': 'Optimization without telemetry is premature speculation.',
        'author': 'Aether Systems Architecture',
        'domain': 'Resilience Engineering'
    }
]


def fetch_external_telemetry(timeout=None):
    """
    Fetches daily tech telemetry/quote from a third-party public API with a strict timeout.
    If the API times out, fails, or network is down, seamlessly returns a resilient fallback.
    """
    api_url = os.environ.get('EXTERNAL_INSIGHT_API_URL', 'https://dummyjson.com/quotes/random')
    if timeout is None:
        try:
            timeout = float(os.environ.get('EXTERNAL_API_TIMEOUT', 2.0))
        except ValueError:
            timeout = 2.0

    start_time = time.perf_counter()

    try:
        response = requests.get(
            api_url,
            timeout=timeout,
            headers={'User-Agent': 'Aether-Django-Platform/1.0'}
        )
        latency_ms = (time.perf_counter() - start_time) * 1000

        if response.status_code == 200:
            data = response.json()
            # Extract quote & author depending on endpoint format
            quote = data.get('quote') or data.get('content') or data.get('text') or str(data)
            author = data.get('author') or 'External Telemetry Service'

            return {
                'status': 'online',
                'source': 'third_party_api',
                'endpoint': api_url,
                'latency_ms': round(latency_ms, 2),
                'timeout_threshold_seconds': timeout,
                'data': {
                    'quote': quote,
                    'author': author,
                    'domain': 'External Cloud Telemetry'
                }
            }
        else:
            raise requests.RequestException(f"Upstream returned HTTP {response.status_code}")

    except requests.Timeout as e:
        latency_ms = (time.perf_counter() - start_time) * 1000
        logger.warning(f"Third-party API exceeded timeout of {timeout}s: {e}")
        # Return fallback with timeout indication
        import random
        fallback = random.choice(DEFAULT_FALLBACK_INSIGHTS)
        return {
            'status': 'fallback',
            'source': 'offline_resilient_fallback',
            'endpoint': api_url,
            'latency_ms': round(latency_ms, 2),
            'timeout_threshold_seconds': timeout,
            'reason': f"Request timed out after {timeout} seconds",
            'data': fallback
        }

    except Exception as e:
        latency_ms = (time.perf_counter() - start_time) * 1000
        logger.info(f"Third-party API unreachable ({e}). Engaging local fallback.")
        import random
        fallback = random.choice(DEFAULT_FALLBACK_INSIGHTS)
        return {
            'status': 'fallback',
            'source': 'offline_resilient_fallback',
            'endpoint': api_url,
            'latency_ms': round(latency_ms, 2),
            'timeout_threshold_seconds': timeout,
            'reason': str(e),
            'data': fallback
        }
