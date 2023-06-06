# pylint: disable=C0301,C0114,C0115
# This line is longer than the maximum allowed length
# Missing module docstring
# Missing class docstring

# Your code here

import time
import concurrent.futures
import asyncio
import socket
import psycopg2
import nmap
from dotenv import load_dotenv
from connection_param import Color, Connection

load_dotenv()

conn = Connection()
colors = Color()

def initialize_database(conn):
    """
    Initialize the database by creating the necessary table if it doesn't exist.
    """
    try:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS hosts (
                id SERIAL PRIMARY KEY,
                hostname VARCHAR(255),
                ip_address VARCHAR(255),
                open_ports VARCHAR(255),
                postgres_open BOOLEAN,
                last_scanned BIGINT,
                ssh_login VARCHAR(255)
            );
        """)
        conn.commit()
        print("Database initialization complete.")
    except psycopg2.Error as caught_error:
        print(f"Error occurred during database initialization: {caught_error}")

def read_hostnames_file():
    """
    Read the hostnames from the file 'real_hosts.txt' and return them as a list.
    """
    with open('real_hosts.txt', 'r', encoding='utf-8') as open_file:
        hostnames = open_file.readlines()
    hostnames = [hostname.strip() for hostname in hostnames]
    return hostnames

def resolve_hosts(hosts, conn):
    """
    Resolve the IP addresses of the given hostnames and store them in the database.
    """
    results = {}
    for host in hosts:
        cur = conn.cursor()
        try:
            cur.execute("SELECT ip_address FROM hosts WHERE hostname = %s", (host,))
            result = cur.fetchone()
            if result is not None:
                results[host] = result[0]
            else:
                ip_address = socket.gethostbyname(host)
                results[host] = ip_address
                cur.execute("INSERT INTO hosts (hostname, ip_address) VALUES (%s, %s)", (host, ip_address))
                conn.commit()
        except socket.gaierror as caught_error:
            print(f"Error resolving {host}: {str(caught_error)}")
            conn.rollback()
        except psycopg2.Error as caught_error:
            print(f"Error updating database for host {host}: {str(caught_error)}")
            conn.rollback()
    return results

def scan_host(host, hostname, scanner, conn):
    """
    Scan the specified host for open ports and update the database with the results.
    """
    print(f"Scanning host {hostname} ({host})...")
    try:
        cur = conn.cursor()
        cur.execute("SELECT last_scanned FROM hosts WHERE hostname = %s", (hostname,))
        last_scanned = cur.fetchone()[0]
        if last_scanned is None or time.time() - last_scanned >= 24 * 60 * 60:
            scanner.scan(host)
            results = scanner[host]['tcp']
            open_ports = [port for port, data in results.items() if data['state'] == 'open']
            if 5432 in open_ports:
                print(f"{colors.GREEN}Port 5432 is open on host {colors.RESET}{hostname} ({host})!")
                cur.execute("UPDATE hosts SET postgres_open = true WHERE hostname = %s", (hostname,))
                conn.commit()
                print(f"{colors.GREEN}Database record updated for host {colors.RESET}{hostname} ({host}){colors.RESET}")
            cur.execute("UPDATE hosts SET open_ports = %s WHERE hostname = %s", (open_ports, hostname))
            conn.commit()
            print(f"{colors.GREEN}Open ports ({open_ports}) updated in the database for host {colors.RESET}{hostname} ({host}){colors.RESET}")
            cur.execute("UPDATE hosts SET last_scanned = %s WHERE hostname = %s", (int(time.time()), hostname))
            conn.commit()
            print(f"{colors.GREEN}Last scanned timestamp updated in the database for host {colors.RESET}{hostname} ({host}){colors.RESET}")
        else:
            print(f"{colors.YELLOW}Skipping host{colors.RESET} {hostname} ({host}){colors.YELLOW} from port scan as it was recently scanned.{colors.RESET}")
    except psycopg2.Error as caught_error:
        print(f"{colors.RED}Error updating database for host {hostname} ({host}): {str(caught_error)}{colors.RESET}")
        conn.rollback()
    return hostname


def scan_hosts_concurrently(hosts, scanner, conn):
    """
    Scan the hosts concurrently and return the results.
    """
    loop = asyncio.get_event_loop()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        scan_tasks = [
            loop.run_in_executor(executor, scan_host, host, hostname, scanner, conn)
            for hostname, host in hosts.items()
        ]
        results = loop.run_until_complete(asyncio.gather(*scan_tasks))
    return results


def list_checker(conn):
    """
    Check the open_ports column in the database and update its format if necessary.
    """
    cur = conn.cursor()
    cur.execute("SELECT hostname, open_ports FROM hosts")
    rows = cur.fetchall()
    for row in rows:
        host, open_ports = row
        if open_ports is None:
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
    """
    The main function that orchestrates the enumeration and scanning process.
    """
    try:
        scanner = nmap.PortScanner()

        initialize_database(conn)
        hostnames = read_hostnames_file()
        host_dict = resolve_hosts(hostnames, conn)
        print(host_dict)

        # Scan hosts and collect open ports
        scan_hosts_concurrently(host_dict, scanner, conn)

        # Check and update the format of open_ports column in the database
        list_checker(conn)

        # Connect to PostgreSQL using collected open hosts and credentials
        # connect_to_postgres(postgres_open, credentials)

        # Perform SSH login on the resolved hosts
        # ssh_login('usernames.txt', 'common_root_passwords.txt')

    except socket.gaierror as caught_error:
        print(f"{colors.RED}Error resolving host: {str(caught_error)}{colors.RESET}")
        conn.rollback()

    except psycopg2.Error as caught_error:
        print(f"{colors.RED}Error updating database: {str(caught_error)}{colors.RESET}")
        conn.rollback()

    except Exception as caught_error:
        print(f"{colors.RED}Error running main function: {str(caught_error)}{colors.RESET}")

main()

       

