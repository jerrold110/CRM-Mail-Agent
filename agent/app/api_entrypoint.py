from agent_queue_tasks import dummy_task, invoke_agent_celery_task, invoke_agent_langfuse_celery_task

from fastapi import FastAPI, status, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import datetime
from celery.exceptions import CeleryError
import uuid

"""
We are using Celery instead of FastAPI BackgroundTasks for better scalability and reliability.
"""


class AgentInput(BaseModel):
    customer_id: int
    customer_name: str
    case_id: int
    email_content: str


app = FastAPI()

@app.post("/email_agent/", status_code=202)
async def a_agent_request(agent_input: AgentInput):
    """
    This is the API entrypoint for invoking the agent asynchronously using Celery. It receives the input data, generates a job ID, and calls the Celery task to process the agent logic.
    """

    job_id = uuid.uuid4() # get job id for this http request
    customer_id = agent_input.customer_id
    customer_name = agent_input.customer_name
    case_id = agent_input.case_id
    email_content = agent_input.email_content

    # Invoke the Celery task asynchronously to the default queue "celery"
    try:
        dummy_task.delay()
        invoke_agent_langfuse_celery_task.delay(customer_id, customer_name, case_id, email_content, str(job_id))

    except Exception as e:
        return JSONResponse(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content={"error": str(e)})
    
    return {"job_id": job_id, 
            "time": datetime.now().isoformat(),
            "error": None}