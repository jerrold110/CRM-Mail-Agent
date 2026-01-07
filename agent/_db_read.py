import asyncio
import asyncpg

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