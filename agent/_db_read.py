import asyncio
import asyncpg # Supposedly better performance than psycopg, does not block the thread 

from pydantic import BaseModel, Field
from typing import Literal

from langchain.tools import tool

async def get_shoe_characteristics():
    conn = await asyncpg.connect(user='admin', password='admin',
                                database='company', host='127.0.0.1')
    values = await conn.fetch(
        'SELECT * FROM shoe_characteristics'
    )

    await conn.close()
    shoe_char_data_str = "product_id,color,material,brand,description\n"
    for row in values:
        row_data = []
        row_data.append(str(row['product_id']))
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
def get_product_availability(productId: int) -> str: # This function is the synchronous wrapper for an asynchronous function
    """
    Get the inventory of a product from the database by id and get: 
    product_name, size, quantity

    If there are no stocks of the product or its quantity is 0, check the incoming deliveries and get:
    product_name, size, quantity, expected_date

    Args:
        productId: Product Id
    """
    #response = asyncio.run(a_get_product_availability(productId=productId))
    #return response
    pass

@tool(args_schema=ProuctIdInput)
async def a_get_product_availability(productId: int) -> str:
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


# test
if __name__ == "__main__":
    productId = 3
    x = get_product_availability(productId=productId) #asyncio.run(get_product_availability(productId=productId))
    print(x)