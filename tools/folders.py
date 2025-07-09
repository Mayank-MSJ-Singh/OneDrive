import requests
from .base import get_onedrive_client

def onedrive_create_folder(parent_folder_id, new_folder_name, behavior = "fail"):
    client = get_onedrive_client()
    if not client:
        return ("Could not get OneDrive client")

    url = f"{client['base_url']}/me/drive/items/{parent_folder_id}/children"
    data = {
        "name": new_folder_name,
        "folder": {},
        "@microsoft.graph.conflictBehavior": behavior
    }

    response = requests.post(url, headers={**client['headers'], "Content-Type": "application/json"}, json=data)

    if response.ok:
        return ("Folder created successfully:", response.json())
    else:
        return ("Error:", response.status_code, response.text)

def onedrive_create_folder_in_root(folder_name):
    client = get_onedrive_client()
    if not client:
        return ("Could not get OneDrive client")

    url = f"{client['base_url']}/me/drive/root/children"
    body = {
        "name": folder_name,
        "folder": {},
        "@microsoft.graph.conflictBehavior": "rename"
    }

    response = requests.post(url, headers=client['headers'], json=body)

    if response.ok:
        return response.json()  # info about the new folder
    else:
        return ("Error creating folder:", response.status_code, response.text)