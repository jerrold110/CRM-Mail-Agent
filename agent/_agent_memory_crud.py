from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.store.postgres import PostgresStore
import asyncio

DB_URI = "postgresql://admin:admin@localhost:5432/agent_memory?sslmode=disable"
"""
https://reference.langchain.com/python/langgraph/store/#langgraph.store.postgres.PostgresStore

"""

async def update_customer_support_history(
        customer_id:int, 
        case_id:int, 
        message:str, 
        message_history: dict,
        from_customer:bool=True):
    """
    Namespace and key have to be strings
    Passing the entire history prevents unnecessary reading from the database
    """
    assert message_history is None or isinstance(message_history, dict)
    namespace = ("email_conversation_history", str(customer_id))
    key = str(case_id)
    if from_customer:
        memory_value = f"{message}"
    else:
        memory_value = f"{message}"

    with (
        PostgresStore.from_conn_string(DB_URI) as store,  
        PostgresSaver.from_conn_string(DB_URI) as checkpointer,
    ):
        if not message_history:
            message_history = {'0': memory_value}
            await store.aput(namespace, key, message_history)
        else:
            message_history[str(len(message_history))] = memory_value
            await store.aput(namespace, key, message_history)


async def read_customer_support_history(customer_id: int, case_id:int) -> dict | None:
    """
    Do not block the event loop as this function is executed at scale 
    """
    namespace = ("email_conversation_history", str(customer_id))
    key = str(case_id)

    with (
        PostgresStore.from_conn_string(DB_URI) as store,  
        PostgresSaver.from_conn_string(DB_URI) as checkpointer,
    ):
        
        result = await store.aget(namespace=namespace, key=key)
        if result:
            return result.value # exctract the data as a dictionary
        return None
    
def delete_customer_support_history(
        customer_id:int, 
        case_id:int
    ):
    """
    Used to clear memory after testing
    """
    namespace = ("email_conversation_history", str(customer_id))
    key = str(case_id)

    with (
        PostgresStore.from_conn_string(DB_URI) as store,  
        PostgresSaver.from_conn_string(DB_URI) as checkpointer,
    ):

        store.put(namespace, key, None)

    

if __name__ == "__main__":
    cust = '404'
    case = '404'


    # delete_customer_support_history(cust, case)
    x = asyncio.run(read_customer_support_history(404, 404))
    print(x)
