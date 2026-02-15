from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.store.postgres import PostgresStore 

"""
script to setup Postgres Langgraph memory
"""

# ===================== Code to load configuration variables =====================
import configparser
from pathlib import Path

config = configparser.ConfigParser()
config_file_path = Path(__file__).resolve().parent / "config.cfg"

files_read = config.read(config_file_path)
if not files_read:
    raise FileNotFoundError(f"Error: {config_file_path} not found or could not be read.")
else:
    # Access values by section and key
    db_host = config['database']['host']
    db_user = config['database']['user']
    db_password = config['database']['password']
    db_database = config['database']['memory_database']

DB_URI = f"postgresql://{db_user}:{db_password}@{db_host}:5432/{db_database}?sslmode=disable"

with (
    PostgresStore.from_conn_string(DB_URI) as store,  
    PostgresSaver.from_conn_string(DB_URI) as checkpointer,
):
    store.setup()
    checkpointer.setup()
    print("Postgres Langgraph memory setup done...")
    print(f"URI: {DB_URI}")