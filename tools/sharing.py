import requests
from base import get_onedrive_client

def list_shared_items():
    client = get_onedrive_client()
    if not client:
        print("Could not get OneDrive client")
        return

    url = f"{client['base_url']}/me/drive/sharedWithMe"
    response = requests.get(url, headers=client['headers'])

    if response.ok:
        items = response.json()
        print("Items shared with me:", items)
    else:
        print("Error:", response.status_code, response.text)

if __name__ == "__main__":
    pass