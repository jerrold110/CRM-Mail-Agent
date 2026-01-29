from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.store.postgres import PostgresStore

import asyncio
import asyncpg

# ===================== Code to load configuration variables =====================
import configparser
from pathlib import Path

config = configparser.ConfigParser()
config_file_path = Path(__file__).resolve().parent.parent / "config.cfg"

files_read = config.read(config_file_path)
if not files_read:
    raise FileNotFoundError(f"Error: {config_file_path} not found or could not be read.")
else:
    print(f"Successfully read {config_file_path}")

    # Access values by section and key
    db_host = config['database']['host'] # or localhost
    db_user = config['database']['user']
    db_password = config['database']['password']
    db_database = config['database']['database']
    db_memory_database = config['database']['memory_database']
    db_port = config['database']['port']
# ===================== Code to load configuration variables =====================

DB_URI = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_memory_database}?sslmode=disable"
# conn = await asyncpg.connect(user=db_user, password=db_password, database=db_database, host=db_host)

sql_file_path = Path(__file__).resolve().parent / "load_eval.sql"

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

async def add_sql_database_query(sql_file_path):
    conn = await asyncpg.connect(user=db_user, password=db_password,
                                database=db_database, host=db_host)
    
    sql = Path(sql_file_path).read_text(encoding="utf-8")
    
    async with conn.transaction():
        await conn.execute(sql)

    await conn.close()
    print("Asyncpg Connection closed")

if __name__ == "__main__":
    
    asyncio.run(add_sql_database_query(sql_file_path))

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