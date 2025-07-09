import requests
from base import get_onedrive_client
from search_n_list import onedrive_list_inside_folder
import os


def onedrive_read_file_content(file_id):
    client = get_onedrive_client()
    if not client:
        print("Could not get OneDrive client")
        return

    url = f"{client['base_url']}/me/drive/items/{file_id}/content"
    response = requests.get(url, headers=client['headers'])

    if response.ok:
        print("File content:")
        print(response.text)  # or response.content for binary
    else:
        print("Error:", response.status_code, response.text)

def onedrive_overwrite_file_by_id(file_id, new_content):
    client = get_onedrive_client()
    if not client:
        print("Could not get OneDrive client")
        return

    url = f"{client['base_url']}/me/drive/items/{file_id}/content"

    response = requests.put(url, headers=client['headers'], data=new_content.encode('utf-8'))

    if response.ok:
        print("File overwritten successfully:", response.json())
    else:
        print("Error:", response.status_code, response.text)


def onedrive_create_file(parent_folder_id, new_file_name, data=None, if_exists='error'):
    """
    if_exists: 'error' → abort if exists
               'rename' → create with new unique name
               'replace' → overwrite
    """
    client = get_onedrive_client()
    if not client:
        print("Could not get OneDrive client")
        return

    # Step 1: list files/folders inside parent folder
    existing_items = onedrive_list_inside_folder(parent_folder_id)
    if existing_items is None:
        print("Could not list folder contents")
        return

    existing_names = [item['name'] for item in existing_items.get('value', [])]

    # Step 2: decide
    final_name = new_file_name
    if new_file_name in existing_names:
        if if_exists == 'error':
            print(f"File '{new_file_name}' already exists. Aborting.")
            return
        elif if_exists == 'rename':
            import uuid
            name, ext = os.path.splitext(new_file_name)
            final_name = f"{name}_{uuid.uuid4().hex}{ext}"
            print(f"File exists. Creating new file as '{final_name}'")
        elif if_exists == 'replace':
            print(f"File exists. Will replace.")
        else:
            print("Invalid if_exists option.")
            return

    # Step 3: upload (this will overwrite if file exists, but we controlled name above)
    upload_url = f"{client['base_url']}/me/drive/items/{parent_folder_id}:/{final_name}:/content"
    put_response = requests.put(upload_url, headers=client['headers'], data=data or '')

    if put_response.ok:
        print("File created:", put_response.json())
    else:
        print("Error creating file:", put_response.status_code, put_response.text)

if __name__ == '__main__':
    '''
    print("   ")
    onedrive_read_file_content('9070248CB48F76D1!s789c335b3a4c492ca35fc7f1f962aa22')
    print("   ")
    onedrive_overwrite_file_by_id('9070248CB48F76D1!s789c335b3a4c492ca35fc7f1f962aa22', 'Hello From OneDrive')
    print("   ")
    onedrive_read_file_content('9070248CB48F76D1!s789c335b3a4c492ca35fc7f1f962aa22')
    '''
    #onedrive_create_empty_file_in_folder('9070248CB48F76D1!sc69751d3820a41ddac373e7b209be2f0', 'new_file.txt')

    pass