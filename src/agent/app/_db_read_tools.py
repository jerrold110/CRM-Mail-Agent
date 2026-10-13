"""Database-read tools for the shoe/customer-support agent.

Only connection configuration/pooling has changed. Existing tool names,
parameters, SQL, output formats, and the fixed test date are preserved.

Required environment variables: DB_HOST, DB_PORT, DB_USER,
DB_PASSWORD, DB_DATABASE.

DB_HOST should point at the PgBouncer Compose service ("pgbouncer"), NOT
at the PostgreSQL service, for the read-tool path.
"""

import atexit
import logging
import os
import threading
from datetime import date

from langchain.tools import tool
from pydantic import BaseModel
from psycopg.conninfo import make_conninfo
from psycopg_pool import ConnectionPool


logger = logging.getLogger(__name__)

# Libpq handles quoting special characters in passwords and other values.
DSN = make_conninfo(
    host=os.environ["DB_HOST"],
    port=os.getenv("DB_PORT", "5432"),
    user=os.environ["DB_USER"],
    password=os.environ["DB_PASSWORD"],
    dbname=os.environ["DB_DATABASE"],
    sslmode=os.getenv("DB_SSLMODE", "disable"),
    connect_timeout=10,
)

# Each Celery prefork process gets its own lazily-created, bounded pool.
# PgBouncer then multiplexes those client connections onto PostgreSQL.
_pool: ConnectionPool | None = None
_pool_pid: int | None = None
_pool_lock = threading.Lock()


def get_db_pool() -> ConnectionPool:
    """Return a pool that belongs to the current OS process.

    Never open a Psycopg pool in the Celery parent process before forking.
    A PID check guards against accidentally reusing an inherited pool.
    """
    global _pool, _pool_pid

    pid = os.getpid()
    if _pool is not None and _pool_pid == pid and not _pool.closed:
        return _pool

    with _pool_lock:
        if _pool is None or _pool_pid != pid or _pool.closed:
            min_size = int(os.getenv("DB_POOL_MIN_SIZE", "0"))
            max_size = int(os.getenv("DB_POOL_MAX_SIZE", "2"))
            timeout = float(os.getenv("DB_POOL_TIMEOUT", "10"))

            if not 0 <= min_size <= max_size:
                raise ValueError("DB_POOL_MIN_SIZE must be between 0 and DB_POOL_MAX_SIZE")
            if max_size < 1:
                raise ValueError("DB_POOL_MAX_SIZE must be at least 1")

            _pool = ConnectionPool(
                conninfo=DSN,
                min_size=min_size,
                max_size=max_size,
                timeout=timeout,
                kwargs={"prepare_threshold": None},
                open=False,
                name=f"agent-read-{pid}",
            )
            _pool.open(wait=False)
            _pool_pid = pid
            logger.info(
                "Initialized read DB pool | pid=%s | min_size=%s | max_size=%s",
                pid,
                min_size,
                max_size,
            )

    return _pool


def close_db_pool() -> None:
    """Close only the current process's pool on normal process shutdown."""
    global _pool, _pool_pid
    if _pool is not None and _pool_pid == os.getpid():
        _pool.close()
        _pool = None
        _pool_pid = None


atexit.register(close_db_pool)


# === Existing DB tool function interfaces and query behavior below ===


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


# These two functions can be optimised further to reduce token usage.
def get_shoe_characteristics():
    pool = get_db_pool()
    with pool.connection() as conn:
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
    return date(2024, 1, 20)


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
