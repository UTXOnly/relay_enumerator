import requests

URL = "https://api.nostr.watch/v1/public"


response = requests.get(URL)

if response.status_code == 200:
    data = response.json()
    items_list = []
    for item in data:
        items_list.append(item)
        print(f"Added item {item} to the list")
    print(len(items_list))
else:
    print("Error: Unable to fetch data from API")
