import requests
from base import get_onedrive_client

def list_root_files_folders():
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

def search_file(filename):
    client = get_onedrive_client()
    if not client:
        return ("Could not get OneDrive client")

    url = f"{client['base_url']}/me/drive/root/search(q='{filename}')"
    response = requests.get(url, headers=client['headers'])

    if response.ok:
        items = response.json()
        return ("Found items:", items)
    else:
        return ("Error:", response.status_code, response.text)

def search_folder(folder_name):
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

def get_file_by_id(file_id):
    client = get_onedrive_client()
    if not client:
        return ("Could not get OneDrive client")

    url = f"{client['base_url']}/me/drive/items/{file_id}"

    response = requests.get(url, headers=client['headers'])

    if response.ok:
        data = response.json()
        return data
    else:
        return ("Error:", response.status_code, response.text)


def onedrive_get_file_content(file_id):
    client = get_onedrive_client()
    if not client:
        return ("Could not get OneDrive client")

    url = f"{client['base_url']}/me/drive/items/{file_id}/content"
    response = requests.get(url, headers=client['headers'])

    if response.ok:
        return (response.text)  # or response.content for binary
    else:
        return ("Error:", response.status_code, response.text)



if __name__ == "__main__":
    #list_root_files_folders()
    #list_inside_folder('9070248CB48F76D1!sc69751d3820a41ddac373e7b209be2f0')
    #search_file('newtestfile')
    #search_folder('new')
    #return (get_file_by_id('9070248CB48F76D1!s789c335b3a4c492ca35fc7f1f962aa22'))
    #list_shared_files()
    pass