from langfuse import get_client
from langfuse.langchain import CallbackHandler

from email_agent import app
import uuid

from _agent_memory_crud import update_customer_support_history, read_customer_support_history, delete_customer_support_history

# https://langfuse.com/guides/cookbook/example_langgraph_agents#step-3-observe-and-evaluate-a-more-complex-agent
"""
In Langfuse Observability is structured into three components: sessions, traces, and observations.
Observations have types, trces represent a single request of operations, sessions are used to group traces within the same user interaction
https://langfuse.com/docs/observability/data-model#adding-attributes

Langfuse is built on OpenTelemetery. Langfuse sends traces asynchronously in batche through a background exporter that runs continuously and flushes batches on its own. This allows it to work well for long-running applications like AI agents.

"""

def invoke_agent_langfuse(customer_id: int, customer_name: str, case_id: int, email_content: str, job_id: str):
    """
    This function starts the agent workflow which orchestrates the agent actions and sending the response to the backend. If state.send_backend is False such as during testing, it will not send a http request to the backend

    thread_id is the same as job_id. This enables retries, and human in the loop

    Langgraph is designed to return the entire state (streaming, branching, retries, HITL...)
    """

    # Langfuse
    # Group trace by customer_id and job_id
    # ENV variables loaded in email_agent.py for authentication and tracing environment (dev, sit, uat...)
    ###########################################################################################
    langfuse = get_client()
    if langfuse.auth_check():
        print("Langfuse client is authenticated and ready!")
    else:
        print("Authentication failed. Please check your credentials and host.")

    langfuse_handler = CallbackHandler()
    ###########################################################################################
    
    config = {
                "configurable": {"thread_id": str(case_id)},        # Thread ID is case_id to maintain context across job runs
                "callbacks": [langfuse_handler],
                "metadata" : {                                      # Metadata for trace grouping. You can use keywords langfuse_user_id, langfuse_session_id, langfuse_tags
                    "langfuse_user_id": str(customer_id), 
                    "langfuse_session_id": str(job_id),
                    "case_id": str(case_id),
                    "job_id": str(job_id),
                    "agent_version": "0.0.1",
                }
             }
    
    initial_state = {
        'send_backend': False,
        "customer_name": customer_name,
        "customer_id": customer_id,
        "case_id": case_id,
        "email_content": email_content
    }


    for s in app.stream(input=initial_state, config=config):
        print(s)


def invoke_agent(customer_id: int, customer_name: str, case_id: int, email_content: str, job_id: str):
    """
    This function starts the agent workflow which orchestrates the agent actions and sending the response to the backend. If state.send_backend is False such as during testing, it will not send a http request to the backend

    thread_id is the same as job_id. This enables retries, and human in the loop

    Langgraph is designed to return the entire state (streaming, branching, retries, HITL...)
    """
    
    config = {"configurable": 
                {"thread_id": str(case_id)}
             }
    initial_state = {
        'send_backend': False,
        "customer_name": customer_name,
        "customer_id": customer_id,
        "case_id": case_id,
        "email_content": email_content
    }

    graph_state = app.invoke(initial_state, config=config) # this returns a dictionary

    eval_output = {
        'email_response': graph_state.get('email_response', ''), # this is buggy, unsure why
        'context': graph_state['context'],
        'actions': graph_state['actions']
    }

    return eval_output


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

    eval_output = invoke_agent_langfuse(num, "Michael", num, other_email, job_id)

    print('==========================================')
    print(eval_output)
    print('==========================================')
