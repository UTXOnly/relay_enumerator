import asyncio
import socket
import nmap
import psycopg2
import traceback
import time
import os
import concurrent.futures
from dotenv import load_dotenv

GREEN = '\033[32m'
RED = '\033[31m'
RESET = '\033[0m'
YELLOW = '\033[33m'

load_dotenv()

def initialize_database(conn):
    # Load environment variables from .env file
    try:
        cur = conn.cursor()
        # Create the 'hosts' table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS hosts (
                id SERIAL PRIMARY KEY,
                hostname VARCHAR(255),
                ip_address VARCHAR(255),
                open_ports VARCHAR(255),
                postgres_open BOOLEAN,
                last_scanned BIGINT
            );
        """)

        conn.commit()

        print("Database initialization complete.")

    except psycopg2.Error as e:
        print(f"Error occurred during database initialization: {e}")

def read_hostnames_file():
    # Open the file for reading
    with open('real_hosts.txt', 'r') as f:
        # Read all lines from the file into a list
        hostnames = f.readlines()

    # Strip newline characters from each line in the list
    hostnames = [hostname.strip() for hostname in hostnames]

    # Return the list of hostnames
    return hostnames

def resolve_hosts(hosts, conn):
    results = {}
    for host in hosts:
        cur = conn.cursor()
        cur.execute("SELECT ip_address FROM hosts WHERE hostname = %s", (host,))
        result = cur.fetchone()
        if result is not None:
            results[host] = result[0]
        else:
            try:
                ip = socket.gethostbyname(host)
                results[host] = ip
                cur.execute("INSERT INTO hosts (hostname, ip_address) VALUES (%s, %s)", (host, ip))
                conn.commit()
            except socket.error as err:
                print(f"Error resolving {host}: {err}")
    return results

def scan_host(host, hostname, scanner, conn):
    print(f"Scanning host {hostname} ({host})...")
    try:
        scanner.scan(host)
        results = scanner[host]['tcp']
    except Exception as e:
        print(f"{RED}Error scanning host {hostname} ({host}): {str(e)}{RESET}")
        return None

    cur = conn.cursor()
    open_ports = []
    for port, data in results.items():
        if data['state'] == 'open':
            open_ports.append(port)

    if 5432 in open_ports:
        try:
            print(f"{GREEN}Port 5432 is open on host {RESET}{hostname} ({host})!")
            cur.execute("UPDATE hosts SET postgres_open = true WHERE hostname = %s", (hostname,))
            conn.commit()
            print(f"{GREEN}Database record updated for host {RESET}{hostname} ({host}){RESET}")
        except Exception as e:
            print(f"{RED}Error updating database for host {hostname} ({host}): {str(e)}{RESET}")
            
    try:
        cur.execute("UPDATE hosts SET open_ports = %s WHERE hostname = %s", (open_ports, hostname))
        conn.commit()
        print(f"{GREEN}Open ports ({open_ports}) updated in the database for host {RESET}{hostname} ({host}){RESET}")
    except Exception as e:
        print(f"{RED}Error updating database for host {hostname} ({host}): {str(e)}{RESET}")
        
    cur.execute("SELECT last_scanned FROM hosts WHERE hostname = %s", (hostname,))
    last_scanned = cur.fetchone()[0]
    
    if last_scanned is None or time.time() - last_scanned >= 24 * 60 * 60:
        try:
            cur.execute("UPDATE hosts SET last_scanned = %s WHERE hostname = %s", (int(time.time()), hostname))
            conn.commit()
            print(f"{GREEN}Last scanned timestamp updated in the database for host {RESET}{hostname} ({host}){RESET}")
        except Exception as e:
            print(f"{RED}Error updating last scanned timestamp for host {hostname} ({host}): {str(e)}{RESET}")
    
    return hostname

def scan_hosts_concurrently(hosts, scanner, conn):
    loop = asyncio.get_event_loop()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Create a list of future tasks for scanning each host concurrently
        scan_tasks = [
            loop.run_in_executor(executor, scan_host, host, hostname, scanner, conn)
            for hostname, host in hosts.items()
        ]

        # Await the completion of all tasks
        results = loop.run_until_complete(asyncio.gather(*scan_tasks))

    return results

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
                conn.close()
                break  # Stop trying credentials if one works
            except Exception as e:
                print(f"{RED}Could not connect to PostgreSQL on {RESET}{host} {RED}with credentials: {RESET}{username}:{password}: {e}")

def list_checker(conn):
    cur = conn.cursor()
    cur.execute("SELECT hostname, open_ports FROM hosts")
    rows = cur.fetchall()
    for row in rows:
        host, open_ports = row
         
        if open_ports is None:   # Skip the row if open_ports is None
            continue
        elif not isinstance(open_ports, list):
            port_list = []
            for port in open_ports.split(','):
                port = port.strip()
                if port.isdigit():
                    port_list.append(int(port))
            cur.execute("UPDATE hosts SET open_ports = %s WHERE hostname = %s", (port_list, host))
            conn.commit()

def main():
    try:
        # Create a new Nmap scanner object
        scanner = nmap.PortScanner()

        # Resolve hosts
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT'),
            dbname=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD')
        )

        # Load environment variables from .env file
        load_dotenv()

        # Initialize the database
        initialize_database(conn)

        # Read hostnames from file
        hostnames = read_hostnames_file()

        # Resolve hosts asynchronously
        host_dict = resolve_hosts(hostnames, conn)
        print(host_dict)

        # Scan hosts and collect open ports
        postgres_open = scan_hosts_concurrently(host_dict, scanner, conn)

        # Connect to PostgreSQL using collected open hosts and credentials
        #connect_to_postgres(postgres_open, credentials)

        # Perform SSH login on the resolved hosts
        # ssh_login('usernames.txt', 'common_root_passwords.txt')

    except Exception as e:
        print(f"{RED}Error running main function: {str(e)}{RESET}")


