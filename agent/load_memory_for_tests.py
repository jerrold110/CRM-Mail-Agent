from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.store.postgres import PostgresStore

DB_URI = "postgresql://admin:admin@localhost:5432/agent_memory?sslmode=disable"

def add_customer_support_history(
        customer_id:int, 
        case_id:int, 
        value: dict
):
    """
    Entries follow the format:
    {
        '0': 'this is a message',
        '1': 'this is a response to the first message'
        '2': 'this is a response to the second message'
    }
    """

    namespace = ("email_conversation_history", str(customer_id))
    key = str(case_id)

    with (
        PostgresStore.from_conn_string(DB_URI) as store,  
        PostgresSaver.from_conn_string(DB_URI) as checkpointer,
    ):
        store.put(namespace, key, value)
        print(f'Put value: {value}')



history = {
    '0': "Customer inquires about the availability of red leather shoes designed to help with running fast.",
    '1': "The customer service team responded to Michael's inquiry, confirming that they have 100 pairs of red leather Nike Air Max shoes in size 10.0 and 100 in size 9.5 in stock. They offered assistance with ordering or providing additional information.",
}

add_customer_support_history(
    404,
    404,
    history
)


history = {
    '0': "Customer inquires about the availability of red leather shoes designed to help with running fast.",
    '1': "The customer service team responded to Michael's inquiry, confirming that they have 100 pairs of red leather Nike Air Max shoes in size 10.0 and 100 in size 9.5 in stock. They offered assistance with ordering or providing additional information.",
    '2': "The client, Michael, is looking for red leather shoes that will help him run fast.",
    '3': "The email confirms the availability of red leather Nike Air Max shoes in sizes 9.5 and 10.0, with 100 units of each size in stock. It highlights the shoes' comfort and support and offers further assistance or to place an order."
}

add_customer_support_history(
    405,
    405,
    history
)

history = {
    '0': "Customer inquires about the availability of red leather shoes designed to help with running fast.",
    '1': "The customer service team responded to Michael's inquiry, confirming that they have 100 pairs of red leather Nike Air Max shoes in size 10.0 and 100 in size 9.5 in stock. They offered assistance with ordering or providing additional information.",
    '2': "The client, Michael, is looking for red leather shoes that will help him run fast.",
    '3': "The email confirms the availability of red leather Nike Air Max shoes in sizes 9.5 and 10.0, with 100 units of each size in stock. It highlights the shoes' comfort and support and offers further assistance or to place an order.",
    '4': "The client, Michael, is looking for red leather shoes that will help him run fast.",
    '5': "The Customer Service Team responded to Michael's inquiry by confirming the availability of red leather Nike Air Max running shoes. They have 100 units in size 10.0 and 100 units in size 9.5 in stock and offered to provide additional assistance if needed."
}

add_customer_support_history(
    406,
    406,
    history
)


history = {
    '0': "Customer is inquiring about a delayed delivery.",
    '1': "The Customer Service Team requests Michael to provide his valid tracking number so they can locate his delayed delivery and assist him more effectively."
}
# Customer has provided the tracking number UPS321654987 in response to a request from Customer Service to assist with locating the delayed delivery.
# The customer service team acknowledges receipt of the tracking number UPS321654987 but cannot find a matching open delivery. They request verification or additional details to assist with the delivery issue.

add_customer_support_history(
    407,
    407,
    history
)