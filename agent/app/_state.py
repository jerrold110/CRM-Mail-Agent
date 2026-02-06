from typing import TypedDict, Literal, Annotated
from pydantic import BaseModel, Field
import operator
from langchain.messages import AnyMessage

# Define the state
class EmailCharacteristics(BaseModel):
    topic: Literal["transaction_inquiry", "product_availability_or_recommendation", "delivery_delay", "billing_dispute", "other"]
    urgency: Literal["low", "medium", "high", "urgent"]
    summary: str

class DeliveryInfo(BaseModel):
    tracking_number: list[str] = Field(default_factory=list)

class EmailAgentState(BaseModel):
    # Test status
    send_backend: bool = Field(default=True)

    # Email data 
    customer_name: str
    customer_id: int
    case_id: int
    email_content: str 
    email_summary_history: str | None = None # Used when Email history provides context; such as when answering a request for more information to process action

    # Email characteristics. Add more fields as use-cases increase
    classification: EmailCharacteristics | None = None
    closest_product_sql_query: str = Field(default="")
    delivery: DeliveryInfo | None = None 

    # LLM messages. Follow up actions should be more deterministic after the initial observation steps by the agent. These actions use specific state fields for follow-up actions
    # Refer to message with .content
    messages: Annotated[list[AnyMessage], operator.add] = Field(default_factory=list)

    # Email response
    email_response: str = Field(default="")
    email_response_summary: str = Field(default="")
    # Context gathered from system. Will be included in source reflected to user.
    context: Annotated[list[str], operator.add] = Field(default_factory=list)
    # Actions to be taken after human review
    actions: Annotated[list[dict], operator.add] = Field(default_factory=list)


