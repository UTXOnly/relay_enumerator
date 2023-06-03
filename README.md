Certainly! Here's a sample GitHub README.md file written in raw Markdown to guide users on how to use your program:

```markdown
# Relay Enumerator

Relay Enumerator is a Python program that scans a list of hostnames, resolves their IP addresses, and performs various operations such as port scanning, connecting to PostgreSQL, and SSH login attempts.

## Prerequisites

- Python 3.x
- PostgreSQL database
- Nmap tool
- Paramiko library

## Installation

1. Clone the repository:

   ```shell
   git clone https://github.com/your-username/relay-enumerator.git
   ```

2. Change into the project directory:

   ```shell
   cd relay-enumerator
   ```

3. Install the required Python dependencies using pip:

   ```shell
   pip install -r requirements.txt
   ```

4. Set up the PostgreSQL database:

   - Create a new database.
   - Update the `.env` file with the appropriate database connection details.

5. Prepare the hostnames file:

   - Create a file named `hostnames.txt` in the project directory.
   - Add each hostname you want to scan on a new line.

6. Update the credentials:

   - Modify the `credentials` dictionary in `pg_test.py` to include the desired credentials for PostgreSQL and SSH login attempts.

## Usage

1. Initialize the database:

   Run the following command to create the necessary database tables:

   ```shell
   python3 pg_test.py init
   ```

2. Run the program:

   ```shell
   python3 pg_test.py
   ```

   This will start the scanning process, which includes resolving hostnames, scanning ports, connecting to PostgreSQL, and attempting SSH logins.

3. View the results:

   The program will output the status of each operation, including open ports, successful database updates, and SSH login attempts.

## Contributing

Contributions are welcome! If you encounter any issues or have suggestions for improvements, please open an issue or submit a pull request.

## License

[MIT License](LICENSE)
```

Feel free to modify and enhance the README.md file according to your specific program and requirements.
