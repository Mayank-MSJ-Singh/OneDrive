import requests
from base import get_onedrive_client

def list_shared_items():
    client = get_onedrive_client()
    if not client:
        print("Could not get OneDrive client")
        return

    url = f"{client['base_url']}/me/drive/sharedWithMe"
    response = requests.get(url, headers=client['headers'])

    if response.ok:
        items = response.json()
        print("Items shared with me:", items)
    else:
        print("Error:", response.status_code, response.text)

def onedrive_create_share_link(item_id, link_type="view"):
    """
    link_type can be:
      - view (read-only)
      - edit (edit)
      - embed (embed)
    """
    client = get_onedrive_client()
    if not client:
        print("Could not get OneDrive client")
        return

    url = f"{client['base_url']}/me/drive/items/{item_id}/createLink"
    data = {
        "type": link_type,
        "scope": "anonymous"  # or "organization" if you want to limit
    }

    response = requests.post(
        url,
        headers={**client['headers'], "Content-Type": "application/json"},
        json=data
    )

    if response.ok:
        result = response.json()
        print("Share link created:", result['link']['webUrl'])
        return result['link']['webUrl']
    else:
        print("Error:", response.status_code, response.text)

if __name__ == "__main__":
    pass