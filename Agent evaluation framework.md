# **Agent evaluation framework**

This document outlines the approach to evaluating the CRM email agent system by describing evaluation approach, the functions of the agentic system that will undergo evaluation, how they will be evaluated

# Evaluation methodology
Construct evaluation set that defines input state and expected outcome. 
- LLM mutatations to introduce ambiguity/inject rare idioms/mutate working examples. 
- Use LLM to generate distributional interpolation (e.g., Blend two intents to create an ambiguous request).

Write functions to read from a structured evaluation set to test tools/planning/evaluation that output metric scores


Load all rows into internal database (Postgres). Instead of loading rows per evaluation which would cause evaluation to be unwieldy
Per each evaluation, load accompanying agent memory, run test, remove memory: 

# What functions of the system to evaluate
The langGraph agent is made up of nodes that use state to contain input state. Each node can be evaluated in isolation, and segments of the graph composed of several nodes/edges can be evaluated as a discrete system.

**Tool evaluation**
- get_comprehensive_product_query
    - Converts product email into sql query for single or multiple products. If email question cannot be understood, returns CANNOT_ANSWER
- match_closest_product
    - matches database output from SQL query output with customer query to identify matching product(s)
- get_product_availability
    - Deterministic tool, checks company table for a product_id, if none, checks incoming_deliveries table
- find_customer_order
    - Extracts relevant tracking numbers from a customer's email
- check_deliveries
    - Deteriministic tool. Checks customer's open deliveries, checks for matches, returns string responses in context and actions (python lists) to take (that a tool would use, but HITL is required for all actions in this system)
- write_response
    - generates an email response based on context, email_classification, and email

**Planning evaluation**
- classify_email with memory
    - Classification
    - Urgency
- check_inventory_llm_call
    - Plans what tool calls (get_product_availability) to make and what parameters
    - Not very useful in this project as there is only one tool to call. More beneficial for projects with multiple tools at once decision point.

**Holistic evaluation**

Holistic evaluation involves testing the entire stack of the agent's workflow: **Node input/output, tool invocation/input/output, state messages/context/actions, memory configurations**. *While it would be ideal to test every aspect of the full stack, evaluation will become unwieldy as the output of every function will have to be verified. So we should omit what has already been thorougly tested in above evaluations and validate the most salient aspects of the system that have not been validated yet.*
- What nodes were traversed in the graph?
- Tool invocations (without considering input and output)
- State messages/context/action
    - Are all expected context included? (Especially important for write_response)
    - Are correct actions taken?
    - Is message history correct?
- Testing holistically with different memory configurations
    - No prior conversation history
    - Conversation history requesting further information
    - Conversation history about unrelated matters or matters that should be in a separate case_id due to customer error

# Evaluation metrics for each system

## get_comprehensive_product_query
This is an llm invocation. Use an LLM-judge to return a score of 0-1 and an explanation of the score. 

## match_closest_product
This input state is an email product query and a string that represents tabular output from a database. The LLM extracts the matching product IDs and outputs a list of product ids that match the query. Measure with Precision/Recall

Since SQL query accuracy is not an evaluation criteria of this function, this test will use a standard database output (the entire database) which with to recommend from based on the customer's input query. This does not deteriorate the quality of the system's capacity to make precise recommendations, but rather increases it because there are more opportunities for errors. **This should include nuanced, strange, or even contradictory requests from clients**

## get_product_availability
This is a deterministic function, input is simply data in SQL and the output is a string. Measure with Accuracy to see if strings are correct.

## find_customer_order
The output is a list of tracking numbers extracted from an email. Measure with precision/recall

## check_deliveries
This is a deterministic function that outputs fixed strings into lists, input is simply data in SQL. Measure context and accuracy lists with precision/recall

### write_response
This function input is: **context, email classification, customer email**. Validate that the output is not hallucinating by comparing the context against the final message with llm-judge (Deepeval/RAGAS). 

The email that has been generated will be compared against a model email that takes into context all the bold items above, and can be evaluated against the model email for semantic similarity with ROUGE/METEOR/Bertscore (I prefer BertScore)

## classify_email with memory
This is a structured llm invocation.

Classification
- This uses accuracy to determine how many emails were correctly classified

Urgency
- This evaluate the system's ability to classify emails as Urgent using Precision/Recall, as this is the only important category.

## check_inventory_llm_call
This is an llm invocation planner that decides what tools to call and what parameters to call them with.

## Holistic evaluation
Evaluating the system holistically for a single test case involves a representative workflow in JSON similar to the other test cases.