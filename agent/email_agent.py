import os
from dotenv import load_dotenv
load_dotenv()

from typing import TypedDict, Literal, Annotated

# Define the Nodes of the agent
from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt, Command, RetryPolicy
from langchain_openai import ChatOpenAI
from langchain.messages import HumanMessage, SystemMessage, AIMessage, ToolMessage
import asyncio

# Graph State imports
from _state import EmailCharacteristics, EmailAgentState, DeliveryInfo

# Import tools
from _db_read_tools import get_unique_list, get_shoe_characteristics, get_query_shoe_characteristics, get_product_availability, get_customer_open_deliveries, get_current_date, is_coupon_redeemed, late_delivery_last60d

# Import agent memory functions
from _agent_memory_crud import update_customer_support_history, read_customer_support_history, delete_customer_support_history

# Setup
llm = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0.5)

summary_llm = ChatOpenAI(
    model="gpt-4.1-nano",
    temperature=0.5)

tools = [get_product_availability]
tools_by_name = {tool.name: tool for tool in tools}

llm_check_inventory_with_tools = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0.5).bind_tools(tools)

"""
This needs to be changed. Async should only be used if there are multiple concurrent calls within the agent, celery handles asynchronous execution so agent should be synchronous
https://docs.langchain.com/oss/python/langgraph/use-graph-api#async

"""

# Nodes
def classify_email(state: EmailAgentState) -> Command[Literal["get_comprehensive_product_query", "find_customer_order"]]:
    """
    Use LLM to classify email topic and urgency, then route accordingly. 

    Reads from memory to classify correctly and updates memory.
    """
    structured_llm = llm.with_structured_output(EmailCharacteristics)
    
    conversation_summary = read_customer_support_history(state.customer_id, state.case_id) # Dict or none

    if not conversation_summary:
        conversation_summary_formatted = "No history available"
    else:
        conversation_summary_formatted = "\n".join([f'-{v}' for v in conversation_summary.values()])

    # Format the prompt on-demand, not stored in state
    classification_prompt = f"""
    Analyze this email from a customer and classify it. Use the email conversation history to gain context on this email if necessary. 

    Email: 
    {state.email_content}

    Email history summary:
    {conversation_summary_formatted}
        
    Provide classification including topic, urgency, and provide a summary. If the customer has sent an email with the same meaning that occurs more than three times in the email history, classify urgency as urgent. If there are multiple request types in the email classify topic as 'other'.
    """

    # Get structured response directly as dict
    classification = structured_llm.invoke(classification_prompt)

    # Determine next node based on classification    
    if classification.topic == 'product_availability_or_recommendation':
        goto = "get_comprehensive_product_query"
    elif classification.topic == 'delivery_delay':
        goto = 'find_customer_order'
    else:
        print('email could not be classified and is routed to human escalation')
        goto = "other"
    # print(conversation_summary_formatted)
    # print("Summary:", classification.summary)
    # print("Classification:", classification.topic)
    # print("urgency:", classification.urgency)
    
    # Update memory with summary of customer email
    update_customer_support_history(
        state.customer_id,
        state.case_id,
        classification.summary,
        conversation_summary,       # None or a dictionary
        True)

    if classification.urgency == 'urgent' or goto == 'other':
        return Command(
            update={"classification": classification,
                    'actions': [{"Action": "Human_escalation"}]
                    },
            goto='send_response_to_backend'
        )

    # Update state data and select the next node (goto)
    return Command(
        update={"classification": classification},
        goto=goto
    )

def find_customer_order(state: EmailAgentState) -> Command[Literal["write_response", "check_deliveries"]]:
    """
    - Prompt the LLM to extract the tracking_numbers provided by the customer.
    """
    product_match_prompt = f"""
    Identify the  tracking numbers in the client's email. 
    Tracking numbers are a combination of letters and integers such as: UPS987654321, FDX123456789

    Client email: 
    {state.email_content}
    """

    structured_llm = llm.with_structured_output(DeliveryInfo)
    response = structured_llm.invoke(product_match_prompt)

    if len(response.tracking_number) == 0:
        message = "The customer has not provided a valid delivery tracking number in their email. Ask them to respond with valid information."

        return Command(
            update = {'context': [message]},
            goto = "write_response"
        )

    return Command(
        update = {'delivery': response},
        goto="check_deliveries"
    )

def check_deliveries(state: EmailAgentState):
    """
    - Check if there are any open deliveries
    - If there are, check for matches
    - If there are matches, check for deliveries that 
    """

    open_deliveries = asyncio.run(get_customer_open_deliveries(state.customer_id))
    # Match open_deliveries with information extracted from email
    matches = []
    for d in open_deliveries:
        tracking_number = d[2]
        if tracking_number in state.delivery.tracking_number:
            matches.append(d)
    
    # No matches
    if len(matches) == 0:
        message = f"The customer has provided tracking numbers {state.delivery.tracking_number} but they do not correspond with any of the customer's open deliveries."

        return Command(
            update = {'context': [message]},
            goto = "write_response"
        )

    present_date = asyncio.run(get_current_date())
    # Credit refunds and coupons
    new_context = []
    new_actions = []
    for match in matches:
        delivery_id = match[1]
        tracking_number = match[2]
        expected_delivery_end = match[3]
        shipped_date = match[4]
        actual_delivery = match[5]
        # item is late, may or may not be delivered
        if expected_delivery_end < present_date:
            # item is delivered
            if actual_delivery is not None:
                difference = present_date - expected_delivery_end
                days_late = difference.days
                new_context.append(f"Delivery id {delivery_id} and tracking number {tracking_number} shipped on {str(shipped_date)} is late by {days_late} days and a refund for {days_late} days of the delivery fee is being refunded to the customer.")
                new_actions.append({"Action": "Refund_delivery_fee", "params": {"delivery_id": str(delivery_id), "days": str(days_late)}})
            # item is not delivered yet
            elif actual_delivery is None:
                new_context.append(f"Delivery id {delivery_id} and tracking number {tracking_number} shipped on {str(shipped_date)} is late and currently out on delivery refund of the delivery fee for the number of late days will be credited to the customer when delivered.")
                new_actions.append({"Action": "Track_refund_delivery_fee", "params": {"delivery_id": str(delivery_id)}})

            # Create coupon if 
            # - There was a late closed delivery in the last 60 days
            ldl = asyncio.run(late_delivery_last60d(state.customer_id))
            icr = asyncio.run(is_coupon_redeemed(state.customer_id, delivery_id))
            if ldl and not icr:
                new_context.append(f"Delivery id {delivery_id} and tracking number {tracking_number} is late and there was another late delivery within the last 60 days. A coupon for expedited delivery is created and offered to the customer which can be used on the next order.")
                new_actions.append({"Action": "Create_coupon", "params": {"delivery_id": str(delivery_id), "customer_id": str(state.customer_id)}})
        # item is not late and an open dlivery
        else:
            new_context.append(f"Delivery id {delivery_id} and tracking number {tracking_number} shipped on {str(shipped_date)} has not been delivered yet, and this delivery is still on time. Ask the customer to be patient.")

    # Despite using pydantic, state is updated with this syntax not state.new_context. This is possible because this is a LangGraph
    return {'context': new_context,
            'actions': new_actions}

def get_comprehensive_product_query(state: EmailAgentState) -> str:
    """
    Query always uses the format:
    SELECT * FROM shoe_characteristics ...

    This is necessary because the LLM is not able to intelligently understand tabular data on numerical columns (such as size), it is however able to understand textual data (such as descriptions).
    Hence the process is

    Query -> SQL query -> Tabular output -> filter by specific thing the customer is asking for

    """

    query = state.email_content

    text2sql_prompt = f"""
    You are an expert data analyst.

    Your task is to translate a natural-language question into a single, valid, read-only SQL query. If there are multiple shoes mentioned use inclusive logic and not use exclusive logic to return everything in the query.

    Database:
    - Engine: PostgreSQL

    Rules:
    - ONLY Filter by the columns listed in the schema using the where clause
    - Do NOT invent columns or tables.
    - Always use SELECT *.
    - Return at most 500 rows.
    - For string columns, apply the lower() function to both sides
    - If the question cannot be answered with the schema, return: CANNOT_ANSWER

    Schema:
    Table: shoe_characteristics
    Columns:
    - size (Decimal(3,1)): the size of the shoe
    - color (VARCHAR(50)): the color
    - weight (DECIMAL(5,2)): the weight in grams
    - brand (TEXT): brand of the shoe: the brand

    Use these examples as reference:

    Question: I am looking for blue mesh shoes in size 9.
    Answer: SELECT * FROM shoe_characteristics\nWHERE lower(color) = 'blue'\n AND size = 9\nLIMIT 500;

    Question: Can you recommend any white shoes in size 9.5 that are comfortable and stylish?
    Answer: SELECT * FROM shoe_characteristics\nWHERE lower(color) = 'white'\n AND size = 9.5\nLIMIT 500;
    """

    response = llm.invoke(
        [SystemMessage(content=text2sql_prompt)] + [HumanMessage(query)]
    )

    return {'closest_product_sql_query': response.content}

def match_closest_product(state: EmailAgentState) -> Command[Literal["check_inventory_llm_call"]]:
    """
    Email -> sql template -> results -> analyse results
    - Product name: Do not use
    - Brand: Use, let llm edit query
    - Numbers: Extract

    Prompt the LLM to determine if there if there are products that matches the description(s) provided by the customer.

    """
    #valid_brands = get_unique_list('brand')
    #valid_colors = get_unique_list('color')
    #valid_materials = get_unique_list('material')
    #print('-------------------------------------------------')
    #raise ValueError("This is a manually throws error.")
    
    sql_query = state.closest_product_sql_query

    # Check without filters. THIS IS A BAD OPTION BUT ALLOWS GRACEFUL HANDLING
    if sql_query == 'CANNOT_ANSWER':
        product_characteristics = asyncio.run(get_shoe_characteristics())
    else:
        product_characteristics = asyncio.run(get_query_shoe_characteristics(sql_query))

    if product_characteristics == "No results":
        response = "There are no products in the inventory that match the customer's inquiry."
        return Command(
            update={"messages": [AIMessage(content=response)], "context": [response]},    # Adds to messages not replace. We don't want to save the response metadata to the state,
            goto="write_response"
        )
    else:
        product_match_prompt = f"""
        Match the products the client is looking for to the closest products we have in our product catalogue which is in csv format. Pay attention to specific requests about size. Tell me what the client is looking for and the ids of the matching products.

        Client email: {state.email_content}

        Product catalogue in csv format: 
        {product_characteristics}
        """

        response = llm.invoke(product_match_prompt) # AIMessage type
        response = response.content

        return Command(
            update={"messages": [AIMessage(content=response)]},    # Adds to messages not replace. We don't want to save the response metadata to the state,
            goto="check_inventory_llm_call"
        )

def check_inventory_llm_call(state: EmailAgentState):
    """ 
    LLM decides what tool calls to make. The tool call decisions are made here.
    This function will either declare that tools need to be called, or declare that no more tool calls need to be made and progress to the next node.
    """
    
    agent_message = """
    You are a helpful assistant that checks the availability of products by checking the inventory and incoming shipments of product(s) by product_id.
    """
    # print("START---------------------------------")
    # for s in state['messages']:
    #     print('>>', s)
    # print("END---------------------------------")

    #llm_closest_product_findings = state['messages'][-1].content
    
    """
    We have to pass in the entire message history so that when the agent sees:
    - Instruction (SystemMessage)
    - Tool call instructions (Unformatted)
    - Tool call result 1,2,3...n (ToolMessage)
    
    It will append a new message that summarizes the findings and has no more tool call instructions
    """
    response = llm_check_inventory_with_tools.invoke(
        [SystemMessage(content=agent_message)] + state.messages
    )
    
    return {
        "messages": [response] # Return the entire response
    }

def conditional_edge_check_inventory(state: EmailAgentState) -> Literal["check_inventory_tool_node", "write_response"]:
    """Decide if we should continue the loop or stop based upon whether the LLM made a tool call"""

    messages = state.messages
    last_message = messages[-1]

    if last_message.tool_calls:
        return "check_inventory_tool_node"
    
    return "write_response"
    
def check_inventory_tool_node(state: EmailAgentState):
    """
    This node performs the tool calls for get_inventory_stock and get_incoming_deliveries
    """
    tool_call_message = state.messages[-1].tool_calls

    message_result = []
    context_result = []

    for tool_call in tool_call_message:
        tool = tools_by_name[tool_call["name"]]
        observation = tool.invoke(tool_call["args"])

        message_result.append(ToolMessage(content=observation, tool_call_id=tool_call["id"]))
        context_result.append(observation)

    return {"messages": message_result,
            "context": context_result}

def write_response(state: EmailAgentState) -> Command[Literal["send_response_to_backend"]]:
    """
    Write email to the customer that achieves the objective and responds to the customer email
    """
    classification = state.classification
    email_topic = 'unknown' if classification.topic == None else classification.topic

    email_objective = {
        "other": None,
        "product_availability_or_recommendation": "The customer has asked for a recommendation based on certain criteria or availability of certian shoes. Tell the customer that these products are the closest match to what they are looking for and their availability",
        "delivery_delay": "The customer has complained about a delivery being delayed, refer to the context for details and respond. Only mention deliveries by tracking number, do not mention delivery id"
    }

    if state.context != None:
        formatted_context = "\n".join([f"- {doc}" for doc in state.context])

    # Build the prompt with formatted context
    draft_prompt = f"""
    {email_objective[email_topic]}.
    The customer's name is: {state.customer_name}
    Draft a reply to this customer email:
    {state.email_content}

    Relevant context:
    {formatted_context}

    Guidelines:
    - Be professional and helpful
    - Address their specific concern
    - Use the provided context when relevant
    - Sign off the email as Customer Service Team
    """

    email_response = llm.invoke(draft_prompt)

    # Get the summary with 4.1 micro
    summary_instructions = "You are an expert summarizer that summarizes the content in an email."
    #"You are an expert summarizer that summarizes the content in an email sent by the Customer Service Team."
    email_response_summary = summary_llm.invoke(
        [
            SystemMessage(content=summary_instructions),
            HumanMessage(content=email_response.content)
        ]
    )

    return Command(
        update={"messages": [AIMessage(content=email_response.content)],
                "email_response": email_response.content,
                "email_response_summary": email_response_summary.content},
        goto="send_response_to_backend"
    )

def send_response_to_backend(state: EmailAgentState) -> dict:
    """
    Send to event queue that writes to backend CRM database:
    - Case ID
    - Response
    - Response summary
    - Context
    - Actions
    
    """
    
    print(state.email_response)
    print('Context:', state.context)
    print('Actions:', state.actions)
    print(state.email_response_summary)
    if state.send_backend:
        print('send backend status:', state.send_backend)

from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import RetryPolicy
import uuid
from asyncpg.exceptions import PostgresSyntaxError, PostgresConnectionError, PostgresIOError
from openai import RateLimitError, APIConnectionError, BadRequestError

workflow = StateGraph(EmailAgentState)

# Explicit mention of the error type is required for retrying to work
# API/tool time outs, network, wrong model output

all_retrypolicy = RetryPolicy(
    max_attempts=3, 
    initial_interval=1.0,
    backoff_factor=2.0,
    retry_on=[
        ConnectionRefusedError, 
        ConnectionError, 
        PostgresSyntaxError, 
        PostgresConnectionError, 
        PostgresIOError,
        RateLimitError,
        APIConnectionError,
        BadRequestError
    ]
)

# Add nodes with appropriate error handling
workflow.add_node("classify_email", classify_email)

workflow.add_node("get_comprehensive_product_query", get_comprehensive_product_query, retry_policy=all_retrypolicy)
workflow.add_node("match_closest_product", match_closest_product, retry_policy=all_retrypolicy)
workflow.add_node("check_inventory_llm_call", check_inventory_llm_call, retry_policy=all_retrypolicy)
workflow.add_node("check_inventory_tool_node", check_inventory_tool_node, retry_policy=all_retrypolicy)

workflow.add_node("find_customer_order", find_customer_order, retry_policy=all_retrypolicy)
workflow.add_node("check_deliveries", check_deliveries, retry_policy=all_retrypolicy)

workflow.add_node("write_response", write_response, retry_policy=all_retrypolicy)
workflow.add_node("send_response_to_backend", send_response_to_backend)

# Add only the essential edges
workflow.add_edge(START, "classify_email")

workflow.add_edge("get_comprehensive_product_query", "match_closest_product")
workflow.add_edge("match_closest_product", "check_inventory_llm_call")
workflow.add_conditional_edges(
    "check_inventory_llm_call",
    conditional_edge_check_inventory,
    ["check_inventory_tool_node", "write_response"]
)
workflow.add_edge("check_inventory_tool_node", "check_inventory_llm_call")

workflow.add_edge("check_deliveries", "write_response")

workflow.add_edge("write_response", "send_response_to_backend")
workflow.add_edge("send_response_to_backend", END)

# Compile with checkpointer for persistence
memory = MemorySaver()
app = workflow.compile(checkpointer=memory)

def invoke_agent(initial_state:dict, job_id:str):
    """
    This function starts the agent workflow which orchestrates the agent actions and sending the response to the backend. If state.send_backend is False such as during testing, it will not send a http request to the backend

    thread_id is the same as job_id. This enables retries, and human in the loop

    Langgraph is designed to return the entire state (streaming, branching, retries, HITL...)
    """
    
    config = {"configurable": 
                {"thread_id": str(job_id)}
             }

    graph_state = app.invoke(initial_state, config=config) # this returns a dictionary

    eval_output = {
        'email_response': graph_state.get('email_response', ''), # this is buggy, unsure why
        'context': graph_state['context'],
        'actions': graph_state['actions']
    }

    return eval_output


# ======= Test the agent ==========


    