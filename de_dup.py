# pylint: disable=C0301,C0114,C0115,W0718
# This line is longer than the maximum allowed length
# Missing module docstring
# Missing class docstring
# Catching too general exception Exception (broad-exception-caught)
from dotenv import load_dotenv
from connection_param import Color, Connection

conn = Connection()
colors = Color()

load_dotenv()

def remove_duplicate_hosts():
    """
    Remove duplicate hosts from the database.
    """
    cur = conn.connect().cursor()
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
            print(f"{colors.RED}Deleting duplicate rows with last_scanned as None{colors.RESET}")
            cur.execute("DELETE FROM hosts WHERE id = %s", (rows_to_delete[0][0],))
            conn.connect().commit()
            cur.execute("DELETE FROM hosts WHERE id = %s", (rows_to_delete[1][0],))
            conn.connect().commit()
        elif len(rows_to_delete) == 2 and rows_to_delete[0][1] is None:  # if one row has last_scanned as None
            print(f"{colors.RED}Deleting duplicate row with last_scanned as None{colors.RESET}")
            cur.execute("DELETE FROM hosts WHERE id = %s", (rows_to_delete[0][0],))
            conn.connect().commit()
        else:  # delete the older record
            print(f"{colors.RED}Deleting older duplicate row{colors.RESET}")
            cur.execute("DELETE FROM hosts WHERE id = %s", (rows_to_delete[0][0],))
            conn.connect().commit()

remove_duplicate_hosts()
