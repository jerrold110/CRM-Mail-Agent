# Add parent path to sys path 
import sys
import os
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
)

# import the objects from email_agent.py
from email_agent import *
from _agent_memory_crud import update_customer_support_history, delete_customer_support_history

def get_node_output(test_case:dict, node_n:function):
    """
    Input is a dictionary representing the input state, and a function of the node that you want to test in agent.py

    Uses the same case_id for every evaluation
    """
    name = test_case['input_state']['customer_name']
    # Prepare the initial state
    init_state = EmailAgentState(
        customer_name=name,
        customer_id=1,
        case_id=1,
        email_content=test_case['input_state']['email_content']
    )
    
    # Set the memory
    delete_customer_support_history(name, 1)
    node_output = node_n(init_state)

    # Compare the results against the expected results
    # return the value for topic (Yes/no) and urgency(TP/TN/FP/FN)

    return node_output