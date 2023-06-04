import asyncio
import socket
import nmap
import psycopg2
import paramiko
import traceback
import time
import os 
import json
import random
from dotenv import load_dotenv

GREEN = '\033[32m'
RED = '\033[31m'
RESET = '\033[0m'
YELLOW = '\033[33m'

load_dotenv()

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
            print(f"Deleting duplicate rows with last_scanned as None")
            cur.execute("DELETE FROM hosts WHERE id = %s", (rows_to_delete[0][0],))
            conn.commit()
            cur.execute("DELETE FROM hosts WHERE id = %s", (rows_to_delete[1][0],))
            conn.commit()
        elif len(rows_to_delete) == 2 and rows_to_delete[0][1] is None:  # if one row has last_scanned as None
            print(f"Deleting duplicate row with last_scanned as None")
            cur.execute("DELETE FROM hosts WHERE id = %s", (rows_to_delete[0][0],))
            conn.commit()
        else:  # delete the older record
            print(f"Deleting older duplicate row")
            cur.execute("DELETE FROM hosts WHERE id = %s", (rows_to_delete[0][0],))
            conn.commit()

remove_duplicate_hosts()
