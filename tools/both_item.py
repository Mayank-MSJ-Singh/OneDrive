import requests
from base import get_onedrive_client

def onedrive_rename_item(file_id, new_name):
    client = get_onedrive_client()
    if not client:
        return ("Could not get OneDrive client")
    url = f"{client['base_url']}/me/drive/items/{file_id}"
    data = {"name": new_name}

    response = requests.patch(url, headers={**client['headers'], "Content-Type": "application/json"}, json=data)

    if response.ok:
        return ("Renamed successfully:", response.json())
    else:
        return ("Error:", response.status_code, response.text)

def onedrive_move_item(item_id, new_parent_id):
    client = get_onedrive_client()
    if not client:
        return ("Could not get OneDrive client")

    url = f"{client['base_url']}/me/drive/items/{item_id}"
    body = {
        "parentReference": {"id": new_parent_id}
    }

    response = requests.patch(url, headers=client['headers'], json=body)

    if response.ok:
        return ("Item moved:", response.json())
    else:
        return ("Error:", response.status_code, response.text)

def onedrive_delete_item(item_id):
    client = get_onedrive_client()
    if not client:
        return ("Could not get OneDrive client")

    url = f"{client['base_url']}/me/drive/items/{item_id}"

    response = requests.delete(url, headers=client['headers'])

    if response.status_code == 204:
        return (f"Item {item_id} deleted.")
    else:
        return ("Error:", response.status_code, response.text)

if __name__ == "__main__":
    pass