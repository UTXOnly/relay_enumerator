"""
This module handles the removal of duplicate hosts from the database.
"""

from dotenv import load_dotenv
import connection_param

load_dotenv()

conn = connection_param.conn
GREEN = connection_param.GREEN
RED = connection_param.RED
RESET = connection_param.RESET
YELLOW = connection_param.YELLOW

def remove_duplicate_hosts():
    """
    Remove duplicate hosts from the database.
    """
    cur = conn.cursor()
    cur.execute(
        "SELECT hostname, COUNT(*) FROM hosts GROUP BY hostname HAVING COUNT(*) > 1"
    )  # find duplicate hostnames
    rows = cur.fetchall()
    for row in rows:
        hostname = row[0]
        print(f"Processing duplicate hostname: {hostname}")
        cur.execute(
            "SELECT id, last_scanned FROM hosts WHERE hostname = %s ORDER BY last_scanned ASC NULLS FIRST",
            (hostname,),
        )
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
