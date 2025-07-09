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

if __name__ == '__main__':
    onedrive_read_file_content('9070248CB48F76D1!s6aa0a1237a3b41c2b0a49813afd9cc30')