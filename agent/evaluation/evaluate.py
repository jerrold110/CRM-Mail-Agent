# Add parent path to sys path 
import sys
import os
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
)

import json
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent

# import the objects from email_agent.py
from email_agent import *
from _agent_memory_crud import delete_customer_support_history, add_customer_support_history

def get_node_output(test_case:dict, node_n):
    """
    This is used for all tool evaluations
    
    Input is a dictionary representing the input state, and a function of the node that you want to test in agent.py

    Uses the same case_id for every evaluation
    """
    customer_name = test_case['input_state']['customer_name']
    customer_id =test_case['input_state']['customer_id']
    email = test_case['input_state']['email_content']
    case_id = 1
    case_memory = test_case['input_state']['case_memory'] # this is the memory in the form {'0':'asdasd', '1':'asdasd'}

    # Prepare the initial state
    init_state = EmailAgentState(
        customer_name=customer_name,
        customer_id=customer_id,
        case_id=case_id,
        email_content=email
    )
    
    # Set the memory
    delete_customer_support_history(customer_id, case_id)
    if case_memory:
        # let message_history be blank
        add_customer_support_history(customer_id,
                                     case_id,
                                     case_memory
                                     )

    # Execute the node get the output
    node_output = node_n(init_state)

    return node_output

def get_eval_results_email_classifier():

    file_path = BASE_DIR / "eval_classify_email_long.json"

    # read json file
    with open(file_path, "r", encoding="utf-8") as f:
        json_array = json.load(f)

    # run evaluation for each case and aggregate results
    results = []
    for test_case in json_array:
        test_no = test_case['test_no']
        print(f"Test case: {test_no}")

        # Sets memory and initial state then deletes memory
        state_output = get_node_output(test_case, classify_email)
        output_topic = state_output.update['classification'].topic
        output_urgency = state_output.update['classification'].urgency
        output_urgency = True if output_urgency=='urgent' else False
        expected_topic = test_case['expected']['topic']
        expected_urgency = test_case['expected']['urgency']
        expected_urgency = True if expected_urgency=='urgent' else False
        
        result = (test_no, output_topic, output_urgency, expected_topic, expected_urgency)

        results.append(result)

    return results


print("Evaluation Version: 0.0.3")


