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
from _db_read_tools import get_shoe_characteristics, get_product_availability, get_customer_open_deliveries

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

# Nodes
async def classify_email(state: EmailAgentState) -> Command[Literal["find_closest_product", "find_customer_order"]]:
    """
    Use LLM to classify email topic and urgency, then route accordingly. 

    Reads from memory to classify correctly and updates memory.
    """

    structured_llm = llm.with_structured_output(EmailCharacteristics)
    
    conversation_summary = None #= await read_customer_support_history(state['customer_id'], state['case_id']) # Dict or none

    if not conversation_summary:
        conversation_summary_formatted = "No history available"
    else:
        conversation_summary_formatted = "\n".join([f'-{v}' for v in conversation_summary.values()])

    # Format the prompt on-demand, not stored in state
    classification_prompt = f"""
    Analyze this email and classify it. Use the email conversation history to gain context on this email if necessary

    Email: 
    {state.email_content}

    Email history summary:
    {conversation_summary_formatted}
        
    Provide classification including topic, urgency, and provide a summary. 
    """

    # Get structured response directly as dict
    classification = await structured_llm.ainvoke(classification_prompt)

    # Update memory with summary of customer email
    # await update_customer_support_history(
    #     state['customer_id'],
    #     state['case_id'],
    #     classification['summary'],
    #     conversation_summary,       # None or a dictionary
    #     True)

    # Determine next node based on classification
    if classification.topic == 'product_availability_inquiry':
        goto = "find_closest_product"
    elif classification.topic == 'product_recommendation_request':
        goto = "find_closest_product"
    elif classification.topic == 'delivery_complaint':
        goto = 'find_customer_order'
    else:
        goto = "other"
    
    print("Summary:", classification.topic)
    print("Classification:" ,classification.topic)
    print(goto)

    # Update state data and select the next node (goto)
    return Command(
        update={"classification": classification},
        goto=goto
    )

async def find_closest_product(state: EmailAgentState) -> Command[Literal["check_inventory_llm_call"]]:
    """
    Prompt the LLM to determine if there if there are products that matches the description(s) provided by the customer.
    """
    # Identify what the product being searched for is by checking product features database
    # asyncio.run(get_shoe_characteristics()) is wrong for asynchronous programming
    product_characteristics = await get_shoe_characteristics() 

    product_match_prompt = f"""
    Match the products the client is looking for in their email to the closest products we have in our product catalogue. Tell me what the client is looking for and the ids of the matching products.

    Client email: {state.email_content}

    Product catalogue: {product_characteristics}
    """

    response = await llm.ainvoke(product_match_prompt) # AIMessage type

    return Command(
        update={"messages": [AIMessage(content=response.content)]},    # Adds to messages not replace. We are not using [response] because we don't want to save the response metadata to the state
        goto="check_inventory_llm_call"
    )

async def find_customer_order(state: EmailAgentState): # -> Command[Literal["check_inventory_llm_call"]]:
    """
    Prompt the LLM to extract the the delivery_ids or tracking_numbers provided by the customer.
    """
    # Identify what the product being searched for is by checking product features database
    # asyncio.run(get_shoe_characteristics()) is wrong for asynchronous programming

    product_characteristics = await get_customer_open_deliveries(state.customer_id)  

    product_match_prompt = f"""
    Identify the delivery ids or tracking numbers in the client's email. The customer must explicitly mention that it is a delivery id or a tracking number, if not mentioned, ignore it

    Client email: 
    {state.email_content}
    """

    structured_llm = llm.with_structured_output(DeliveryInfo)

    response = await structured_llm.ainvoke(product_match_prompt) # AIMessage type

    print(response)
    exit(0)

    return Command(
        update={"messages": [AIMessage(content=response.content)]},    # Adds to messages not replace. We are not using [response] because we don't want to save the response metadata to the state
        goto="check_inventory_llm_call"
    )

async def check_inventory_llm_call(state: EmailAgentState):
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
    response = await llm_check_inventory_with_tools.ainvoke(
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
    
async def check_inventory_tool_node(state: EmailAgentState):
    """
    This node performs the tool calls for get_inventory_stock and get_incoming_deliveries
    """
    tool_call_message = state.messages[-1].tool_calls

    message_result = []
    context_result = []

    for tool_call in tool_call_message:
        tool = tools_by_name[tool_call["name"]]
        observation = await tool.ainvoke(tool_call["args"])

        message_result.append(ToolMessage(content=observation, tool_call_id=tool_call["id"]))
        context_result.append(observation)

    return {"messages": message_result,
            "context": context_result}

async def write_response(state: EmailAgentState) -> Command[Literal["send_response_to_backend"]]:
    """
    Write email to the customer that achieves the objective and responds to the customer email
    """

    classification = state.classification
    email_topic = 'unknown' if classification.topic == None else classification.topic

    email_objective = {
        "other": None,
        "product_availability_inquiry": "The customer has asked about the availability of specific products. Tell the customer that these products are available",
        "product_recommendation_request": "The customer has asked for a recommendation based on certain criteria. Tell the customer that these products are the closest match to what they are looking for and their availability"
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

    email_response = await llm.ainvoke(draft_prompt)

    # Get the summary with 4.1 micro
    summary_instructions = "You are an expert summarizer that summarizes the content in an email."
    email_response_summary = await summary_llm.ainvoke(
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

async def send_response_to_backend(state: EmailAgentState):
    """
    Send the following to the backend:
    - Case ID
    - Response
    - Response summary
    - Context
    - Actions
    
    """
    print(state.email_response_summary)
    print(state.email_response)
    print(state.context)
    print(state.actions)

    return {}


from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import RetryPolicy
workflow = StateGraph(EmailAgentState)

# Add nodes with appropriate error handling
workflow.add_node("classify_email", classify_email)
workflow.add_node("find_closest_product", find_closest_product)
workflow.add_node("find_customer_order", find_customer_order)

workflow.add_node("check_inventory_llm_call", check_inventory_llm_call)
workflow.add_node("check_inventory_tool_node", check_inventory_tool_node)
workflow.add_node("write_response", write_response)
workflow.add_node("send_response_to_backend", send_response_to_backend)



# Add only the essential edges
workflow.add_edge(START, "classify_email")

workflow.add_edge("find_closest_product", "check_inventory_llm_call")
workflow.add_conditional_edges(
    "check_inventory_llm_call",
    conditional_edge_check_inventory,
    ["check_inventory_tool_node", "write_response"]
)
workflow.add_edge("check_inventory_tool_node", "check_inventory_llm_call")
workflow.add_edge("write_response", "send_response_to_backend")
workflow.add_edge("send_response_to_backend", END)

# Compile with checkpointer for persistence, in case run graph with Local_Server --> Please compile without checkpointer
memory = MemorySaver()
app = workflow.compile()

async def main():
        config = {"configurable": {"thread_id": "1"}} # Enables checkpointing for memory, hitl, etc...
        result = await app.ainvoke(initial_state)
        print(f"Graph exited")

if __name__ == '__main__':

    product_availability_email = """
        Dear Sir/Madam,

        I would like to inquire the availability of red leather shoes

        Regards,
        Michael
    """
    delivery_delay_email = """
    Dear sir/madam,

    I would like to ask why my deliveries with id 123 and 444 have been delayed 

    """
    # Test the agent
    initial_state = {
        "customer_name": "Michael",

        "customer_id": 1,

        "case_id": 1000,

        "email_content": delivery_delay_email 
    }
    
    asyncio.run(main())

    # Reset memory
    #delete_customer_support_history("customer_123", "1000")