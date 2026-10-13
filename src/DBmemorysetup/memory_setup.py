import os
import logging

from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.store.postgres import PostgresStore

logger = logging.getLogger(__name__)

db_host = os.getenv("DB_HOST")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_database = os.getenv("DB_MEMORY_DATABASE")
db_port = os.getenv("DB_PORT")

if not all([db_host, db_user, db_password, db_database]):
    raise ValueError(
        "Missing required environment variables. "
        "Please ensure DB_HOST, DB_USER, DB_PASSWORD, "
        "and DB_MEMORY_DATABASE are set."
    )

DB_URI = (
    f"postgresql://{db_user}:{db_password}"
    f"@{db_host}:{db_port}/{db_database}"
    "?sslmode=disable"
)

print(f"Connecting to PostgreSQL at {db_host}:{db_port}/{db_database}")

with (
    PostgresStore.from_conn_string(DB_URI) as store,
    PostgresSaver.from_conn_string(DB_URI) as checkpointer,
):
    store.setup()
    checkpointer.setup()

print("Postgres LangGraph memory setup done.")
logger.info(
        "Postgres LangGraph memory setup done."
    )

