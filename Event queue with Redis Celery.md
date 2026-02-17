# Why is an event queue necessary?
Agent systems are typically long running independent processes. In this system, Agents run concurrently as each email enters the system. An asynchronous event-driven architecture is necessary, hence an event broker with a queue is necessary. As **events are run in real-time**, the system needs to have rate limiting to prevent system overload, and retries with backoff and graceful error handling to make it durable.

# Why Celery and Redis?
Since the agent is written in python, I will be using Python native tools to build the event queue. 

Hence Celery is a good option because it is a python framework. This article outlines the capabilities of Celery (Simple, Highly available, Fase, Flexible)
https://docs.celeryq.dev/en/stable/getting-started/introduction.html#celery-is

Why Redis is the choice of broker (works well for rapid transport of small messages and scales well)
https://docs.celeryq.dev/en/stable/getting-started/backends-and-brokers/index.html#redis

# Quick use
## Run celery worker server.
celery -A agent_queue_tasks worker --loglevel=info --pool=threads (single thread)

celery -A agent_queue_tasks worker --loglevel=info --pool=threads (multi-thread)

python agent_queue_tasks_worker

## Run multiple workers
celery -A proj worker --loglevel=INFO --concurrency=10 -n worker1@%h

celery -A proj worker --loglevel=INFO --concurrency=10 -n worker2@%h

First steps: https://docs.celeryq.dev/en/stable/getting-started/first-steps-with-celery.html

Next steps: https://docs.celeryq.dev/en/stable/getting-started/next-steps.html

User Guide: https://docs.celeryq.dev/en/stable/userguide/index.html


# Monitoring and mangement
https://docs.celeryq.dev/en/stable/userguide/monitoring.html#monitoring-redis-queues

The number of tasks in a queue can be seen with redis-cli -h HOST -p PORT -n DATABASE_NUMBER llen QUEUE_NAME


Furthermore I am using Redis commander which is a redis management tool written with node.js https://github.com/joeferner/redis-commander

# Routing 
Options for routing tasks to different queues, adding queues to the celery app, and specifying workers to confume from specific queues.

https://docs.celeryq.dev/en/stable/getting-started/next-steps.html#routing


# Workers Guide
Workers in production are more complex

https://docs.celeryq.dev/en/stable/getting-started/first-steps-with-celery.html#running-the-celery-worker-server
https://docs.celeryq.dev/en/main/userguide/workers.html