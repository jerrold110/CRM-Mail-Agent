"""
Agent execution entrypoints.

Provides:
- Agent execution with Langfuse observability
- Agent execution without Langfuse callbacks
- Shared LangGraph input and configuration
"""

import logging
import uuid


from langfuse import get_client, propagate_attributes
from langfuse.langchain import CallbackHandler

from email_agent import app
from _agent_memory_crud import delete_customer_support_history

logger = logging.getLogger(__name__)

AGENT_VERSION = "0.0.7"


def _run_agent_graph(
    customer_id: int,
    customer_name: str,
    case_id: int,
    email_content: str,
    callbacks=None,
    send_backend: bool = False,
):
    """
    Run the LangGraph workflow.

    Conversation history is scoped to both customer
    and case to avoid checkpoint collisions.
    """

    thread_id = f"{customer_id}:{case_id}"

    config = {
        "configurable": {
            "thread_id": thread_id,
        },
    }

    if callbacks is not None:
        config["callbacks"] = callbacks

    initial_state = {
        "send_backend": send_backend,
        "customer_name": customer_name,
        "customer_id": customer_id,
        "case_id": case_id,
        "email_content": email_content,
    }

    return app.invoke(
        initial_state,
        config=config,
    )


def invoke_agent_langfuse(
    customer_id: int,
    customer_name: str,
    case_id: int,
    email_content: str,
    job_id: str,
):
    """
    Execute agent with Langfuse tracing.

    Every execution gets:
    - Its own root observation
    - Its own LangChain callback handler
    - A job_id for correlation

    Related executions for the same customer/case
    share a Langfuse session.
    """

    # Reuses the process-local Langfuse client.
    langfuse = get_client()

    session_id = f"{customer_id}:{case_id}"

    logger.info(
        "Starting traced agent | job_id=%s",
        job_id,
    )

    with langfuse.start_as_current_observation(
        as_type="span",
        name="agent.run",
    ):
        # langfuse propogate_attributes
        with propagate_attributes(
            user_id=str(customer_id),
            session_id=session_id,
            version=AGENT_VERSION,
            metadata={
                "job_id": job_id,
                "case_id": str(case_id),
            },
        ):
            # New handler for this execution only.
            langfuse_handler = CallbackHandler()

            graph_state = _run_agent_graph(
                customer_id=customer_id,
                customer_name=customer_name,
                case_id=case_id,
                email_content=email_content,
                callbacks=[langfuse_handler],
            )

    logger.info(
        "Traced agent completed | job_id=%s",
        job_id,
    )

    return graph_state


if __name__ == "__main__":
    product_availability_email = """
        Dear Sir/Madam,

        Do you carry any boots suitable for hiking? I need something durable in a size 8.5

        Regards,
        Michael
    """

    product_availability_email_urgent = """
        Dear Sir/Madam,

        We urgently need to place an order of Addidas football shoes because our team is competing in the state finals next weekend. We request an immediate response.

        Regards,
        Michael
    """
    # UPS321654987
    delivery_delay_email = """
        Dear sir,

        I want to find out why my delivery is delayed, tracking number UPS321654987

        """
    delivery_delay_email_1 = """
        Dear sir,

        I want to find out why my delivery is delayed

        """
    delivery_delay_email_2 = """

        tracking number UPS321654987

        """
    urgent_email = """
        Dear sir/madam,

        I ordered a shipment of PUMA shoes, the shoes have a manufacturing defect that caused the death of one of our employees. Please contact us immediately

        Regards
        """

    product_availability_email_puma = """
        Dear Sir/Madam,

        I would like to inquire the availability of Puma running shoes.

        Can you also recommend a pair of blue basketball shoes.

        Regards,
        Michael
        """

    other_email = """
        Dear Sir/Madam,

        What time does your store close on saturday evening?

        Regards,
        Michael
        """

    random_email = """
    Hello,

    We are looking to purchase shoes for our sprinting team. Could you provide information on the types of shoes you have available for sprinters?

    Thank you,
    Michael 
    """

    delete_customer_support_history(4000, 4000)

    job_id = uuid.uuid4()

    num = 4000

    eval_output = invoke_agent_langfuse(
        num, "Michael", num, product_availability_email, job_id
    )

    print("==========================================")
    print(eval_output)
    print("==========================================")
