from db.utils import format_data_list_to_dict, get_params_from_new_treasure
from pydantic import BaseModel
from main import NewTreasure

def test_format_data_list_to_dict():
    input_list = [[1, 'Luck Lust Liquor & Burn', 1, 'Mexican', 'http://lucklustliquorburn.com/']]
    expected = {
	"restaurant":
		{
			"restaurant_id": 1,
			"restaurant_name": "Luck Lust Liquor & Burn",
			"area_id": 1,
			"cuisine": "Mexican",
			"website": "http://lucklustliquorburn.com/"
		}
    }
    assert format_data_list_to_dict(input_list, "restaurant", ["restaurant_id","restaurant_name","area_id","cuisine","website"]) == expected


def test_get_params_from_new_treasure():

	new_treasure = NewTreasure(
			treasure_name="Golden Chalice",
			colour="gold",
			age=500,
			cost_at_auction=100000.0,
			shop_id=123
		)

	excepted = {
			'name': 'Golden Chalice',
			'colour': 'gold',
			'age': 500,
			'cost': 100000.0,
			'shop_id': 123
		}
	
	assert get_params_from_new_treasure(new_treasure) == excepted


