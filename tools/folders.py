import requests
from base import get_onedrive_client

def onedrive_create_folder(parent_folder_id, new_folder_name, behavior = "fail"):
    client = get_onedrive_client()
    if not client:
        print("Could not get OneDrive client")
        return

    url = f"{client['base_url']}/me/drive/items/{parent_folder_id}/children"
    data = {
        "name": new_folder_name,
        "folder": {},
        "@microsoft.graph.conflictBehavior": behavior
    }

    response = requests.post(url, headers={**client['headers'], "Content-Type": "application/json"}, json=data)

    if response.ok:
        print("Folder created successfully:", response.json())
    else:
        print("Error:", response.status_code, response.text)

if __name__ == "__main__":
    pass