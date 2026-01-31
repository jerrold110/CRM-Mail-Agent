# Add parent path to sys path 
import sys
import os
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
)


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

def eval_email_classifier(test_case:dict):
    # Sets memory and initial state, returns node output
    state_output = get_node_output(test_case, classify_email)

    test_no = test_case['test_no']

    output_topic = state_output.update['classification'].topic
    output_urgency = state_output.update['classification'].urgency

    expected_topic = test_case['expected']['topic']
    expected_urgency = test_case['expected']['urgency']

    topic_res = output_topic == expected_topic
    if expected_urgency == 'urgent' and output_urgency == 'urgent':
        urgency_res = 'TP'
    elif expected_urgency != 'urgent' and output_urgency == 'urgent':
        urgency_res = 'FP'
    elif expected_urgency == 'urgent' and output_urgency != 'urgent':
        urgency_res = 'FN'
    elif expected_urgency != 'urgent' and output_urgency != 'urgent':
        urgency_res = 'TN'

    return (test_no, topic_res, urgency_res)


def get_evaluation_results(file_path:str, evaluator_func):
    # read json file
    with open(file_path, "r", encoding="utf-8") as f:
        json_array = json.load(f)

    # run evaluation for each case and aggregate results
    results = []
    for case in json_array:
        result = evaluator_func(case)
        results.append(result)

    return results

import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
json_path = BASE_DIR / "eval_classify_email.json"

result = get_evaluation_results(json_path, eval_email_classifier)
print(result)

