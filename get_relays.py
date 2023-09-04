import requests

def fetch_data_from_api():
    URL = "https://api.nostr.watch/v1/online"
    try:
        response = requests.get(URL, timeout=5)
        response.raise_for_status()  # Raise an exception if the status code is not 200
        data = response.json()
        items_list = []
        for item in data:
            hostname = item.replace("wss://", "")  # Remove "wss://" from the item
            items_list.append(hostname)
            print(f"Added item {hostname} to the list")
            with open("hostnames.txt", "a") as file:
                file.write(hostname + "\n")
        print(len(items_list))
        return items_list
    except requests.exceptions.RequestException as e:
        print("Error: Unable to fetch data from API")
        return []

if __name__ == "__main__":
    items = fetch_data_from_api()
    print(items)


