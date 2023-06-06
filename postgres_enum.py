import psycopg2

GREEN = '\033[32m'
RED = '\033[31m'
RESET = '\033[0m'
YELLOW = '\033[33m'\

def connect_to_postgres(hosts, credentials):
    for host in hosts:
        for username, password in credentials.items():
            try:
                conn = psycopg2.connect(
                    host=host,
                    user=username,
                    password=password
                )
                print(f"{GREEN}Successfully connected to PostgreSQL on {RESET}{host} {GREEN}using credentials: {RESET}{username}:{password}")
                break  # Stop trying credentials if one works
            except Exception as error:
                print(f"{RED}Could not connect to PostgreSQL on {RESET}{host} {RED}with credentials: {RESET}{username}:{password}: {error}")