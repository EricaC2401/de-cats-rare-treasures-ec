from db.connection import connect_to_db, load_enviroment
from pydantic import BaseModel
from os import getenv
from fastapi import HTTPException


TESTING = getenv('TESTING')

def format_data_list_to_dict(input_list, key, key_list):
    if not input_list:
        raise HTTPException(status_code=404, detail='Page Not Found')
    if len(input_list) > 1:
        output_list = []
        for item in input_list:
            output_list.append(dict(zip(key_list, item)))
        return{key:output_list}
    else:
        return{key:dict(zip(key_list, input_list[0]))}


def connect_to_db_and_get_formatted_result(query_str, key, **value_keys):
    conn = None
    try:
        load_enviroment(TESTING)
        conn = connect_to_db()
        if value_keys:
            result = conn.run(query_str, **value_keys)
        else:
            result = conn.run(query_str)
        key_list = [column['name'] for column in conn.columns]
        formatted_result = format_data_list_to_dict(result, key, key_list)
        return formatted_result
    except HTTPException as http_err:
        print(http_err)
        raise http_err
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            conn.close()

def get_treasures_query():
    # SELECT string_agg(column_name, ', ') AS column_list FROM (SELECT column_name FROM information_schema.columns WHERE table_name = 'treasures' ORDER BY ordinal_position) AS ordered_columns;
    # SELECT string_agg('"'||column_name||'"', ', ') FROM information_schema.columns where table_name = 'treasures';
    # SELECT constraint_name, column_name FROM information_schema.key_column_usage WHERE table_name = 'treasures' AND constraint_name LIKE '%_pkey';
    return '''SELECT treasure_id, treasure_name, colour, age, cost_at_auction, shop_name
            FROM treasures t
            LEFT JOIN shops s
            ON t.shop_id = s.shop_id'''

def get_valid_colours_from_db():
    load_enviroment(TESTING)
    conn = connect_to_db()
    colour_list = conn.run('''SELECT DISTINCT colour from treasures;''')
    conn.close()
    colour_list = [item for sublist in colour_list for item in sublist]
    return colour_list

def get_insert_treasures_query():
    return '''INSERT INTO treasures (treasure_name, colour, age, cost_at_auction, shop_id)
            VALUES
            (:name, :colour, :age, :cost, :shop_id)
            RETURNING *;'''

def get_params_from_new_treasure(new_treasure):
    placeholder = ['name', 'colour', 'age', 'cost', 'shop_id']
    attributes = ["treasure_name", "colour", "age", "cost_at_auction", "shop_id"]
    params = {placeholder[i]:getattr(new_treasure, attributes[i]) for i in range(len(placeholder))}
    return params

def get_update_treasures_query():
    return '''UPDATE treasures SET cost_at_auction = :cost WHERE treasure_id = :id
            RETURNING *;'''

def get_delete_treasures_query():
    return '''DELETE FROM treasures WHERE treasure_id = :id
            RETURNING *;'''

def get_shops_query():
    return '''
            WITH total_cost_per_shop AS 
            (SELECT shop_id, SUM(cost_at_auction) AS stock_value, COUNT(treasure_id) AS count FROM treasures GROUP BY shop_id)
            SELECT s.shop_id, shop_name, slogan ,stock_value, count as treasure_count
            FROM shops s
            LEFT JOIN total_cost_per_shop tc
            ON s.shop_id = tc.shop_id
            ORDER BY s.shop_id ASC;'''

