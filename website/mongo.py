import os
import logging
from datetime import datetime, timezone
from collections import deque

logger = logging.getLogger('website.mongo')

# In-memory fallback ring buffers if MongoDB is temporarily unreachable
_memory_chat_logs = deque(maxlen=200)
_memory_feedback = deque(maxlen=200)
_memory_request_logs = deque(maxlen=200)

_mongo_client = None


def get_mongo_client():
    global _mongo_client
    if _mongo_client is not None:
        return _mongo_client

    mongo_uri = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/aether_db')
    try:
        from pymongo import MongoClient
        # Quick timeout (1.5 seconds) so offline local MongoDB never slows down requests
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=1500)
        _mongo_client = client
        return _mongo_client
    except Exception as e:
        logger.warning(f"Could not initialize MongoClient: {e}")
        return None


def get_mongo_db():
    client = get_mongo_client()
    if not client:
        return None
    try:
        # Ping server to confirm live connection
        client.admin.command('ping')
        mongo_uri = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/aether_db')
        db_name = mongo_uri.split('/')[-1].split('?')[0] or 'aether_db'
        return client[db_name]
    except Exception as e:
        logger.debug(f"MongoDB ping failed: {e}")
        return None


def save_chat_log(session_id, user_message, bot_response, intent=None, source="ai_assistant"):
    """
    Saves a chat log entry into MongoDB 'chat_logs' collection.
    Falls back to memory if MongoDB is unavailable.
    """
    doc = {
        'session_id': session_id,
        'user_message': user_message,
        'bot_response': bot_response,
        'intent': intent,
        'source': source,
        'timestamp': datetime.now(timezone.utc).isoformat(),
    }

    db = get_mongo_db()
    if db is not None:
        try:
            db.chat_logs.insert_one(doc.copy())
            logger.info(f"Chat log saved to MongoDB for session {session_id}")
            return True
        except Exception as e:
            logger.warning(f"MongoDB insert_one failed for chat_logs: {e}")

    # Fallback storage
    _memory_chat_logs.append(doc)
    logger.info(f"Chat log cached in-memory (fallback) for session {session_id}")
    return True


def save_chat_feedback(session_id, rating, comment="", message=None):
    """
    Saves user feedback (thumbs up/down, 1-5 rating, comments) to MongoDB 'feedback' collection.
    """
    doc = {
        'session_id': session_id,
        'rating': rating,
        'comment': comment,
        'message_snippet': message,
        'timestamp': datetime.now(timezone.utc).isoformat(),
    }

    db = get_mongo_db()
    if db is not None:
        try:
            db.feedback.insert_one(doc.copy())
            logger.info(f"Feedback saved to MongoDB for session {session_id}")
            return True
        except Exception as e:
            logger.warning(f"MongoDB insert_one failed for feedback: {e}")

    _memory_feedback.append(doc)
    logger.info(f"Feedback cached in-memory (fallback) for session {session_id}")
    return True


def save_request_log(method, path, status_code, duration_ms, ip_address):
    """
    Saves HTTP request logs to MongoDB 'request_logs' collection.
    """
    doc = {
        'method': method,
        'path': path,
        'status_code': status_code,
        'duration_ms': round(duration_ms, 2),
        'ip_address': ip_address,
        'timestamp': datetime.now(timezone.utc).isoformat(),
    }

    db = get_mongo_db()
    if db is not None:
        try:
            db.request_logs.insert_one(doc.copy())
            return True
        except Exception:
            pass

    _memory_request_logs.append(doc)
    return True


def get_mongo_status():
    """
    Returns connection diagnosis for health check endpoint.
    """
    mongo_uri = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/aether_db')
    # Mask password if in URI
    masked_uri = mongo_uri
    if '@' in mongo_uri and '://' in mongo_uri:
        prefix, rest = mongo_uri.split('://', 1)
        creds, host = rest.split('@', 1)
        masked_uri = f"{prefix}://***:***@{host}"

    db = get_mongo_db()
    if db is not None:
        try:
            chat_count = db.chat_logs.count_documents({})
            feedback_count = db.feedback.count_documents({})
            return {
                'connected': True,
                'status': 'online',
                'target_uri': masked_uri,
                'chat_logs_count': chat_count,
                'feedback_count': feedback_count,
                'storage': 'MongoDB Database'
            }
        except Exception as e:
            return {
                'connected': False,
                'status': 'error',
                'target_uri': masked_uri,
                'error': str(e),
                'storage': 'In-Memory Fallback Active'
            }

    return {
        'connected': False,
        'status': 'offline',
        'target_uri': masked_uri,
        'chat_logs_cached': len(_memory_chat_logs),
        'feedback_cached': len(_memory_feedback),
        'storage': 'In-Memory Fallback Active (Zero Crash Resilience)'
    }


def get_recent_chat_logs(limit=10):
    db = get_mongo_db()
    if db is not None:
        try:
            cursor = db.chat_logs.find({}, {'_id': 0}).sort('_id', -1).limit(limit)
            return list(cursor)
        except Exception:
            pass
    return list(_memory_chat_logs)[-limit:]
