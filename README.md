# Relay Enumerator

Relay Enumerator is a Python program that scans a list of hostnames, resolves their IP addresses, and performs various operations such as port scanning, connecting to PostgreSQL, and SSH login attempts. This is for research purposes and should only be used in sandbox environments, do not attempt to gain unauthorized access to relays.

## Prerequisites

Install dependencies by running:

```
pip install -r requirements.txt

```

## Getting started

To run the enumerator program you should first populate the `hostnames.txt` files with hosts you want to scan. The program will read through this list, resolve the host's ip address and then scan for open ports as well as weak `ssh` and `postgresql` security measures.

Running the enumerator is as easy as:

```
python3 pg_test.py
```

The program will create a database of the hosts you scanned, creaiting columns for  `hostname`, `ip address`, `open ports`, `postgres open` and `last scanned`.


Hostname             | IP Address     | Open Ports | PostgreSQL Open | Last Scanned
---------------------|----------------|------------|-----------------|--------------
example.com          | 192.168.0.1    | 22, 80     | Yes             | 1633204314
test.domain          | 10.0.0.1       | 443        | No              | 1633205412
mockhost.local       | 172.16.0.1     | 5432       | Yes             | 1633206523

## To Do
* Update scripts to scan for more vulnerabilites
    * Provide guidance to relay admin to remediate
* Collect Nip 20 contact info for relay admin
* Integratate with [nostr_note_generator](https://github.com/UTXOnly/nostr_note_generator)
    * To test relay's response to spam
    * Message relay admin if vulnerabilites are found

## Contributing

Contributions are welcome! If you encounter any issues or have suggestions for improvements, please open an issue or submit a pull request.

## License

[MIT License](https://opensource.org/license/mit/)

