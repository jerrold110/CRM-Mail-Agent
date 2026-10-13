
"""
This file contains the API endpoint and task definition for invoking the agent asynchronously using Celery.

Using celery:
https://docs.celeryq.dev/en/stable/getting-started/first-steps-with-celery.html#calling-the-task
process.delay(3, 4)  Call the task asynchronously

Celery tasks for asynchronous agent execution.

Start worker:
    celery -A agent_queue_tasks:app worker --loglevel=INFO
"""

import logging
from time import sleep

from celery import Celery, Task
from agent_entrypoint import invoke_agent_langfuse


logger = logging.getLogger(__name__)

# Celery application
app = Celery("agent_queue_tasks")
app.config_from_object("celeryconfig")


class BaseAgentTask(Task):
    """
    Common Celery task behavior.

    Maximum execution attempts: 3
    (1 initial attempt + 2 retries).
    """

    max_retries = 2

    # Preserve existing behavior: retry any exception.
    # Narrow this to transient errors before production.
    autoretry_for = (Exception,)

    # Automatic exponential backoff
    retry_backoff = 4
    retry_backoff_max = 60
    retry_jitter = True

    def before_start(self, task_id, args, kwargs):
        logger.info(
            "Task starting | task=%s | task_id=%s | attempt=%s",
            self.name,
            task_id,
            self.request.retries + 1,
        )

    def on_retry(self, exc, task_id, args, kwargs, einfo):
        logger.warning(
            "Task retrying | task=%s | task_id=%s | "
            "retry=%s | error_type=%s",
            self.name,
            task_id,
            self.request.retries,
            type(exc).__name__,
        )

    def on_success(self, retval, task_id, args, kwargs):
        logger.info(
            "Task succeeded | task=%s | task_id=%s",
            self.name,
            task_id,
        )

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logger.error(
            "Task failed | task=%s | task_id=%s | "
            "retries=%s | error_type=%s",
            self.name,
            task_id,
            self.request.retries,
            type(exc).__name__,
        )

        # Future: persist terminal failure in your
        # job-status store or publish a failure event.


@app.task(
    name="dummy_task",
    base=BaseAgentTask,
    ignore_result=True,
    bind=True,
    time_limit=3600,
)
def dummy_task(self):
    for i in range(3):
        logger.info(
            "Dummy task iteration | task_id=%s | iteration=%s",
            self.request.id,
            i,
        )
        sleep(1)


@app.task(
    name="agent.run",
    base=BaseAgentTask,
    ignore_result=True,
    bind=True,
    soft_time_limit=3500,
    time_limit=3600,
)
def invoke_agent_langfuse_celery_task(
    self,
    customer_id: int,
    customer_name: str,
    case_id: int,
    email_content: str,
    job_id: str,
):
    """
    Execute the LangGraph workflow asynchronously.

    The task_id should match the job_id supplied
    by FastAPI.

    Exceptions propagate so Celery can manage retries.
    """

    logger.info(
        "Agent execution started | job_id=%s | case_id=%s",
        job_id,
        case_id,
    )

    invoke_agent_langfuse(
        customer_id=customer_id,
        customer_name=customer_name,
        case_id=case_id,
        email_content=email_content,
        job_id=job_id,
    )

    logger.info(
        "Agent execution completed | job_id=%s",
        job_id,
    )

    return {"job_id": job_id, "status": "completed"}

"""
Using celery:

https://docs.celeryq.dev/en/stable/getting-started/first-steps-with-celery.html#calling-the-task

dummy_task.delay()  Call the task asynchronously

"""

if __name__ == "__main__":
    # Local manual test
    result = invoke_agent_langfuse_celery_task.delay(
        4000,
        "Michael",
        4000,
        "Do you carry any boots suitable for hiking? I need something durable in a size 8.5",
        "job_12345",
    )

    logger.info("Test task submitted | task_id=%s", result.id)
