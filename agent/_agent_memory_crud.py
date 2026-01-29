from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.store.postgres import PostgresStore


# ===================== Code to load configuration variables =====================
import configparser
from pathlib import Path

config = configparser.ConfigParser()
config_file_path = Path(__file__).resolve().parent / "config.cfg"

files_read = config.read(config_file_path)
if not files_read:
    raise FileNotFoundError(f"Error: {config_file_path} not found or could not be read.")
else:
    print(f"Successfully read {config_file_path}")

    # Access values by section and key
    db_host = config['database']['host'] # or localhost
    db_user = config['database']['user']
    db_password = config['database']['password']
    db_memory_database = config['database']['memory_database']
    db_port = config['database']['port']
# ===================== Code to load configuration variables =====================

DB_URI = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_memory_database}?sslmode=disable"

"""
https://reference.langchain.com/python/langgraph/store/#langgraph.store.postgres.PostgresStore

"""

def update_customer_support_history(
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
            store.put(namespace, key, message_history)
        else:
            message_history[str(len(message_history))] = memory_value
            store.put(namespace, key, message_history)


def read_customer_support_history(customer_id: int, case_id:int) -> dict | None:
    """
    Do not block the event loop as this function is executed at scale 
    """
    namespace = ("email_conversation_history", str(customer_id))
    key = str(case_id)

    with (
        PostgresStore.from_conn_string(DB_URI) as store,  
        PostgresSaver.from_conn_string(DB_URI) as checkpointer,
    ):
        
        result = store.get(namespace=namespace, key=key)
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

    delete_customer_support_history(cust, case)
    x = read_customer_support_history(404, 404)
    print(x)
