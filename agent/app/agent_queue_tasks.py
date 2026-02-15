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
# https://docs.celeryq.dev/en/main/userguide/tasks.html#retrying
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
def dummy_task(self):
    try:
        for i in range(3):
            print(f"Dummy task iteration: {i}")
            sleep(1)
    except Exception as exc:
        raise self.retry(exc=exc)

@app.task(name='invoke_agent_langfuse_celery_task',
          base=BaseTaskWithRetry,
          ignore_result=True,
          bind=True,
          time_limit=3600)
def invoke_agent_langfuse_celery_task(self,
                                      customer_id: int,
                                      customer_name: str, 
                                      case_id: int, 
                                      email_content: str, 
                                      job_id: str):
    try:
        invoke_agent_langfuse(customer_id, customer_name, case_id, email_content, job_id)
    except Exception as exc:
        raise self.retry(exc=exc)

@app.task(name='invoke_agent_celery_task',
          base=BaseTaskWithRetry,
          ignore_result=True,
          bind=True,
          time_limit=3600)
def invoke_agent_celery_task(self,
                             customer_id: int, 
                             customer_name: str,
                             case_id: int,
                             email_content: str,
                             job_id: str):
    try:
        invoke_agent(customer_id, customer_name, case_id, email_content, job_id)
    except Exception as exc:
        raise self.retry(exc=exc)

"""
Using celery:

https://docs.celeryq.dev/en/stable/getting-started/first-steps-with-celery.html#calling-the-task

dummy_task.delay()  Call the task asynchronously

"""
if __name__ == "__main__":

    product_availability_email = """
        Do you carry any boots suitable for hiking? I need something durable in a size 8.5
    """

    invoke_agent_langfuse_celery_task.delay(4000, "Michael", 4000, product_availability_email, "job_12345")
    #dummy_task.delay()
    #print("task invoked, now the worker will pick it up and execute asynchronously")