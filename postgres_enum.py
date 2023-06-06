import psycopg2
from connection_param import Color

colors = Color()

def connect_to_postgres(hosts, credentials):
    for host in hosts:
        for username, password in credentials.items():
            try:
                conn = psycopg2.connect(
                    host=host,
                    user=username,
                    password=password
                )
                print(f"{colors.GREEN}Successfully connected to PostgreSQL on {colors.RESET}{host} {colors.GREEN}using credentials: {colors.RESET}{username}:{password}")
                break  # Stop trying credentials if one works
            except psycopg2.OperationalError as caught_error:
                print(f"{colors.RED}Could not connect to PostgreSQL on {colors.RESET}{host} {colors.RED}with credentials: {colors.RESET}{username}:{password}: {caught_error}")
