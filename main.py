'''This module is the entrypoint for the `Cat's Rare Treasures` FastAPI app.'''

from fastapi import FastAPI, Query, HTTPException, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.exceptions import RequestValidationError
from db.utils import connect_to_db_and_get_formatted_result, get_treasures_query, get_valid_colours_from_db, get_insert_treasures_query,\
                    get_params_from_new_treasure, get_update_treasures_query, get_delete_treasures_query, get_shops_query
from typing import Optional, Annotated, Literal
from enum import Enum
from pydantic import BaseModel
from pg8000 import DatabaseError
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

app = FastAPI()

#app.mount('/static', StaticFiles(directory='static'), name='static')

#templates = Jinja2Templates(directory="templates")


# class SortBy(str, Enum):
#     age = 'age'
#     cost_at_auction = 'cost_at_auction'
#     treasure_name = 'treasure_name'

# class Order(str, Enum):
#     ASC = 'ASC'
#     DESC = 'DESC'

# order of defining handlers matters
@app.exception_handler(DatabaseError)
def handle_db_error(request, exc):
    print(exc)
    err_code = exc.args[0]['C']
    err_message = exc.args[0]['M']
    if err_code:
        raise HTTPException(status_code=500, detail=err_message)
    raise HTTPException(status_code=500, detail='Sorry! Server-side error has occured,\
                        admins have been notified.')

#When you want to raise more than 1 HTTPException in a function
@app.exception_handler(HTTPException)
def handle_httpexception(request, exc):
    return JSONResponse(
        status_code = exc.status_code,
        content={'detail': exc.detail},
    )

@app.exception_handler(RequestValidationError)
def handle_request_validation(request, exc):
    output = []
    for err in exc.errors():
        if 'Input should be a valid' in err['msg']:
            output.append(f"query {err['loc'][1]} {err['msg'][6:]}")
    if output:
        return JSONResponse(status_code=422, content={'detail':output})
    else:
        return JSONResponse(status_code=422, content={'detail':exc.errors()})
    # if request.url.path == '/api/treasures':
    #     return JSONResponse(status_code=422, content={'detail':exc.errors()})
    # else:
    #     return JSONResponse(status_code=422, content={'detail':'Validation Error'})

@app.exception_handler(Exception)
def handle_general_exception(request, exc):
    return JSONResponse(status_code=500, content={'detail':'Interal Server Error'})

@app.get('/api/treasures') # , response_class=HTMLResponse
def get_treasures(#request:Request,
                sort_by: 
                Optional[str] = 
                Query(default='age', description='Field to sort by', examples='age', pattern='^(?i)(age|cost_at_auction|treasure_name|treasure_id)$'), 
                order:
                Optional[str] =
                Query(default='ASC', description='Sort order (case insensitive, must be "ASC" or "DESC")', examples='ASC', pattern='^(?i)(ASC|DESC)$'),
                colour:
                Optional[str] = 
                Query(default=None, description='Filter by colour (case insensitive)', examples='gold', pattern='^(?i)[a-z]+$'),
                max_age:
                Optional[int] = 
                Query(default=None, description='Filter by max_age', examples=100), # pattern='^[0-9]{1,3}$' would
                min_age:
                Optional[int] =
                Query(default=None, description='Filter by min_age', examples=1),
                limit:
                Optional[int] = 
                Query(default=5, description='Limit the number of results', examples=5),
                page:
                Optional[int] = 
                Query(default=1, description='Respond with the select page', examples=1)
                ):


    query_str = get_treasures_query()
    params = {}
    if colour:
        colour_list = get_valid_colours_from_db()
        if colour.lower() not in colour_list:
            raise HTTPException(status_code=422, detail="There is no such colour in the database, please try another one")
        query_str += ' WHERE colour = :colour'
        params['colour'] = colour.lower()
    if max_age:
        params['max_age'] = max_age
        if colour:
            query_str += ' AND '
        else:
            query_str += ' WHERE '
        query_str += 'age <= :max_age'
    if min_age:
        params['min_age'] = min_age
        if colour or max_age:
            query_str += ' AND '
        else:
            query_str += ' WHERE '
        query_str += 'age >= :min_age'
    if sort_by:
        query_str += f' ORDER BY {sort_by} {order}'
    if limit:
        query_str += f' LIMIT {limit}'
    if page:
        query_str += f' OFFSET {(page-1) *limit}'
    query_str += ';'
    #if params:
    response = connect_to_db_and_get_formatted_result(query_str, 'treasures', **params)
    #else:
    #    response = connect_to_db_and_get_formatted_result(query_str, 'treasures')
    if not response and page > 1:
        raise HTTPException(status_code=404, detail='Page not found')
    return response
    #return templates.TemplateResponse(request, name='treasures.html', context=response)

    # except HTTPException as http_err:
    #     print(http_err)
    #     raise http_err

    # except Exception as e:
    #     print(e)
    #     return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})



class NewTreasure(BaseModel):
    treasure_name : str | None = None
    colour : str | None = None
    age : int | None = None
    cost_at_auction : float | None = None
    shop_id : int | None = None


@app.post('/api/treasures', status_code=201)
def post_treasures(new_treasure:NewTreasure):
    # try:
    query_str = get_insert_treasures_query()
    params = get_params_from_new_treasure(new_treasure)
    response = connect_to_db_and_get_formatted_result(query_str, 'treasure', **params)
    return response
    # except Exception as e:
    #     print(f"An error occurred: {e}")
    #     raise HTTPException(status_code=500, detail=str(e))



class UpdateTreasures(BaseModel):
    cost_at_auction: int | None = None

@app.patch('/api/treasures/{treasure_id}')
def patch_treasures(treasure_id:int, update_treasure:UpdateTreasures):
    try:
        params = {'id':treasure_id}
        params['cost'] = getattr(update_treasure, 'cost_at_auction')
        query_str = get_update_treasures_query()
        response = connect_to_db_and_get_formatted_result(query_str, 'treasure', **params)
        return response
    except HTTPException as http_err:
        raise HTTPException(status_code=404, detail='There is no data given the request')
    # except Exception as e:
    #     print(f"An error occurred: {e}")
    #     raise HTTPException(status_code=500, detail=str(e))

@app.delete('/api/treasures/{treasure_id}', status_code=204)
def delete_treasures(treasure_id:int):
    # try:
    query_str = get_delete_treasures_query()
    response = connect_to_db_and_get_formatted_result(query_str, 'treasure', id=treasure_id)
    # except HTTPException as http_err:
    #     raise HTTPException(status_code=404, detail='There is no such treasure_id in the database')
    # except Exception as e:
    #     print(f"An error occurred: {e}")
    #     raise HTTPException(status_code=500, detail=str(e))

        
@app.get('/api/shops')
def get_shops():
    query_str = get_shops_query()
    response = connect_to_db_and_get_formatted_result(query_str, 'shops')
    return response








# @app.get('/api/treasures')
# def get_treasures(sort_by: 
#                 Annotated[Optional[Literal['age', 'cost_at_auction', 'treasure_name']], 
#                 Query(description='Field to sort by', examples='age')] = 'age', 
#                 order:
#                 Annotated[Optional[str],
#                 Query(description='Sort order (case insensitive, must be "ASC" or "DESC")', examples='ASC')]='ASC'):

#     if order.upper() not in ['ASC', 'DESC']:
#         raise HTTPException(status_code=422, detail="Invalid order parameter. Must be 'ASC' or 'DESC'")

#     query_str = get_treasures_query()
#     if sort_by:
#         query_str += f' ORDER BY {sort_by} {order};'
#     response = connect_to_db_and_get_formatted_result(query_str, 'treasures')
#     return response


# @app.get('/api/treasures')
# def get_treasures(sort_by: 
#                 Annotated[Optional[Literal['age', 'cost_at_auction', 'treasure_name']], 
#                 Query(description='Field to sort by')] = 'age', 
#                 order='ASC'):

#     query_str = get_treasures_query()
#     if sort_by:
#         query_str += f' ORDER BY {sort_by} {order};'
#     response = connect_to_db_and_get_formatted_result(query_str, 'treasures')
#     return response

    
# def get_treasures(sort_by:Optional[SortBy]=SortBy.age, order='ASC'):
#     query_str = get_treasures_query()
#     # if sort_by in ['age', 'cost_at_auction', 'treasure_name']:
#     if sort_by:
#         query_str += f' ORDER BY {sort_by.value} {order};'
#     response = connect_to_db_and_get_formatted_result(query_str, 'treasures')
#     return response

    