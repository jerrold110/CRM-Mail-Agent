from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.store.postgres import PostgresStore  

DB_URI = "postgresql://admin:admin@localhost:5432/agent_memory?sslmode=disable"

with (
    PostgresStore.from_conn_string(DB_URI) as store,  
    PostgresSaver.from_conn_string(DB_URI) as checkpointer,
):
    store.setup()
    checkpointer.setup()
    print("Postgres Langgraph memory setup done...")
    print(f"URI: {DB_URI}")