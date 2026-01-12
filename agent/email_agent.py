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
    email_summary: str

class EmailResponse(TypedDict):
    observation: str
    context_source: str

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
    inventory_context: str | None
    transaction_context: str | None

    # Email response
    response: EmailResponse | None
    actions: list[str] | None


# Define the Nodes of the agent

from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt, Command, RetryPolicy
from langchain_openai import ChatOpenAI
from langchain.messages import HumanMessage, SystemMessage, AIMessage
import asyncio

from langchain.tools import tool

llm = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0)


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
    if classification['intent'] == 'product_availability_inquiry':
        goto = "find_closest_product"
    elif classification['intent'] == 'product_recommendation_request':
        goto = "find_closest_product"
    else:
        goto = "other"

    # Update state data and select the next node (goto)
    return Command(
        update={"classification": classification},
        goto="find_closest_product"
    )


def find_closest_product(state: EmailAgentState) -> Command[Literal["check_inventory"]]:
    """
    Prompt the LLM to determine if there if there are products that matches the description(s) provided by the customer.
    """
    # Identify what the product being searched for is by checking product features database
    product_characteristics = asyncio.run(get_shoe_characteristics())

    product_match_prompt = f"""
    Match the products the client is looking for in their email to the closest products we have in our product catalogue. Tell me what the client is looking for and their product_id, nothing more.

    Client email: {state['email_content']}

    Product catalogue: {product_characteristics}
    """

    response = llm.invoke(product_match_prompt)
    ai_message = [AIMessage(content=response.content)]

    return Command(
        update={"messages": state["messages"]},
        goto="check_inventory"
    )

from _db_read import get_shoe_characteristics, get_inventory_stock, get_incoming_deliveries

tools = [get_inventory_stock, get_incoming_deliveries]
tools_by_name = {tool.name: tool for tool in tools}

llm_with_tools = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0).bind_tools(tools)

def llm_call_check_inventory(state: EmailAgentState):
    """ 
    LLM decides what inventory check tool calls to make
    """
    llm_closest_product_findings = state['messages'][-1].content # the most recent message
    exit(0)
    system_message = """
    You are a helpful assistant that checks the availability of products by checking the inventory and incoming shipments of product(s) the client is inquiring about by product_id.
    """

    response = llm_with_tools.invoke(
        [SystemMessage(content=system_message)] + [llm_closest_product_findings]
    )
    print(response)
    exit(0)
    
    return {
        "messages": [AIMessage(response.content)]
    }
    
def check_inventory_tool_node(state: EmailAgentState):
    """
    This node performs the tool calls for get_inventory_stock and get_incoming_deliveries
    """
    print(state)
    # result = []
    # for tool_call in state["messages"][-1].tool_calls:
    #     tool = tools_by_name[tool_call["name"]]
    #     observation = tool.invoke(tool_call["args"])
    #     result.append(ToolMessage(content=observation, tool_call_id=tool_call["id"]))


def draft_response(state: EmailAgentState) -> Command[Literal["send_reply_to_backend"]]:
    """Generate response using context and route based on quality"""

    classification = state.get('classification', {})

    # Format context from raw state data on-demand
    context_sections = []

    # if state.get('search_results'):
    #     # Format search results for the prompt
    #     formatted_docs = "\n".join([f"- {doc}" for doc in state['search_results']])
    #     context_sections.append(f"Relevant documentation:\n{formatted_docs}")

    # if state.get('customer_history'):
    #     # Format customer data for the prompt
    #     context_sections.append(f"Customer tier: {state['customer_history'].get('tier', 'standard')}")

    # Build the prompt with formatted context
    draft_prompt = f"""
    Draft a response to this customer email:
    {state['email_content']}

    Email intent: {classification.get('intent', 'unknown')}
    Email topic: {classification.get('topic', 'unknown')}

    Guidelines:
    - Tell them the intent and topic of their email
    - Be professional and helpful
    - Address their specific concern
    - Use the provided documentation when relevant
    """

    response = llm.invoke(draft_prompt)

    # Route to appropriate next node
    goto = "send_reply_to_backend"

    return Command(
        update={"draft_response": response.content},  # Store only the raw response
        goto=goto
    )
    
def send_reply_to_backend(state: EmailAgentState) -> dict:
    """Send the email response"""
    print(f"Sending reply: {state['draft_response']}...")
    return {}


# Wire it all together

from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import RetryPolicy

workflow = StateGraph(EmailAgentState)

# Add nodes with appropriate error handling
workflow.add_node("classify_email", classify_email)
workflow.add_node("find_closest_product", find_closest_product)
workflow.add_node("check_inventory", check_inventory)
workflow.add_node("check_inventory_tool_node", check_inventory_tool_node)

#workflow.add_node("draft_response", draft_response)
#workflow.add_node("send_reply_to_backend", send_reply_to_backend)


# Add only the essential edges
workflow.add_edge(START, "classify_email")
workflow.add_edge("classify_email", "find_closest_product")
workflow.add_edge("find_closest_product", "check_inventory")
workflow.add_edge("check_inventory", "check_inventory_tool_node")
workflow.add_edge("check_inventory_tool_node", END)

# Compile with checkpointer for persistence, in case run graph with Local_Server --> Please compile without checkpointer
memory = MemorySaver()
app = workflow.compile(checkpointer=memory)

# Test the agent
initial_state = {
    "sender_email": "customer@example.com",
    "email_id": "email_123",
    "email_content": """
    Dear Sir/Madam,

    I would like to inquire if you have any red leather shoes.

    Regards,
    Customer123
    """
}


config = {"configurable": {"thread_id": "customer_123"}} # Run with a thread_id for persistence
result = app.invoke(initial_state, config)
print(f"Email sent successfully!")