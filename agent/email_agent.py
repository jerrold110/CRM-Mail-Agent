import os
from dotenv import load_dotenv
load_dotenv()

from typing import TypedDict, Literal, Annotated
from langchain.messages import AnyMessage
import operator

# Define the state
class EmailCharacteristics(TypedDict):
    topic: Literal["transaction_inquiry", "product_availability_inquiry", "product_recommendation_request", "delivery_complaint", "billing_dispute", "other"]
    urgency: Literal["low", "medium", "high", "critical"]
    summary: str

class EmailAgentState(TypedDict):
    # Email characteristics
    classification: EmailCharacteristics | None

    # Email data 
    customer_name: str
    customer_id: int
    email_content: str
    email_summary_history: str | None # Used when Email history provides context; such as when answering a request for more information to process action

    # LLM messages. Follow up actions should be more deterministic after the initial observation steps by the agent. These actions use specific state fields for follow-up actions
    # Refer to message with .content
    messages: Annotated[list[AnyMessage], operator.add]

    # Context gathered from system. Will be included in source reflected to user.
    context: Annotated[list[str], operator.add] | None

    # Email response
    email_response: str | None
    email_response_summary: str | None
    actions: dict | None    # To be JSON string


# Define the Nodes of the agent

from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt, Command, RetryPolicy
from langchain_openai import ChatOpenAI
from langchain.messages import HumanMessage, SystemMessage, AIMessage, ToolMessage
import asyncio

from langchain.tools import tool

llm = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0.5)

summary_llm = ChatOpenAI(
    model="gpt-4.1-nano",
    temperature=0.5)

from _db_read import get_shoe_characteristics, get_product_availability

tools = [get_product_availability]
tools_by_name = {tool.name: tool for tool in tools}

llm_check_inventory_with_tools = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0.5).bind_tools(tools)

def classify_email(state: EmailAgentState) -> Command[Literal["find_closest_product"]]:
    """
    Use LLM to classify email topic and urgency, then route accordingly
    """

    structured_llm = llm.with_structured_output(EmailCharacteristics)

    # Format the prompt on-demand, not stored in state
    classification_prompt = f"""
    Analyze this customer email and classify it

    Email: {state['email_content']}

    Provide classification including topic, urgency, and provide a summary.
    """

    # Get structured response directly as dict
    classification = structured_llm.invoke(classification_prompt)

    # Determine next node based on classification
    if classification['topic'] == 'product_availability_inquiry':
        goto = "find_closest_product"
    elif classification['topic'] == 'product_recommendation_request':
        goto = "find_closest_product"
    else:
        goto = "other"
    
    print(classification['summary'])

    # Update state data and select the next node (goto)
    return Command(
        update={"classification": classification},
        goto=goto
    )


def find_closest_product(state: EmailAgentState) -> Command[Literal["check_inventory_llm_call"]]:
    """
    Prompt the LLM to determine if there if there are products that matches the description(s) provided by the customer.
    """
    # Identify what the product being searched for is by checking product features database
    product_characteristics = asyncio.run(get_shoe_characteristics())

    product_match_prompt = f"""
    Match the products the client is looking for in their email to the closest products we have in our product catalogue. Tell me what the client is looking for and the ids of the matching products.

    Client email: {state['email_content']}

    Product catalogue: {product_characteristics}
    """

    response = llm.invoke(product_match_prompt)

    return Command(
        update={"messages": [AIMessage(content=response.content)]},    # Adds to messages not replace. Must use .content
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
    - Instruction
    - Tool call instructions
    - Tool call result 1,2,3...n
    
    It will append a new message that summarizes the findings and has no more tool call instructions
    """
    response = llm_check_inventory_with_tools.invoke(
        [SystemMessage(content=agent_message)] + state['messages']
    )

    return {
        "messages": [response] 
    }


def conditional_edge_check_inventory(state: EmailAgentState) -> Literal["check_inventory_tool_node", "write_response"]:
    """Decide if we should continue the loop or stop based upon whether the LLM made a tool call"""

    messages = state["messages"]
    last_message = messages[-1]
    

    if last_message.tool_calls:
        return "check_inventory_tool_node"
    
    return "write_response"
    
def check_inventory_tool_node(state: EmailAgentState):
    """
    This node performs the tool calls for get_inventory_stock and get_incoming_deliveries
    """
    tool_call_message = state["messages"][-1].tool_calls

    message_result = []
    context_result = []

    for tool_call in tool_call_message:
        tool = tools_by_name[tool_call["name"]]
        observation = tool.invoke(tool_call["args"])

        message_result.append(ToolMessage(content=observation, tool_call_id=tool_call["id"]))
        context_result.append(observation)

    return {"messages": message_result,
            "context": context_result}


def write_response(state: EmailAgentState): #-> Command[Literal["send_response_to_backend"]]:
    """
    Write email to the customer that achieves the objective and responds to the customer email
    """

    classification = state.get('classification', {})
    email_topic = classification.get('topic', 'unknown')

    email_objective = {
        "other": None,
        "product_availability_inquiry": "The customer has asked about the availability of specific products. Tell the customer that these products are available",
        "product_recommendation_request": "The customer has asked for a recommendation based on certain criteria. Tell the customer that these products are the closest match to what they are looking for and their availability"
    }

    if state.get('context'):
        formatted_context = "\n".join([f"- {doc}" for doc in state['context']])

    # Build the prompt with formatted context
    draft_prompt = f"""
    {email_objective}.
    The customer's name is: {state['customer_name']}
    Draft a reply to this customer email:
    {state['email_content']}

    Relevant context:
    {formatted_context}

    Guidelines:
    - Be professional and helpful
    - Address their specific concern
    - Use the provided context when relevant
    - Sign off the email as Customer Service Team
    """
    print(state['classification'])
    email_response = llm.invoke(draft_prompt)
    print("-----------------------------------------")
    print(email_response.content)

    summary_instructions = "You are an expert summarizer that summarizes the content in an email."
    email_response_summary = summary_llm.invoke(
        [
            SystemMessage(content=summary_instructions),
            HumanMessage(content=email_response.content)
        ]
    )

    return Command(
        update={"messages": [response],
                "email_response": email_response,
                "email_response_summary": email_response_summary},
        goto="send_reponse_to_backend"
    )


# Wire it all together

from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import RetryPolicy
workflow = StateGraph(EmailAgentState)

# Add nodes with appropriate error handling
workflow.add_node("classify_email", classify_email)
workflow.add_node("find_closest_product", find_closest_product)
workflow.add_node("check_inventory_llm_call", check_inventory_llm_call)
workflow.add_node("check_inventory_tool_node", check_inventory_tool_node)
workflow.add_node("write_response", write_response)

# Add only the essential edges
workflow.add_edge(START, "classify_email")
workflow.add_edge("classify_email", "find_closest_product")
workflow.add_edge("find_closest_product", "check_inventory_llm_call")
workflow.add_conditional_edges(
    "check_inventory_llm_call",
    conditional_edge_check_inventory,
    ["check_inventory_tool_node", "write_response"]
)
workflow.add_edge("check_inventory_tool_node", "check_inventory_llm_call")

# Compile with checkpointer for persistence, in case run graph with Local_Server --> Please compile without checkpointer
memory = MemorySaver()
app = workflow.compile(checkpointer=memory)

# Test the agent
initial_state = {
    "customer_name": "Michael",
    "customer_id": "email_123",
    "email_content": """
    Dear Sir/Madam,

    I would like to inquire if you have any red leather shoes.

    Regards,
    Michael
    """
}


config = {"configurable": {"thread_id": "1"}} # Enables checkpointing for memory, hitl, etc...
result = app.invoke(initial_state, config)
print(f"Graph exited")