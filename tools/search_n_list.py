import requests
from .base import get_onedrive_client

def onedrive_list_root_files_folders():
    client = get_onedrive_client()
    if not client:
        return ("Could not get OneDrive client")

    url = f"{client['base_url']}/me/drive/root/children"

    response = requests.get(url, headers=client['headers'])

    if response.ok:
        files = response.json()
        return ("Files:", files)
    else:
        return ("Error:", response.status_code, response.text)

def onedrive_list_inside_folder(folder_id):
    client = get_onedrive_client()
    if not client:
        return ("Could not get OneDrive client")

    url = f"{client['base_url']}/me/drive/items/{folder_id}/children"

    response = requests.get(url, headers=client['headers'])

    if response.ok:
        items = response.json()
        return ("Items inside folder:", items)
    else:
        return ("Error:", response.status_code, response.text)

def onedrive_search_item_by_name(itemname):
    client = get_onedrive_client()
    if not client:
        return ("Could not get OneDrive client")

    url = f"{client['base_url']}/me/drive/root/search(q='{itemname}')"
    response = requests.get(url, headers=client['headers'])

    if response.ok:
        items = response.json()
        return ("Found items:", items)
    else:
        return ("Error:", response.status_code, response.text)

def onedrive_search_folder_by_name(folder_name):
    client = get_onedrive_client()
    if not client:
        return ("Could not get OneDrive client")

    url = f"{client['base_url']}/me/drive/root/search(q='{folder_name}')"
    response = requests.get(url, headers=client['headers'])

    if response.ok:
        data = response.json()
        # Filter only folders
        folders = [item for item in data.get('value', []) if 'folder' in item]
        return ("Found folders:", folders)
    else:
        return ("Error:", response.status_code, response.text)

def onedrive_get_item_by_id(item_id):
    client = get_onedrive_client()
    if not client:
        return ("Could not get OneDrive client")

    url = f"{client['base_url']}/me/drive/items/{item_id}"

    response = requests.get(url, headers=client['headers'])

    if response.ok:
        data = response.json()
        return data
    else:
        return ("Error:", response.status_code, response.text)
