
"""
Celery configuration.

Environment variables:
    REDIS                 Redis hostname and port
    CELERY_BROKER_URL     Optional broker URL override
    CELERY_RESULT_BACKEND Optional result backend override
"""

import os


# --------------------------------------------------
# Redis configuration
# --------------------------------------------------

REDIS_ADDRESS = os.environ["REDIS"]

# Use logical database 1 and 2
broker_url = os.getenv(
    "CELERY_BROKER_URL",
    f"redis://{REDIS_ADDRESS}/1",
)

result_backend = os.getenv(
    "CELERY_RESULT_BACKEND",
    f"redis://{REDIS_ADDRESS}/2",
)


# --------------------------------------------------
# Serialization
# --------------------------------------------------

task_serializer = "json"
result_serializer = "json"
accept_content = ["json"]


# --------------------------------------------------
# Timezone
# --------------------------------------------------

timezone = "Asia/Singapore"
enable_utc = True


# --------------------------------------------------
# Task results
# --------------------------------------------------

# Results expire after 10 minutes
result_expires = 600

task_track_started = True


# --------------------------------------------------
# Rate limits
# --------------------------------------------------

task_annotations = {
    "dummy_task": {
        "rate_limit": "100/m",
    },
    "agent.run": {
        "rate_limit": "100/m",
    },
}
