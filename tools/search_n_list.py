import requests
from base import get_onedrive_client

def list_root_files_folders():
    client = get_onedrive_client()
    if not client:
        print("Could not get OneDrive client")
        return

    url = f"{client['base_url']}/me/drive/root/children"

    response = requests.get(url, headers=client['headers'])

    if response.ok:
        files = response.json()
        print("Files:", files)
    else:
        print("Error:", response.status_code, response.text)

def list_inside_folder(folder_id):
    client = get_onedrive_client()
    if not client:
        print("Could not get OneDrive client")
        return

    url = f"{client['base_url']}/me/drive/items/{folder_id}/children"

    response = requests.get(url, headers=client['headers'])

    if response.ok:
        items = response.json()
        print("Items inside folder:", items)
    else:
        print("Error:", response.status_code, response.text)

def search_file(filename):
    client = get_onedrive_client()
    if not client:
        print("Could not get OneDrive client")
        return

    url = f"{client['base_url']}/me/drive/root/search(q='{filename}')"
    response = requests.get(url, headers=client['headers'])

    if response.ok:
        items = response.json()
        print("Found items:", items)
    else:
        print("Error:", response.status_code, response.text)

def search_folder(folder_name):
    client = get_onedrive_client()
    if not client:
        print("Could not get OneDrive client")
        return

    url = f"{client['base_url']}/me/drive/root/search(q='{folder_name}')"
    response = requests.get(url, headers=client['headers'])

    if response.ok:
        data = response.json()
        # Filter only folders
        folders = [item for item in data.get('value', []) if 'folder' in item]
        print("Found folders:", folders)
    else:
        print("Error:", response.status_code, response.text)

def get_file_by_id(file_id):
    client = get_onedrive_client()
    if not client:
        print("Could not get OneDrive client")
        return

    url = f"{client['base_url']}/me/drive/items/{file_id}"

    response = requests.get(url, headers=client['headers'])

    if response.ok:
        data = response.json()
        return data
    else:
        print("Error:", response.status_code, response.text)

def list_recent_files(since_datetime):
    client = get_onedrive_client()
    if not client:
        print("Could not get OneDrive client")
        return

    url = f"{client['base_url']}/me/drive/root/children?$filter=lastModifiedDateTime ge {since_datetime}"
    response = requests.get(url, headers=client['headers'])

    if response.ok:
        data = response.json()
        print("Recently modified files:", data)
    else:
        print("Error:", response.status_code, response.text)

def get_file_content(file_id):
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

def list_shared_files():
    client = get_onedrive_client()
    if not client:
        print("Could not get OneDrive client")
        return

    url = f"{client['base_url']}/me/drive/sharedWithMe"
    response = requests.get(url, headers=client['headers'])

    if response.ok:
        items = response.json()
        print("Files shared with me:", items)
    else:
        print("Error:", response.status_code, response.text)



if __name__ == "__main__":
    #list_root_files_folders()
    #list_inside_folder('9070248CB48F76D1!sc69751d3820a41ddac373e7b209be2f0')
    #search_file('newtestfile')
    #search_folder('new')
    #print(get_file_by_id('9070248CB48F76D1!s789c335b3a4c492ca35fc7f1f962aa22'))
    #list_shared_files()
    pass