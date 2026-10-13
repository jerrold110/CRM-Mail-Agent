import os
import logging
import sys
from uuid import uuid4
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from celery import Celery
from kombu.exceptions import OperationalError

# from agent_queue_tasks import (
#     dummy_task,
#     invoke_agent_celery_task,
#     invoke_agent_langfuse_celery_task,
# )


# --------------------------------------------------
# Configuration
# --------------------------------------------------

# Explicitly send to stdout
logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s | %(levelname)s | "
        "%(name)s | %(message)s"
    ),
    handlers=[
        logging.StreamHandler(sys.stdout)
    ],
    force=True,
)
logger = logging.getLogger(__name__)

REDIS_ADDRESS = os.environ["REDIS"]

app = FastAPI(
    title="Agent REST API",
    version="1.0.0",
)

celery_client = Celery(
    "api",
    broker=f"redis://{REDIS_ADDRESS}/1",
)


# --------------------------------------------------
# Request and response models
# --------------------------------------------------


class AgentInput(BaseModel):
    customer_id: int = Field(gt=0)
    customer_name: str = Field(min_length=1)
    case_id: int = Field(gt=0)
    email_content: str = Field(min_length=1)


class AgentJobResponse(BaseModel):
    job_id: str
    time: datetime
    error: str | None = None


# --------------------------------------------------
# Health check
# --------------------------------------------------


@app.get("/health")
def health_check():
    return {"status": "ok"}


# --------------------------------------------------
# Agent endpoint
# --------------------------------------------------


@app.post(
    "/email_agent/",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=AgentJobResponse,
)
def agent_request(agent_input: AgentInput) -> AgentJobResponse:

    job_id = str(uuid4())

    try:
        celery_client.send_task(
            "agent.run",
            args=[
                agent_input.customer_id,
                agent_input.customer_name,
                agent_input.case_id,
                agent_input.email_content,
                job_id,
            ],
            task_id=job_id,
        )
        # dummy_task.delay()
        # invoke_agent_langfuse_celery_task.delay(
        #     customer_id, customer_name, case_id, email_content, str(job_id)
        # )

    except OperationalError:
        logger.exception(
            "Failed to enqueue agent task: job_id=%s",
            job_id,
        )

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Task queue is temporarily unavailable",
        )

    logger.info(
        "Agent task queued successfully: job_id=%s",
        job_id,
    )
    print(f"Agent task queued successfully: {job_id}")

    return AgentJobResponse(
        job_id=job_id,
        time=datetime.now(timezone.utc),
    )
