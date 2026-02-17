# **CRM-Mail-Agent**
## Introduction
A fullstack agent system for an athletic footwear Ecommerce business that responds to emails and takes appropriate actions with *human-in-the-loop and agent memory* and a **robust agent evaluation framework** (details in Agent evaluation framwork.md). 

The human staff member accesses the front-end and reviews the agent's repliy & actions while also providing the context (observations) the agent has gathered that justifies its response/actions (such as the observed data in the database). The human approves or edits the actions, and the system updates the agent's memory after approval. Langfuse is used for monitoring.

- Fully integrated memory system with context compression that can respond to emails in context while reducing token cost
- Answer product inquiries, recommend products, check stocks and incoming deliveries
- Respond to late delivery complaints, check delivery histories, credit fee refunds, provide coupons for retention
- HITL for all actions and responses, agent runs asynchronously in real-time through a task queue
- Data authorisation at the app level so no breach of data when responding to client

## System diagram (high level)
![System diagram](images/overallSystem.png "Optional title")

1. Customer sends email to Customer Support
2. CRM receives email, sends event to Agent
3. Agent receives event, goes through entire Agent workflow involving data collection from internal systems
4. Agent prepares response and sends it to CRM
5. CRM front-end displays **email with a list of actions to take and contextual data gathered from internal systems** to internal staff
6. Staff reviews email draft and agent's actions, makes edits (optional), approves email and actions 
7. CRM sends AI prepared email response to client and takes actions

## Agent memory system
![System diagram](images/memory.png "Optional title")

This diagram shows how the agent's memory is updated and accessed at each stage of the email conversation between Customer service and the Customer. The memory stores summaries of emails so as to reduce token ingestion/output and save on cost when memory is used.

## Agent workflow diagram
![System diagram](images/agentGraph.png "Optional title")

### First workflow:
1. Obtain conversation history from memory 
2. Classify email by topic and urgency
3. If multiple requests, urgent, or no reply needed route to "other" then "human escalation"

From the web application that customer use to send requests to the customer service backend, customers should only include 1 request per support case. Thus emails with multiple requests are edge cases and will be few in number - while an agent could handle multiple requests with multi-agent system this introduces a vast amount of complexity that will be difficult to evaluate

### Product availability inquiry or product recommendation request:
1. Create a SQL query based on the content of the email to filter results (size, color, brand, etc...), if suitable
2. Query database. Match returned data to customer's request and identify product_ids
3. Check stocks of these products, if empty, check incoming deliveries
4. Write response to customer that these products are the closest match to what they are looking for and what their availability is (or when they will be available if no stocks)

### Late delivery complaint:
1. Identify the tracking number the customer is referring to, route to response generation requesting for number to be provided if not available
2. Check each of the tracking numbers are open deliveries under the customer's id, if none found found, route to response generation saying that there is no such open delivery with the tracking number(s) provided
3. If matched, calculate the numbers of days late/not late, credit devliery fee refunds based on number of days late. If delivery is late and there was a late delivery in the last 60 days of this customer, provide coupon for expedited delivery for customer to use at the next order.
4. Write response to customer detailing the status of each open delivery's tracking number and the actions taken for that delivery

Final step:
Send Case ID, email response, email response summary, context, and actions to backend for Human-in-the-loop evaluation.

## Security
First workflow:
- Unclear/urgent/mixed-request (edge cases)/no-reply-needed emails are routed to human for evaluation (refer to prompt in email_agent.py)
- Emails over 2500 charaters are not sent to the agent and handled manually at the backend. A customer might send an email with hundreds of identifiers or descriptions to extract data or cause system overload
- Emails with repeated >3 request within the same case (same case_id) are routed to human evaluation because >3 similar requests in an email conversation means the agent is not effectively handling the customer service request

Product recummendation/availability workflow:
- System returns a maximum of 500 database results (adjustable) in case a customer is attempting a data leak attack to obtain inventory of all items (e,g,: "I want to find out about the available stocks of all your shoes"). Repeated requests are flagged by the agent

Late delivery complaint workflow:
- Database read results are filtered on the customer's ID at the application level so LLM will never see data that does not belong to the client attached to the case it is handling to prevent data leakage or customer attacks
- 

## Observability and diagnosing
![System diagram](images/Langfuse.png "Optional title")
LangFuse has built-in support for the LangChain ecosystem so integration is easy as pie. Each LangGraph call is monitored by Langfuse at the Trace/Session/User level and can be used for further analysis.
Trace data:
- Nodes traversed in graph 
- State input and output
- Token count
- Attempt number
- Overall latency
- Timestamp
- Cost/tokens/latency/prompt of each API call

Does not trace:
- Terminal output at each Run of LangGraph

Identifier data captured at each trace:
- Agent job ID
- Case ID
- Customer ID
- Additional metadata

## Error handling 

Add diagram.
Error handling occurs at FastAPI, Celery, Langgraph. 

Retries are handled at Celery/LangGraph. In the event a job run fails completely, the error messages are reflected in the system logs, LangFuse (partially), and the status/description of the failed job is sent back to the backend.

FastAPI sends back apprioriate HTTP codes to indicate errors.

## Tech framework of agent streaming
This Agent is a streaming system that runs asynchronously. It includes a task queue for rate limiting to prevent system overload, connection pooling to prevent database connection bottleneck/errors, and the message broker is Redis but we are switching to Kafka.

Connection pooling is at the celery worker level, so all the tasks run by the same worker share the connection pool. Job ID is created at the Rest API endpoint and its is is sent as a response to the backend with HTTP code 202.

### In the first design we use:
- Celery, FastAPI, Redis as the broker

![System diagram](images/tech1.png "Optional title")

### In the improved design we use:
- Celery, Kafka

This is because Kafka has less points of failure as it handles message transmission and endpoints, uses TCP instead of HTTP, and buffers in disk instead of in memory like Redis which is prone to overload under system stress.

![System diagram](images/tech2.png "Optional title")

# **To do list**
- Send update request to delivery team on "Late delivery complaint" workflow
Create a more graceful workflow for multiple requests (multi-agent system), but requires robust evaluation.
- Implement terminal output log storage (possibly with ELK stack or AWS cloudwatch) as Langfuse does not trace the full terminal output which is instrumental in debugging errors
- Move LangFuse callback handler instantiation to the Celery Entrypoint so that the callback handler is reused at the worker level, currently at agent_entrypoint.py. Until it is, Langfuse tracing is unsuitable for production
- Add email categorisation data to LangFuse metadata