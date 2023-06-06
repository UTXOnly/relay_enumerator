# pylint: disable=C0301,C0114,C0115,W0718, C0304, C0305
# This line is longer than the maximum allowed length
# Missing module docstring
# Missing class docstring
# Catching too general exception Exception (broad-exception-caught)

import requests

URL = "https://api.nostr.watch/v1/public"

response = requests.get(URL, timeout=5)

if response.status_code == 200:
    data = response.json()
    items_list = []
    for item in data:
        items_list.append(item)
        print(f"Added item {item} to the list")
    print(len(items_list))
else:
    print("Error: Unable to fetch data from API")

