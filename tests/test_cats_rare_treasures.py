'''This module contains the test suite for the
`Cat's Rare Treasures` FastAPI app.'''

from main import app
import pytest
from fastapi.testclient import TestClient
from db.seed import seed_db
import json

@pytest.fixture
def test_client():
    return TestClient(app)

@pytest.fixture(autouse=True) # default to be function
def reset_db():
    try:
        seed_db('test')
    except Exception as e:
        print(e)
        raise e


class TestGetTreasures:
    @pytest.mark.it('Test if get_treasures return 200 status code and return correct response structure')
    def test_200_return_by_default_return_correct_structure(self, test_client):
        response = test_client.get('/api/treasures?limit=26')
        assert response.status_code == 200
        response_treasures = response.json()['treasures']
        assert len(response_treasures) == 26
        
        for treasure in response_treasures:
            for col, data_type in zip(["treasure_id", "treasure_name", "colour", "age", "cost_at_auction", "shop_name"],\
                                        [int, str, str,int,float,str]):
                assert isinstance(treasure[col],data_type)

    @pytest.mark.it('Test if get_treasures return 200 status code and a reponse sorted by age and order by asc by default')
    def test_200_return_by_default_return_sorted_by_age_asc(self, test_client):
        response = test_client.get('/api/treasures?limit=26')
        assert response.status_code == 200
        response_treasures = response.json()['treasures']
        assert len(response_treasures) == 26
        assert response_treasures == sorted(response_treasures, key=lambda x: x['age'])

    @pytest.mark.it('\nTest if get_treasures return 404 status code with bad request')
    def test_404_error(self, test_client):
        response = test_client.get('/api/treasurs')
        assert response.status_code == 404
        assert response.json()['detail'] == "Not Found"

    @pytest.mark.separator
    @pytest.mark.it('Test if get_treasures return 200 status code and correct response with query sort by age')
    def test_200_get_treasures_sort_by_age(self, test_client):
        response = test_client.get('/api/treasures?sort_by=age&limit=26')
        assert response.status_code == 200
        response_treasures = response.json()['treasures']
        assert len(response_treasures) == 26
        assert response_treasures == sorted(response_treasures, key=lambda x: x['age'])

    @pytest.mark.it('Test if get_treasures return 200 status code and correct response with query sort by cost_at_auction')
    def test_200_get_treasures_sort_by_cost_at_auction(self, test_client):
        response = test_client.get('/api/treasures?sort_by=cost_at_auction&limit=26')
        assert response.status_code == 200
        response_treasures = response.json()['treasures']
        assert len(response_treasures) == 26
        assert response_treasures == sorted(response_treasures, key=lambda x: x['cost_at_auction'])
    
    @pytest.mark.it('Test if get_treasures return 200 status code and correct response with query sort by treasure_name')
    def test_200_get_treasures_sort_by_treasure_name(self, test_client):
        response = test_client.get('/api/treasures?sort_by=treasure_name&limit=26')
        assert response.status_code == 200
        response_treasures = response.json()['treasures']
        assert len(response_treasures) == 26
        assert response_treasures == sorted(response_treasures, key=lambda x: x['treasure_name'])

    @pytest.mark.it('Test if get_treasures return 422 status code and correct message with bad request for query sortby')
    def test_422_get_treasure_bad_request_sort_by(self, test_client):
        response = test_client.get('/api/treasures?sort_by=trea')
        assert response.status_code == 422
        assert response.json()['detail'][0]['msg'] == "String should match pattern '^(?i)(age|cost_at_auction|treasure_name|treasure_id)$'"
        #assert response.json()['detail'][0]['msg'] == "Input should be 'age', 'cost_at_auction' or 'treasure_name'"
        

    
    @pytest.mark.separator
    @pytest.mark.it('Test if get_treasures return 200 status code and correct response with query order desc')
    def test_200_get_treasures_order_desc(self, test_client):
        response = test_client.get('/api/treasures?order=deSc&limit=26')
        assert response.status_code == 200
        response_treasures = response.json()['treasures']
        assert len(response_treasures) == 26
        assert response_treasures == sorted(response_treasures, key=lambda x: x['age'], reverse=True)

    @pytest.mark.it('Test if get_treasures return 200 status code and correct response with query order asc')
    def test_200_get_treasures_order_asc(self, test_client):
        response = test_client.get('/api/treasures?sort_by=cost_at_auction&order=Asc&limit=26')
        assert response.status_code == 200
        response_treasures = response.json()['treasures']
        assert len(response_treasures) == 26
        assert response_treasures == sorted(response_treasures, key=lambda x: x['cost_at_auction'])

    @pytest.mark.it('Test if get_treasures return 422 status code with bad request for query order')
    def test_422_get_treasures_bad_request_order(self, test_client):
        response = test_client.get('/api/treasures?sort_by=cost_at_auction&order=As')
        assert response.status_code == 422
        assert response.json()['detail'][0]['msg'] == "String should match pattern '^(?i)(ASC|DESC)$'"


    
    @pytest.mark.separator
    @pytest.mark.it('Test if get_treasures return 200 status code and correct response with query colour')
    def test_200_get_treasures_colour(self, test_client):
        response = test_client.get('/api/treasures?colour=golD&limit=26')
        assert response.status_code == 200
        response_treasures = response.json()['treasures']
        assert response_treasures == list(filter(lambda x:x['colour']=='gold', response_treasures))
        #assert response_treasures == [item for item in response_treasures if item['colour']=='gold']

    @pytest.mark.it('Test if get_treasures return 422 status code with bad request for query colour')
    def test_422_get_treasures_bad_request_colour(self, test_client):
        response = test_client.get('/api/treasures?colour=noncolour')
        assert response.status_code == 422
        assert response.json()['detail'] == 'There is no such colour in the database, please try another one'
        #assert response.json()['detail'][0]['msg'] == "String should match pattern '^(?i)(ASC|DESC)$'"



    @pytest.mark.separator
    @pytest.mark.it('Test if get_treasures return 200 status code and correct response with query max_age')
    def test_200_get_treasures_max_age(self, test_client):
        response = test_client.get('/api/treasures?max_age=100&limit=26')
        assert response.status_code == 200
        response_treasures = response.json()['treasures']
        assert response_treasures == list(filter(lambda x:x['age']<=100, response_treasures))
        #assert response_treasures == [item for item in response_treasures if item['colour']=='gold']

    @pytest.mark.it('Test if get_treasures return 422 status code and correct response with query max_age')
    def test_422_get_treasures_max_age_wront_data_type(self, test_client):
        response = test_client.get('/api/treasures?max_age=one')
        assert response.status_code == 422
        assert response.json()['detail'][0] == "query max_age should be a valid integer, unable to parse string as an integer"
        # error_message = response.json()['detail'][0]
        # assert error_message['loc'] == [
		# 		"query",
		# 		"max_age"
		# 	]
        # assert error_message['msg'] == "Input should be a valid integer, unable to parse string as an integer"
    

    @pytest.mark.separator
    @pytest.mark.it('Test if get_treasures return 200 status code and correct response with query min_age')
    def test_200_get_treasures_min_age(self, test_client):
        response = test_client.get('/api/treasures?min_age=1&limit=26')
        assert response.status_code == 200
        response_treasures = response.json()['treasures']
        assert response_treasures == list(filter(lambda x:x['age']>=1, response_treasures))
        #assert response_treasures == [item for item in response_treasures if item['colour']=='gold']

    @pytest.mark.it('Test if get_treasures return 422 status code and correct response with query min_age')
    def test_422_get_treasures_min_age_wront_data_type(self, test_client):
        response = test_client.get('/api/treasures?min_age=one')
        assert response.status_code == 422
        assert response.json()['detail'][0] == "query min_age should be a valid integer, unable to parse string as an integer"
        # error_message = response.json()['detail'][0]
        # assert error_message['loc'] == [
		# 		"query",
		# 		"min_age"
		# 	]
        # assert error_message['msg'] == "Input should be a valid integer, unable to parse string as an integer"


    @pytest.mark.separator
    @pytest.mark.it('Test if get_treasures return 200 status code and correct response with query limit')
    def test_200_get_treasures_limit(self, test_client):
        all_reaponse = test_client.get('/api/treasures?sort_by=treasure_name&limit=26')
        response = test_client.get('/api/treasures?sort_by=treasure_name&limit=10')
        assert response.status_code == 200
        all_reaponse_treasures = response.json()['treasures']
        response_treasures = response.json()['treasures']
        assert len(response_treasures) == 10
        assert response_treasures == all_reaponse_treasures[:10]

    @pytest.mark.it('Test if get_treasures return 422 status code and correct response with query limit')
    def test_422_get_treasures_limit_wront_data_type(self, test_client):
        response = test_client.get('/api/treasures?limit=one')
        assert response.status_code == 422
        assert response.json()['detail'][0] == "query limit should be a valid integer, unable to parse string as an integer"
        # error_message = response.json()['detail'][0]
        # assert error_message['loc'] == [
		# 		"query",
		# 		"limit"
		# 	]
        # assert error_message['msg'] == "Input should be a valid integer, unable to parse string as an integer"

    
    @pytest.mark.separator
    @pytest.mark.it('Test if get_treasures return 200 status code and correct response with query page')
    def test_200_get_treasures_page(self, test_client):
        all_response = test_client.get('/api/treasures?sort_by=treasure_name&limit=26')
        response = test_client.get('/api/treasures?sort_by=treasure_name&page=3')
        assert response.status_code == 200
        all_reaponse_treasures = all_response.json()['treasures']
        response_treasures = response.json()['treasures']
        assert len(response_treasures) == 5
        assert response_treasures == all_reaponse_treasures[10:15]

    @pytest.mark.it('Test if get_treasures return 404 status code and page is too large')
    def test_404_get_treasures_page_page_too_large(self, test_client):
        response = test_client.get('/api/treasures?page=100')
        assert response.status_code == 404
        assert response.json()['detail'] == 'Page Not Found'

    @pytest.mark.it('Test if get_treasures return 422 status code and correct response with query page')
    def test_422_get_treasures_page_wrong_data_type(self, test_client):
        response = test_client.get('/api/treasures?page=one')
        assert response.status_code == 422
        assert response.json()['detail'][0] == "query page should be a valid integer, unable to parse string as an integer"
        # error_message = response.json()['detail'][0]
        # assert error_message['loc'] == [
		# 		"query",
		# 		"page"
		# 	]
        # assert error_message['msg'] == "Input should be a valid integer, unable to parse string as an integer"





class TestPostTreasures:
    @pytest.mark.it('Test if post on treasures return 201 status code and correct response')
    def test_201_post_treasures(self, test_client):
        input_data = {
            "treasure_name": "Golden Chalice",
            "colour": "gold",
            "age": 500,
            "cost_at_auction": 100000.0,
            "shop_id": 2
        }
        response = test_client.post('/api/treasures', json=input_data)
        assert response.status_code == 201
        response_treasure = response.json()['treasure']
        assert response_treasure['treasure_id'] == 27
        for key, value in input_data.items():
            assert response_treasure[key] == value

    @pytest.mark.it('Test if post on treasures return 500 status code when missing required field')
    def test_500_post_treasures_missing_required_field(self, test_client):
        input_data = {
            "colour": "gold",
            "age": 500,
            "cost_at_auction": 100000.0,
            "shop_id": 2
        }
        response = test_client.post('/api/treasures', json=input_data)
        assert response.status_code == 500

        error_response = response.json()
        assert "detail" in error_response
        assert 'null value in column \"treasure_name\" of relation \"treasures\" violates not-null constraint' in error_response['detail']
    

    @pytest.mark.it('Test if post on treasures return 500 status code when foreign key field outside the bound')
    def test_500_post_treasures_foreign_key_outside_bound(self, test_client):
        input_data = {
            "treasure_name": "Golden Chalice",
            "colour": "gold",
            "age": 500,
            "cost_at_auction": 100000.0,
            "shop_id": 123
        }
        response = test_client.post('/api/treasures', json=input_data)
        assert response.status_code == 500

        error_response = response.json()
        assert "detail" in error_response
        assert 'insert or update on table \"treasures\" violates foreign key constraint \"treasures_shop_id_fkey\"'

    @pytest.mark.it('Test if post on treasures return 422 status code when incorrect data type')
    def test_422_post_treasures_incorrect_data_type(self, test_client):
        input_data = {
            "treasure_name": 123,
            "colour": "gold",
            "age": "five",
            "cost_at_auction": 2,
            "shop_id": "7"
        }
        response = test_client.post('/api/treasures', json=input_data)
        assert response.status_code == 422

        error_msgs = [('treasure_name', 'string'), ('age', 'integer')]
        for item in error_msgs:
            expected_error = f"query {item[0]} should be a valid {item[1]}" 
            assert any(expected_error in msg for msg in response.json()['detail'])
            #assert any(msg == f"query {item[0]} should be a valid {item[1]}" for msg in response.json()['detail'])


        # expected_errors = [
        #         {'field': 'treasure_name', 'msg': 'Input should be a valid string'},
        #         {'field': 'age', 'msg': 'Input should be a valid integer, unable to parse string as an integer'}
        #     ]
        # assert "detail" in response.json()
        # assert 'msg' in response.json()['detail'][0]
        # for expected_error in expected_errors:
        #     assert any(error['loc'] == ['body', expected_error['field']] and \
        #                 error['msg'] == expected_error['msg']\
        #                     for error in response.json()['detail'])
    
        # assert 'Input should be a valid' in response.json()['detail'][0]['msg']
        # error_response = response.json()
        # assert "detail" in error_response
        # assert 'insert or update on table \"treasures\" violates foreign key constraint \"treasures_shop_id_fkey\"'


class TestPatchTreasures:
    @pytest.mark.it('Test if patch_treasures return 200 status code and correct response')
    def test_200_patch_treasures(self, test_client):
        input_data = {
            "cost_at_auction": 7000,
        }
        response = test_client.patch('/api/treasures/1', json=input_data)
        assert response.status_code == 200
        response_treasure = response.json()['treasure']
        for key, value in input_data.items():
            assert response_treasure[key] == value

    @pytest.mark.it('Test if patch_treasures return 404 status code with unavailable id')
    def test_404_patch_treasures_unavailable_id(self, test_client):
        input_data = {
            "cost_at_auction": 7000,
        }
        response = test_client.patch('/api/treasures/123', json=input_data)
        assert response.status_code == 404
        error_response = response.json()['detail']
        assert error_response == 'There is no data given the request'

    @pytest.mark.it('Test if patch_treasures return 422 status code with incorrect data type')
    def test_422_patch_treasures_incorrect_data_type(self, test_client):
        input_data = {
            "cost_at_auction": 'seven',
        }
        response = test_client.patch('/api/treasures/1', json=input_data)
        assert response.status_code == 422
        assert 'detail' in response.json()
        assert response.json()['detail'][0] == "query cost_at_auction should be a valid integer, unable to parse string as an integer"
        # error_response = response.json()['detail'][0]
        # assert error_response['loc'] == ['body', 'cost_at_auction']
        # assert error_response['msg'] == "Input should be a valid integer, unable to parse string as an integer"


class TestDeleteTreasures:
    @pytest.mark.it('Test if delete_treasures return 204 status code')
    def test_204_delete_treausre(self, test_client):
        response_treasures_before = test_client.get('/api/treasures?limit=26').json()['treasures']
        response = test_client.delete('/api/treasures/1')
        assert response.status_code == 204
        response_treasures_after = test_client.get('/api/treasures?limit=26').json()['treasures']
        assert len(response_treasures_before) - len(response_treasures_after) == 1
        assert 1 in [item['treasure_id'] for item in response_treasures_before]
        assert 1 not in [item['treasure_id'] for item in response_treasures_after]

    @pytest.mark.it('Test if delete_treasures return 404 status code')
    def test_404_delete_treausre_unavailable_id(self, test_client):
        response = test_client.delete('/api/treasures/123')
        assert response.status_code == 404


class TestGetShops:
    @pytest.mark.it('Test of get_shops returns 200 status code and correct structure')
    def test_200_get_shops(self, test_client):
        response = test_client.get('/api/shops')
        assert response.status_code == 200
        response_shop = response.json()['shops']
        for shop in response_shop:
            for col, data_type in zip(["shop_id", "shop_name", "slogan", "stock_value", "treasure_count"], [int, str, str, float, int]):
                assert isinstance(shop[col], data_type)

    @pytest.mark.it('Test of get_shops returns 200 status code and return correct resposne sorted by shop_id ASC by default')
    def test_200_get_shop_return_sortby_shop_id_asc_by_default(self, test_client):
        response = test_client.get('/api/shops')
        assert response.status_code == 200
        response_shops = response.json()['shops']
        assert response_shops == sorted(response_shops, key=lambda x: x['shop_id'])

    @pytest.mark.it('Test of get_shops returns 404 status code with bad request')
    def test_200_get_shops_bad_request(self, test_client):
        response = test_client.get('/api/shop')
        assert response.status_code == 404
        assert response.json()['detail'] == 'Not Found'

        
    


