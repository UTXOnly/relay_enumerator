import os
import psycopg2

GREEN = os.getenv('GREEN')
RED = os.getenv('RED')
RESET = os.getenv('RESET')
YELLOW = os.getenv('YELLOW')

conn = psycopg2.connect(
    host=os.getenv('DB_HOST'),
    port=os.getenv('DB_PORT'),
    dbname=os.getenv('DB_NAME'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD')
)