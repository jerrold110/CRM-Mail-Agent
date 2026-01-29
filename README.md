# **CRM-Mail-Agent**
A straightforward agent system that handles customer support emails where system complexity is reduced to facilitate operational stability.
- Fully integrated memory system with context compression that can respond to emails in context while reducing token cost

- Answer product inquiries, recommend products, check stocks and incoming deliveries
- Respond to late delivery complaints, check delivery histories, credit fee refunds, provide coupons for retention
- HITL for all actions and responses, agent runs asynchronously in real-time
- Data authorisation at the app level so no breach of data when responding to client

## System diagram
![System diagram](images/overallSystem.png "Optional title")

1. Customer sends email to Customer Support
2. CRM receives email, sends event to Agent
3. Agent receives event, goes through entire Agent workflow involving data collection from internal systems
4. Agent prepares response and sends it to CRM
5. CRM displays email with a list of actions taken and contextual data gathered from internal systems to internal staff
6. Staff reviews email draft, approves email
7. CRM sends AI prepared email response to client

## Agent memory system
![System diagram](images/agentProcess.png "Optional title")

## Agent diagram
![System diagram](images/agentGraph.png "Optional title")

## Python frameworks
![System diagram](images/pythonLibraries.png "Optional title")
