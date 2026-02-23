<style>
  p {
    font-size: 16px;
  }
</style>

# **Agent evaluation**
Evaluating Agentic systems is a cruicial step in agent development necessary to determine if a system meets its intended goals and can handle the complexities of real-world function, without which we would just be working in the dark with no idea of how well it performs. Similar to evaluating machine learning models and traditional software systems, we have to define clear and relevant metrics for evaluating Agents that allow us to measure its performance. Quantitative metrics include accuracy, precision, recall, latency, Rouge, BLEU, and BertScore, and LLM-judge scores. Qualitative measures can be used to measure aspects difficult to quantify quantitatively such as user-satisfaction. This project will focus on quantitative metrics since they can be automated.

This document outlines the approach that will be used to evaluate the CRM email agent system by describing its methodology, the functions of the agentic system that will be evaluated, and how each of those functions will be evaluated.

# Methodology
There are many constituents that create a fully functioning Agentic system and we can evaluate them individually or in groups:
- **Component evaluation**: Tools, planning, memory
- **Holistic evaluation**: End-to-end scenarios, Consistency, Hallucination

Under component evaluation, we can evaluating tools, memory, and planning with standard metrics like recall/precision/accuracy with standard and unusual inputs. Within the context of this project, we want to test that tools are performing correctly, planning modules are making the right tool calls with the right parameters, and that memory is stored/retrieved correctly and leads to the correct outcomes. 

Under holistic evaluation, we want to test the agentic system as a whole ensuring that all components are working together seamlessly. This is similar to integration testing. We want to define test cases that involve the entire stack of the agentic system: such as multi-turn conversations that involve interpreting user intent, planning, and tool calls. Consistency ensures that the agent's inputs are aligned with its inputs over diverse scenarios, extended exchanges, and repeated testing. Hallucination is revelant because this Agent system stores observations gathered throughout the lifespan of its workflow in its state under the "context" attribute, and uses these observations to generate an email response. 

## Evaluation approach
The first step is to decide on a structured, and scalable format to define the evaluation sets that define input state and expected output states. According to Miahael Albada in 'Building Applications with AI Agents', he recommends the json format to create evaluation sets. This format is highly nested and allows us to test several things at once in a single example and scales well for multivarious evaluations, examples provided in `agent/evaluation`. In an enterprise, domain experts will be widely utilised to create and manage high quality evaluation sets. AI can be used to mimic and generate more evaluation examples with modifications based on the initial ones provided by experts.
- LLM mutatations to introduce ambiguity/inject rare idioms/mutate working examples. 
- Use LLM to generate distributional interpolation (e.g., Blend two intents to create an ambiguous request).

In this project, I have followed the same approach of manually defining a few examples and using AI to generate a large number of variations making up the majority of the data in the evaluation sets. Based on the output from the agent, we can compare it with the expected output in the evaluation sets and calculate quantitative metrics to understand the system's performance. I have written a simple framework with python to makes these comparisons and calculate the metrics in `/agent/evaluation` using python files, json files, and jupyter notebooks.

### Loading data for tests
Data systems include the internal database and the agent's memory (Postgresql database). Loading the rows of data for the internal database per evaluation test case would cause unwieldy due to the amount of data that as to be added, so the entirety of  this data will be loaded beforehand. Memory data will be loaded per evaluation, and removed after the test is complete due to its smaller size (Agent memory only consists of conversation history in the current state of this agent, but can easily be extended for the development of future platform features such as personalisation and grievance handling).

# Evaluating at the component and holistic level
The langGraph agent is made up of nodes that use state to contain input state. Each node can be considered a tool and evaluated in isolation, and segments of the graph composed of several nodes/edges can be evaluated as a discrete system. This section categorises the different functions and describes what they do.

**Tool and memory evaluation**
- classify_email after retrieving memory. Emails that are dangerous/unclear/have multiple topics/have >3 repeated requests in a row are routed to urgent. Emails that cannot be classified under a topic, or do not require a response are routed to Other. 
    - Topic: "transaction_inquiry", "product_availability_or_recommendation", "delivery_delay", "billing_dispute", "other"
    - Urgency: "low", "medium", "high", "urgent"
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
- check_inventory_llm_call
    - Plans what tool calls (get_product_availability) to make and what parameters
    - Not very useful in this project as there is only one tool to call. More beneficial for projects with multiple tools at once decision point.

**End-to-end scenario evaluation**
This involves testing across the entire stack of the agent's workflow: **Node input/output, tool invocation/input/output, state messages/context/actions, memory configurations**.
- What nodes were traversed in the graph?
- Tool invocations (without considering input and output)
- State messages/context/action
    - Are all expected context observations included? (Especially important for write_response)
    - Are correct actions to be taken identified?
    - Is message history correctly stored in memory and retrieved correctly over multi-turn conversations?
- Important test cases with different memory configurations
    - No prior conversation history
    - Conversation history requesting further information
    - Conversation history about unrelated matters or matters that should be in a separate case_id due to customer error

**Consistency and Hallucination evaluation**
This section largely involves ensuring that the response and actions taken are logical and purposeful across the span of the support case.
- Most of this has been tested in above test cases due to the intricate workflows in the graph
- We can test with a human and an LLM-judge that the response generated is appropriate and purposeful for the input given the observations gathered and the response objective in the prompt.
- We can also create examples of inputs and model email response outputs, then measure the semantic similarity of actual email response and the expected email response with Bleu/Rouge/BertScore

# Evaluation metrics
For each of the functions listed above, these are the quantitative metrics that will be calculated and what these metrics mean. The actual evaluations are not complete due to the amounf of time it takes to prepare data, write boilerplate code, and run the tests to calculate various metrics - the purpose of this project is to gain knowledge and experience of agent evaluation, and the theories that the required knowledge is composed of have been explored in my research through my above writings of this evaluation framework. The completed evaluations can be seen under `/agent/evaluation/Evaluations.ipynb`

## classify_email with memory
This is a structured llm invocation.

Classification
- This uses accuracy to determine how many emails were correctly classified

Urgency
- This evaluate the system's ability to classify emails as Urgent using Precision/Recall, as this is the only important category.
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

## write_response
This function input is: **context, email classification, customer email**. Validate that the output is not hallucinating by comparing the context against the final message with llm-judge (Deepeval/RAGAS). 

The email that has been generated will be compared against a model email that takes into context all the bold items above, and can be evaluated against the model email for semantic similarity with ROUGE/METEOR/Bertscore (I prefer BertScore)

## check_inventory_llm_call
This is an llm invocation planner that decides what tools to call and what parameters to call them with.
