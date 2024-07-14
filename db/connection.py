from pg8000.native import Connection
from dotenv import load_dotenv
import os

#TESTING = os.getenv('TESTING')

def load_enviroment(env):
    if env == 'test':
        load_dotenv('.env.test')
    else:
        load_dotenv('.env.dev')


def connect_to_db():
    print(os.getenv("PG_DATABASE"))
    return Connection(
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        database=os.getenv("PG_DATABASE"),
        host=os.getenv("PG_HOST"),
        port=int(os.getenv("PG_PORT"))
    )
