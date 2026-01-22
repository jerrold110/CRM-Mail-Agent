from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.store.postgres import PostgresStore
import asyncio

DB_URI = "postgresql://admin:admin@localhost:5432/agent_memory?sslmode=disable"

async def update_customer_support_history(
        customer_id:int, 
        case_id:int, 
        message:str, 
        message_history: dict,
        from_customer:bool=True):
    """
    Namespace and key have to be strings
    """
    assert message_history is None or isinstance(message_history, dict)
    namespace = ("email_conversation_history", str(customer_id))
    key = str(case_id)
    if from_customer:
        memory_value = f"Customer: {message}"
    else:
        memory_value = f"Customer Service: {message}"

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
    """
    namespace = ("email_conversation_history", str(customer_id))
    key = str(case_id)

    with (
        PostgresStore.from_conn_string(DB_URI) as store,  
        PostgresSaver.from_conn_string(DB_URI) as checkpointer,
    ):

        store.put(namespace, key, None)

    

if __name__ == "__main__":
    cust = '001'
    case = '001'

    asyncio.run(update_customer_support_history(cust , case, 'Some message 1', None, False))
    convo_data = asyncio.run(read_customer_support_history(cust, case))
    asyncio.run(update_customer_support_history(cust , case, 'Some message 2', convo_data, True))
    convo_data = asyncio.run(read_customer_support_history(cust, case))

    # delete_customer_support_history(cust, case)
    # asyncio.run(read_customer_support_history(cust, case))
