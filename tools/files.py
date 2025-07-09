import requests
from .base import get_onedrive_client
from .search_n_list import onedrive_list_inside_folder
import os


def onedrive_read_file_content(file_id):
    client = get_onedrive_client()
    if not client:
        return ("Could not get OneDrive client")

    url = f"{client['base_url']}/me/drive/items/{file_id}/content"
    response = requests.get(url, headers=client['headers'])

    if response.ok:
        return (response.text)
    else:
        return ("Error:", response.status_code, response.text)

def onedrive_overwrite_file_by_id(file_id, new_content):
    client = get_onedrive_client()
    if not client:
        return ("Could not get OneDrive client")

    url = f"{client['base_url']}/me/drive/items/{file_id}/content"

    response = requests.put(url, headers=client['headers'], data=new_content.encode('utf-8'))

    if response.ok:
        return ("File overwritten successfully:", response.json())
    else:
        return ("Error:", response.status_code, response.text)


def onedrive_create_file(parent_folder_id, new_file_name, data=None, if_exists='error'):
    """
    if_exists: 'error' → abort if exists
               'rename' → create with new unique name
               'replace' → overwrite
    """
    client = get_onedrive_client()
    if not client:
        return ("Could not get OneDrive client")

    # Step 1: list files/folders inside parent folder
    existing_items = onedrive_list_inside_folder(parent_folder_id)
    if existing_items is None:
        return ("Could not list folder contents")

    existing_names = [item['name'] for item in existing_items.get('value', [])]

    # Step 2: decide
    final_name = new_file_name
    if new_file_name in existing_names:
        if if_exists == 'error':
            return (f"File '{new_file_name}' already exists. Aborting.")
        elif if_exists == 'rename':
            import uuid
            name, ext = os.path.splitext(new_file_name)
            final_name = f"{name}_{uuid.uuid4().hex}{ext}"
            return (f"File exists. Creating new file as '{final_name}'")
        elif if_exists == 'replace':
            return (f"File exists. Will replace.")
        else:
            return ("Invalid if_exists option.")

    url = f"{client['base_url']}/me/drive/items/{parent_folder_id}:/{final_name}:/content"
    put_response = requests.put(url, headers=client['headers'], data=data or '')

    if put_response.ok:
        return ("File created:", put_response.json())
    else:
        return ("Error creating file:", put_response.status_code, put_response.text)

def onedrive_create_file_in_root(new_file_name, data=None, if_exists='error'):
    """
    if_exists: 'error' → abort if exists
               'rename' → create with unique name
               'replace' → overwrite
    """
    client = get_onedrive_client()
    if not client:
        return ("Could not get OneDrive client")

    # Step 1: list files/folders in root
    existing_items_resp = requests.get(
        f"{client['base_url']}/me/drive/root/children",
        headers=client['headers']
    )
    if not existing_items_resp.ok:
        return ("Could not list root contents:", existing_items_resp.status_code, existing_items_resp.text)

    existing_items = existing_items_resp.json().get('value', [])
    existing_names = [item['name'] for item in existing_items]

    # Step 2: decide
    final_name = new_file_name
    if new_file_name in existing_names:
        if if_exists == 'error':
            return (f"File '{new_file_name}' already exists. Aborting.")
        elif if_exists == 'rename':
            import uuid
            name, ext = os.path.splitext(new_file_name)
            final_name = f"{name}_{uuid.uuid4().hex}{ext}"
        elif if_exists == 'replace':
            pass  # same name, will overwrite
        else:
            return ("Invalid if_exists option.")

    # Step 3: create (upload) the file
    url = f"{client['base_url']}/me/drive/root:/{final_name}:/content"
    put_response = requests.put(url, headers=client['headers'], data=data or '')

    if put_response.ok:
        return ("File created:", put_response.json())
    else:
        return ("Error creating file:", put_response.status_code, put_response.text)
