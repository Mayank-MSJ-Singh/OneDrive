import requests
from base import get_onedrive_client


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

if __name__ == '__main__':
    print("   ")
    onedrive_read_file_content('9070248CB48F76D1!s789c335b3a4c492ca35fc7f1f962aa22')
    print("   ")
    onedrive_overwrite_file_by_id('9070248CB48F76D1!s789c335b3a4c492ca35fc7f1f962aa22', 'Hello From OneDrive')
    print("   ")
    onedrive_read_file_content('9070248CB48F76D1!s789c335b3a4c492ca35fc7f1f962aa22')

    pass