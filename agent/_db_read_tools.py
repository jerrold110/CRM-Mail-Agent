import asyncio
import asyncpg # Supposedly better performance than psycopg, does not block the thread 

from pydantic import BaseModel, Field
from typing import Literal

from langchain.tools import tool
from datetime import datetime, date

async def get_unique_list(f: str):
    conn = await asyncpg.connect(user='admin', password='admin',
                                database='company', host='127.0.0.1')
    
    query = f"""
    SELECT DISTINCT({f}) AS field 
    FROM shoe_characteristics
    """
    values = await conn.fetch(query)

    await conn.close()
    
    fields = []
    for row in values:
        fields.append(str(row['field']))


    return ", ".join(fields)

# These two functions can be optimised further to reduce token usage
async def get_shoe_characteristics():
    conn = await asyncpg.connect(user='admin', password='admin',
                                database='company', host='127.0.0.1')
    values = await conn.fetch(
        'SELECT * FROM shoe_characteristics'
    )

    await conn.close()
    
    shoe_char_data_str = "product_id,size,color,material,brand,description\n"
    for row in values:
        row_data = []
        row_data.append(str(row['product_id']))
        row_data.append(str(row['size']))
        row_data.append(row['color'])
        row_data.append(row['material'])
        row_data.append(row['brand'])
        row_data.append(row['description'])
        row_data_str = ",".join(row_data) + "\n"
        shoe_char_data_str += row_data_str

    return shoe_char_data_str

async def get_query_shoe_characteristics(sql_query: str):
    conn = await asyncpg.connect(user='admin', password='admin',
                                database='company', host='127.0.0.1')
    values = await conn.fetch(
        sql_query
    )

    await conn.close()

    if not values:
        return "No results"
    
    shoe_char_data_str = "product_id,size,color,material,brand,description\n"
    for row in values:
        row_data = []
        row_data.append(str(row['product_id']))
        row_data.append(str(row['size']))
        row_data.append(row['color'])
        row_data.append(row['material'])
        row_data.append(row['brand'])
        row_data.append(row['description'])
        row_data_str = ",".join(row_data) + "\n"
        shoe_char_data_str += row_data_str

    return shoe_char_data_str

class ProuctIdInput(BaseModel):
    productId: int

@tool(args_schema=ProuctIdInput)
async def get_product_availability(productId: int) -> str:
    """
    Get the inventory of a product from the database by id. If there are no stocks of the product or its quantity is 0, check the incoming deliveries

    Args:
        productId: Product Id
    """
    conn = await asyncpg.connect(user='admin', password='admin',
                                database='company', host='127.0.0.1')
    inventory_values = await conn.fetch(
        f"""
        SELECT a.product_id, a.product_name, a.size, b.quantity
        FROM shoe_characteristics a LEFT JOIN inventory b
            ON a.product_id = b.product_id
        WHERE a.product_id = {productId}
        """
    )
    
    if not inventory_values:
        pass
    else:
        row_data = inventory_values[0]
        if row_data['quantity'] > 0:
            await conn.close()
            response = response = f"There are {str(row_data['quantity'])} units of {row_data['product_name']}, size {str(row_data['size'])} in stock"
            return response

    incoming_delivery_values = await conn.fetch(
        f"""
        SELECT a.product_id, a.product_name, a.size, b.quantity, b.expected_date
        FROM shoe_characteristics a LEFT JOIN incoming_deliveries b
            ON a.product_id = b.product_id
        WHERE a.product_id = {productId}
        """
    )

    if not incoming_delivery_values:
        pass
    else: 
        row_data = incoming_delivery_values[0]
        if row_data['quantity'] > 0:
            row_data = incoming_delivery_values[0]
            await conn.close()
            response = f"There no current stocks of {row_data['product_name']}, size {str(row_data['size'])}, but there is a delivery of {str(row_data['quantity'])} units arriving on {str(row_data['expected_date'])}"
            return response
    
    await conn.close()
    return f"There are no stocks or incoming deliveries of product id {str(productId)}"

async def get_current_date():
    """
    The current date for delivery complaint workflows. 20th Jan 2024
    """
    return date(2024,1,20) # should be datetime not date

async def get_customer_open_deliveries(customer_id: int) -> list[tuple]:
    """
    
    """
    assert isinstance(customer_id, int)
    conn = await asyncpg.connect(user='admin', password='admin',
                                database='company', host='127.0.0.1')
    values = await conn.fetch(
        f"""
        SELECT
            status, delivery_id, tracking_number, expected_delivery_end, shipped_date, actual_delivery_date
        FROM item_deliveries 
        WHERE customer_id = {str(customer_id)}
            AND status IN ('processing', 'in_transit', 'out_for_delivery', 'exception')
        """
    )
    await conn.close()
    open_deliveries = []
    for row in values:
        delivery = (
            str(row['status']),
            int(row['delivery_id']),
            str(row['tracking_number']),
            row['expected_delivery_end'],
            row['shipped_date'],
            row['actual_delivery_date']
        )
        open_deliveries.append(delivery)

    return open_deliveries

async def is_coupon_redeemed(customer_id, delivery_id):
    """
    Determine if the coupon has been created for a late delivery,
    if yes it would have been created in the database
    """
    conn = await asyncpg.connect(user='admin', password='admin',
                                database='company', host='127.0.0.1')
    values = await conn.fetch(
        f"""
        SELECT
            coupon_id, customer_id, delivery_id
        FROM coupon_issued
        WHERE customer_id = {str(customer_id)} AND delivery_id = {str(delivery_id)}
        """
    )
    await conn.close()

    if not values:
        return False
    return True

async def late_delivery_last60d(customer_id):
    """
    Current day is 2024-01-20
    """
    conn = await asyncpg.connect(user='admin', password='admin',
                                database='company', host='127.0.0.1')
    values = await conn.fetch(
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
    )
    await conn.close()

    if not values:
        return False
    return True

# test
if __name__ == "__main__":
    param = 3
    #x = asyncio.run(get_customer_open_deliveries(param))
    #print(x)
    #print(asyncio.run(late_delivery_last60d(param)))
    #print(asyncio.run(get_unique_list('material')))
    print(asyncio.run(get_shoe_characteristics()))