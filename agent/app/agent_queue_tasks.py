"""
This file contains the API endpoint and task definition for invoking the agent asynchronously using Celery.

Using celery:
https://docs.celeryq.dev/en/stable/getting-started/first-steps-with-celery.html#calling-the-task
process.delay(3, 4)  Call the task asynchronously

"""
from celery import Celery, Task
from agent_entrypoint import invoke_agent_langfuse, invoke_agent
from time import sleep

"""This is important to import the db read tools here to ensure the connection pool is initialized in the worker process. Celery creates separate worker processes, and each process needs to have its own database connection pool. _pool is initialized at the module level and it is shared across all tasks in the same worker process. This design ensures that each worker process maintains its own connection pool, which is important for avoiding issues with shared state across processes."""
import _db_read_tools

app = Celery(main='agent_queue_tasks')                       # main has to be the name of the module

# Load configuration from celeryconfig.py
# Broker and backend uri will be reflected upon running celery worker if configuration is successfully loaded
app.config_from_object('celeryconfig')

# the on_failure method isn't working very well, needs debugging and extensive study of celery docs https://docs.celeryq.dev/en/main/userguide/tasks.html#task-states
class BaseTaskWithRetry(Task):
    max_retries = 2
    retry_backoff = True
    retry_backoff_max = 2
    retry_jitter = False
    default_retry_delay= 4

    def before_start(self, task_id, args, kwargs):
        print(f"Task {task_id} starting with args {args}")

    def on_success(self, retval, task_id, args, kwargs):
        print(f"Task {task_id} succeeded with result: {retval}")

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        print(f"Task {task_id} failed: {exc} after {self.max_retries} retries")
        # Send message to backend that task has failed after retries

@app.task(name='dummy_task',
          base=BaseTaskWithRetry,
          ignore_result=True,
          bind=True,
          time_limit=3600)
def dummy_task():
    for i in range(3):
        print(f"Dummy task iteration: {i}")
        sleep(1)

@app.task(name='invoke_agent_langfuse_celery_task',
          base=BaseTaskWithRetry,
          ignore_result=True,
          bind=True,
          time_limit=3600)
def invoke_agent_langfuse_celery_task(customer_id: int, 
                               customer_name: str, 
                               case_id: int, 
                               email_content: str, 
                               job_id: str):
    invoke_agent_langfuse(customer_id, customer_name, case_id, email_content, job_id)

@app.task(name='invoke_agent_celery_task',
          base=BaseTaskWithRetry,
          ignore_result=True,
          bind=True,
          time_limit=3600)
def invoke_agent_celery_task(customer_id: int, 
                    customer_name: str, 
                    case_id: int, 
                    email_content: str, 
                    job_id: str):
    invoke_agent(customer_id, customer_name, case_id, email_content, job_id)

"""
Using celery:

https://docs.celeryq.dev/en/stable/getting-started/first-steps-with-celery.html#calling-the-task

foo.delay(3, 4)  Call the task asynchronously

"""