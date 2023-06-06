import os
import psycopg2

class Connection:
    def __init__(self):
        self.host = os.getenv('DB_HOST')
        self.port = os.getenv('DB_PORT')
        self.dbname = os.getenv('DB_NAME')
        self.user = os.getenv('DB_USER')
        self.password = os.getenv('DB_PASSWORD')

    def connect(self):
        return psycopg2.connect(
            host=self.host,
            port=self.port,
            dbname=self.dbname,
            user=self.user,
            password=self.password
        )
    
connection_params = Connection()

class Color:
    def __init__(self):
        self.GREEN = os.getenv('GREEN')
        self.RED = os.getenv('RED')
        self.RESET = os.getenv('RESET')
        self.YELLOW = os.getenv('YELLOW')

color_params = Color()




