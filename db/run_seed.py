'''This module contains the logic to seed the development databases
for the `Cat's Rare Treasures` FastAPI app.'''
from seed import seed_db
import os

TESTING = os.getenv('TESTING')

try:
    if TESTING:
        seed_db(TESTING.lower())
    else:
        seed_db('dev')
except Exception as e:
    print(e)
    raise e
