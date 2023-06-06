import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

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

def remove_duplicate_hosts():
    cur = conn.cursor()
    cur.execute("SELECT hostname, COUNT(*) FROM hosts GROUP BY hostname HAVING COUNT(*) > 1")  # find duplicate hostnames
    rows = cur.fetchall()
    for row in rows:
        hostname = row[0]
        print(f"Processing duplicate hostname: {hostname}")
        cur.execute("SELECT id, last_scanned FROM hosts WHERE hostname = %s ORDER BY last_scanned ASC NULLS FIRST", (hostname,))
        rows_to_delete = cur.fetchall()
        if len(rows_to_delete) == 2:  # if both rows have last_scanned as None
            print(f"{RED}Deleting duplicate rows with last_scanned as None{RESET}")
            cur.execute("DELETE FROM hosts WHERE id = %s", (rows_to_delete[0][0],))
            conn.commit()
            cur.execute("DELETE FROM hosts WHERE id = %s", (rows_to_delete[1][0],))
            conn.commit()
        elif len(rows_to_delete) == 2 and rows_to_delete[0][1] is None:  # if one row has last_scanned as None
            print(f"{RED}Deleting duplicate row with last_scanned as None{RESET}")
            cur.execute("DELETE FROM hosts WHERE id = %s", (rows_to_delete[0][0],))
            conn.commit()
        else:  # delete the older record
            print(f"{RED}Deleting older duplicate row{RESET}")
            cur.execute("DELETE FROM hosts WHERE id = %s", (rows_to_delete[0][0],))
            conn.commit()

remove_duplicate_hosts()
