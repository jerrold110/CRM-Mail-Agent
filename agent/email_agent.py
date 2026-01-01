import os
from dotenv import load_dotenv

load_dotenv()


from typing import TypedDict, Literal

# Define the state
class EmailClassification(TypedDict):
    intent: Literal["inquiry", "recommendation", "dispute", "other"]
    topic: Literal["product", "transaction", "billing", "delivery", "other"]
    summary: str

class ProductCharacteristics(TypedDict):
    product_id: str
    color: str
    material: str
    brand: str

class EmailAgentState(TypedDict):
    # Raw email data excluding email subject
    email_content: str
    sender_email: str
    customer_id: int

    # Classification result
    classification: EmailClassification | None

    # Raw search/API results
    customer_history: dict | None  # Raw customer data from CRM

    # Generated content
    draft_response: str | None

# Define the Nodes
from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt, Command, RetryPolicy
from langchain_openai import ChatOpenAI
from langchain.messages import HumanMessage

llm = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0)


def classify_email(state: EmailAgentState) -> Command[Literal["draft_response"]]:
    """
    Use LLM to classify email intent and topic, then route accordingly
    """

    # Create structured LLM that returns EmailClassification dict
    structured_llm = llm.with_structured_output(EmailClassification)

    # Format the prompt on-demand, not stored in state
    classification_prompt = f"""
    Analyze this customer email and classify it by intent, topic, and provide a summary
    intent and topic have to be restricted to the values:
    intent: inquiry, recommendation, dispute, other
    topic: product, transaction, billing, delivery, other

    Email: {state['email_content']}

    """

    # Get structured response directly as dict
    classification = structured_llm.invoke(classification_prompt)

    # Determine next node based on classification
    if classification['intent'] == 'inquiry':
        if classification['topic'] == 'product':
            goto = "draft_response"
        elif classification['topic'] == 'product_availability':
            goto = "draft_response"
        elif classification['topic'] == 'transaction':
            goto = "draft_response"
        elif classification['topic'] == 'billing':
            goto = "draft_response"
        elif classification['topic'] == 'delivery':
            goto = "draft_response"
        elif classification['topic'] == 'other':
            goto = "draft_responsew"
    else:
        goto = "draft_response"

    # Store classification as a single dict in state
    return Command(
        update={"classification": classification},
        goto=goto
    )
import asyncio
import asyncpg

def product_stock_assessment(state: EmailAgentState) -> Command[Literal["draft_response"]]:
    """
    Search current and future product inventories
    """
    # Identify what the product being searched for is by checking product features database
    async def run():
        conn = await asyncpg.connect(user='admin', password='admin',
                                    database='company', host='127.0.0.1')
        values = await conn.fetch(
            'SELECT * FROM shoe_characteristics'
        )

        await conn.close()
        shoe_char_data_str = "product_id,color,material,brand,description\n"
        for row in values:
            row_data = []
            row_data.append(str(row['product_id']))
            row_data.append(row['color'])
            row_data.append(row['material'])
            row_data.append(row['brand'])
            row_data.append(row['description'])
            row_data_str = ",".join(row_data) + "\n"
            shoe_char_data_str += row_data_str

        return shoe_char_data_str
    
    values = asyncio.run(run())

    # Search current stock inventory database

    # If above product cannot be found, search incoming stock inventory database

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
workflow.add_node("draft_response", draft_response)
workflow.add_node("send_reply_to_backend", send_reply_to_backend)

# Add only the essential edges
workflow.add_edge(START, "classify_email")
workflow.add_edge("classify_email", "draft_response")
workflow.add_edge("draft_response", "send_reply_to_backend")
workflow.add_edge("send_reply_to_backend", END)

# Compile with checkpointer for persistence, in case run graph with Local_Server --> Please compile without checkpointer
memory = MemorySaver()
app = workflow.compile(checkpointer=memory)

# Test the agent
initial_state = {
    "email_content": """
    Dear Sir/Madam,

    I would like to inquire if you have any red leather shoes in stock.

    Regards,
    Customer123
    """,
    "sender_email": "customer@example.com",
    "email_id": "email_123",
}

# Run with a thread_id for persistence
config = {"configurable": {"thread_id": "customer_123"}}
result = app.invoke(initial_state, config)
print(f"Email sent successfully!")