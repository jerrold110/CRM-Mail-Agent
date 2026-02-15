from psycopg_pool import ConnectionPool

from pydantic import BaseModel, Field

from langchain.tools import tool
from datetime import datetime, date


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
    db_database = config['database']['database']

# ===================== Code to load configuration variables =====================

# --- The Connection String ---
DSN = f"postgresql://{db_user}:{db_password}@{db_host}/{db_database}"

# --- GLOBAL STATE ---
# We set this to None initially. It is a placeholder.
# This executes once when the worker process starts (imports this file).
_pool = None


def get_db_pool():
    """
    This function ensures we get the correct pool for the CURRENT process. 
    
    This is a per-celery-worker pool, not a global pool across all workers. Celery can have multiple worker processes, and each process will have its own instance of this module and thus its own _pool variable. This design ensures that each worker process maintains its own connection pool, which is important for avoiding issues with shared state across processes.
    """
    global _pool
    
    if _pool is None:
        print("Initializing new DB Pool for this worker process...")
        # min_size=1: Keeps 1 connection open per worker always.
        # max_size=5: Allows up to 5 concurrent queries per worker (if using threads).
        _pool = ConnectionPool(DSN, min_size=1, max_size=5, open=True)
    
    return _pool

def get_unique_list(f: str):

    pool = get_db_pool()
    with pool.connection() as conn:
    
        query = f"""
        SELECT DISTINCT({f}) AS field 
        FROM shoe_characteristics
        """
        
        values = conn.execute(query).fetchall()
    
    fields = []
    for row in values:
        fields.append(str(row[0]))

    return ", ".join(fields)

# These two functions can be optimised further to reduce token usage
def get_shoe_characteristics():

    pool = get_db_pool()
    with pool.connection() as conn:
        # Limit the rows by 500
        values = conn.execute('SELECT * FROM shoe_characteristics LIMIT 500').fetchall()
    
    shoe_char_data_str = "product_id,size,color,material,brand,description\n"
    for row in values:
        row_data = []
        row_data.append(str(row[0]))
        row_data.append(str(row[2]))
        row_data.append(row[3])
        row_data.append(row[4])
        row_data.append(row[6])
        row_data.append(row[8])
        row_data_str = ",".join(row_data) + "\n"
        shoe_char_data_str += row_data_str

    return shoe_char_data_str

def get_query_shoe_characteristics(sql_query: str):

    pool = get_db_pool()
    with pool.connection() as conn:
        values = conn.execute(sql_query).fetchall()

    if not values:
        return "No results"
    
    shoe_char_data_str = "product_id,size,color,material,brand,description\n"
    for row in values:
        row_data = []
        row_data.append(str(row[0]))
        row_data.append(str(row[2]))
        row_data.append(row[3])
        row_data.append(row[4])
        row_data.append(row[6])
        row_data.append(row[8])
        row_data_str = ",".join(row_data) + "\n"
        shoe_char_data_str += row_data_str

    return shoe_char_data_str

class ProuctIdInput(BaseModel):
    productId: int

@tool(args_schema=ProuctIdInput)
def get_product_availability(productId: int) -> str:
    """
    Get the inventory of a product from the database by id. If there are no stocks of the product or its quantity is 0, check the incoming deliveries

    Args:
        productId: Product Id
    """

    pool = get_db_pool()
    with pool.connection() as conn:
        inventory_values = conn.execute(
            f"""
            SELECT a.product_id, a.product_name, a.size, b.quantity
            FROM shoe_characteristics a LEFT JOIN inventory b
                ON a.product_id = b.product_id
            WHERE a.product_id = {productId}
            """
        ).fetchall()
    
        if not inventory_values:
            pass
        else:
            row_data = inventory_values[0]
            if row_data[3] > 0:
                response = f"There are {str(row_data[3])} units of {row_data[1]}, size {str(row_data[2])} in stock"
                return response

        incoming_delivery_values = conn.execute(
            f"""
            SELECT a.product_id, a.product_name, a.size, b.quantity, b.expected_date
            FROM shoe_characteristics a LEFT JOIN incoming_deliveries b
                ON a.product_id = b.product_id
            WHERE a.product_id = {productId}
            """
        ).fetchall()

        if not incoming_delivery_values:
            pass
        else: 
            row_data = incoming_delivery_values[0]
            if row_data[3] > 0:
                row_data = incoming_delivery_values[0]
                response = f"There no current stocks of {row_data[1]}, size {str(row_data[2])}, but there is a delivery of {str(row_data[3])} units arriving on {str(row_data[4])}"
                return response
    
    return f"There are no stocks or incoming deliveries of product id {str(productId)}"

def get_current_date():
    """
    The current date for delivery complaint workflows. 20th Jan 2024
    """
    return date(2024,1,20) # should be datetime not date

def get_customer_open_deliveries(customer_id: int) -> list[tuple]:
    """
    Get the open deliveries of a customer for a given customer id
    """
    assert isinstance(customer_id, int)

    pool = get_db_pool()
    with pool.connection() as conn:
        values = conn.execute(
            f"""
            SELECT
                status, delivery_id, tracking_number, expected_delivery_end, shipped_date, actual_delivery_date
            FROM item_deliveries 
            WHERE customer_id = {str(customer_id)}
                AND status IN ('processing', 'in_transit', 'out_for_delivery', 'exception')
            """
        ).fetchall()
    
    open_deliveries = []
    for row in values:
        delivery = (
            str(row[0]),
            int(row[1]),
            str(row[2]),
            row[3],
            row[4],
            row[5]
        )
        open_deliveries.append(delivery)

    return open_deliveries

def is_coupon_redeemed(customer_id, delivery_id):
    """
    Determine if the coupon has been created for a late delivery,
    if yes it would have been created in the database
    """

    pool = get_db_pool()
    with pool.connection() as conn:
        values = conn.execute(
            f"""
            SELECT
                coupon_id, customer_id, delivery_id
            FROM coupon_issued
            WHERE customer_id = {str(customer_id)} AND delivery_id = {str(delivery_id)}
            """
        ).fetchall()

    if not values:
        return False
    return True

def late_delivery_last60d(customer_id):
    """
    Current day is 2024-01-20
    """

    pool = get_db_pool()
    with pool.connection() as conn:
        values = conn.execute(
            f"""
            SELECT
                *
            FROM item_deliveries 
            -- late deliveries in last 60 days
            WHERE actual_delivery_date > expected_delivery_end 
                AND (actual_delivery_date + INTERVAL '60 days') > '2024-01-20'
                AND actual_delivery_date IS NOT NULL
                AND customer_id = {str(customer_id)}
            """
        ).fetchall()

    if not values:
        return False
    return True

# test
if __name__ == "__main__":
    param = 3
    #x = get_customer_open_deliveries(param)
    #print(x)
    #print(late_delivery_last60d(param))
    #print(get_shoe_characteristics())

    #q = "SELECT * FROM shoe_characteristics\nLIMIT 500;"
    #print(get_query_shoe_characteristics(q))
    #print(get_product_availability(1))
    #print(get_customer_open_deliveries(3))