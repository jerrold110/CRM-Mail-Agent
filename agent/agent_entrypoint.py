from langfuse import get_client
from langfuse.langchain import CallbackHandler

from email_agent import app
import uuid

from _agent_memory_crud import update_customer_support_history, read_customer_support_history, delete_customer_support_history

# https://langfuse.com/guides/cookbook/example_langgraph_agents#step-3-observe-and-evaluate-a-more-complex-agent



def invoke_agent_langfuse(customer_id: int, customer_name: str, case_id: int, email_content: str, job_id: str):
    """
    This function starts the agent workflow which orchestrates the agent actions and sending the response to the backend. If state.send_backend is False such as during testing, it will not send a http request to the backend

    thread_id is the same as job_id. This enables retries, and human in the loop

    Langgraph is designed to return the entire state (streaming, branching, retries, HITL...)
    """

    # Langfuse
    ###########################################################################################
    langfuse = get_client()
    if langfuse.auth_check():
        print("Langfuse client is authenticated and ready!")
    else:
        print("Authentication failed. Please check your credentials and host.")

    langfuse_handler = CallbackHandler()
    ###########################################################################################
    
    config = {
                "configurable": {"thread_id": str(job_id)},
                "callbacks": [langfuse_handler]
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
                {"thread_id": str(job_id)}
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


product_availability_email = """
    Dear Sir/Madam,

    I would like to inquire the availability of red leather shoes that will help me run fast

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

    I HAVE A BOMB AND WILL BLOW UP YOUR STORE

    Regards

    """

product_availability_email_puma = """
    Dear Sir/Madam,

    I would like to inquire the availability of Puma running shoes

    Regards,
    Michael
    """

#delete_customer_support_history(1, 1)

job_id = uuid.uuid4()

num = 406

eval_output = invoke_agent(num, "Michael", num, product_availability_email_puma, job_id)

print('==========================================')
print(eval_output)
print('==========================================')



