import requests
import logging
import os
from typing import Tuple, Union, Dict, Any
from .base import get_onedrive_client
from .search_n_list import onedrive_list_inside_folder

# Configure logging
logger = logging.getLogger(__name__)


def onedrive_read_file_content(file_id: str) -> Union[str, Tuple[str, int, str]]:
    """
    Read the content of a file from OneDrive.

    Parameters:
    - file_id: The ID of the file to read

    Returns:
    - The file content as string if successful
    - Tuple with error message, status code, and response text if failed
    """
    client = get_onedrive_client()
    if not client:
        logger.error("Could not get OneDrive client")
        return ("Could not get OneDrive client",)

    url = f"{client['base_url']}/me/drive/items/{file_id}/content"

    try:
        logger.info(f"Reading content of file ID: {file_id}")
        response = requests.get(url, headers=client['headers'])

        if response.ok:
            logger.info(f"Successfully read content of file ID: {file_id}")
            return response.text
        else:
            logger.error(f"Error reading file {file_id}: {response.status_code} - {response.text}")
            return ("Error:", response.status_code, response.text)
    except Exception as e:
        logger.error(f"Exception occurred while reading file content: {e}")
        return ("Error:", str(e))


def onedrive_overwrite_file_by_id(file_id: str, new_content: str) -> Union[Tuple[str, Dict], Tuple[str, int, str]]:
    """
    Overwrite the content of an existing file in OneDrive.

    Parameters:
    - file_id: The ID of the file to overwrite
    - new_content: The new content to write to the file

    Returns:
    - Tuple with success message and response JSON if successful
    - Tuple with error message, status code, and response text if failed
    """
    client = get_onedrive_client()
    if not client:
        logger.error("Could not get OneDrive client")
        return ("Could not get OneDrive client",)

    url = f"{client['base_url']}/me/drive/items/{file_id}/content"

    try:
        logger.info(f"Overwriting content of file ID: {file_id}")
        response = requests.put(url, headers=client['headers'], data=new_content.encode('utf-8'))

        if response.ok:
            logger.info(f"Successfully overwrote file ID: {file_id}")
            return ("File overwritten successfully:", response.json())
        else:
            logger.error(f"Error overwriting file {file_id}: {response.status_code} - {response.text}")
            return ("Error:", response.status_code, response.text)
    except Exception as e:
        logger.error(f"Exception occurred while overwriting file: {e}")
        return ("Error:", str(e))


def onedrive_create_file(
        parent_folder_id: str,
        new_file_name: str,
        data: str = None,
        if_exists: str = 'error'
) -> Union[Tuple[str, Dict], Tuple[str]]:
    """
    Create a new file in a specific OneDrive folder.

    Parameters:
    - parent_folder_id: ID of the parent folder
    - new_file_name: Name for the new file
    - data: Content for the new file (optional)
    - if_exists: Behavior when file exists ('error', 'rename', or 'replace')

    Returns:
    - Tuple with success message and response JSON if successful
    - Tuple with error message if failed
    """
    client = get_onedrive_client()
    if not client:
        logger.error("Could not get OneDrive client")
        return ("Could not get OneDrive client",)

    try:
        logger.info(f"Creating file '{new_file_name}' in folder {parent_folder_id} with if_exists={if_exists}")

        # Step 1: list files/folders inside parent folder
        existing_items = onedrive_list_inside_folder(parent_folder_id)
        if existing_items is None:
            logger.error(f"Could not list contents of folder {parent_folder_id}")
            return ("Could not list folder contents",)

        existing_names = [item['name'] for item in existing_items.get('value', [])]

        # Step 2: handle existing file
        final_name = new_file_name
        if new_file_name in existing_names:
            if if_exists == 'error':
                logger.warning(f"File '{new_file_name}' already exists in folder {parent_folder_id}")
                return (f"File '{new_file_name}' already exists. Aborting.",)
            elif if_exists == 'rename':
                name, ext = os.path.splitext(new_file_name)
                final_name = f"{name}_{uuid.uuid4().hex}{ext}"
                logger.info(f"Renaming file to '{final_name}' due to naming conflict")
            elif if_exists == 'replace':
                logger.info(f"File exists, will replace '{new_file_name}'")
            else:
                logger.error(f"Invalid if_exists option: {if_exists}")
                return ("Invalid if_exists option.",)

        # Step 3: create the file
        url = f"{client['base_url']}/me/drive/items/{parent_folder_id}:/{final_name}:/content"
        put_response = requests.put(url, headers=client['headers'], data=data or '')

        if put_response.ok:
            logger.info(f"Successfully created file '{final_name}' in folder {parent_folder_id}")
            return ("File created:", put_response.json())
        else:
            logger.error(f"Error creating file: {put_response.status_code} - {put_response.text}")
            return ("Error creating file:", put_response.status_code, put_response.text)
    except Exception as e:
        logger.error(f"Exception occurred while creating file: {e}")
        return ("Error:", str(e))


def onedrive_create_file_in_root(
        new_file_name: str,
        data: str = None,
        if_exists: str = 'error'
) -> Union[Tuple[str, Dict], Tuple[str, int, str]]:
    """
    Create a new file in the root of OneDrive.

    Parameters:
    - new_file_name: Name for the new file
    - data: Content for the new file (optional)
    - if_exists: Behavior when file exists ('error', 'rename', or 'replace')

    Returns:
    - Tuple with success message and response JSON if successful
    - Tuple with error message and details if failed
    """
    client = get_onedrive_client()
    if not client:
        logger.error("Could not get OneDrive client")
        return ("Could not get OneDrive client",)

    try:
        logger.info(f"Creating file '{new_file_name}' in root with if_exists={if_exists}")

        # Step 1: list files/folders in root
        existing_items_resp = requests.get(
            f"{client['base_url']}/me/drive/root/children",
            headers=client['headers']
        )
        if not existing_items_resp.ok:
            logger.error(
                f"Could not list root contents: {existing_items_resp.status_code} - {existing_items_resp.text}")
            return ("Could not list root contents:", existing_items_resp.status_code, existing_items_resp.text)

        existing_items = existing_items_resp.json().get('value', [])
        existing_names = [item['name'] for item in existing_items]

        # Step 2: handle existing file
        final_name = new_file_name
        if new_file_name in existing_names:
            if if_exists == 'error':
                logger.warning(f"File '{new_file_name}' already exists in root")
                return (f"File '{new_file_name}' already exists. Aborting.",)
            elif if_exists == 'rename':
                name, ext = os.path.splitext(new_file_name)
                final_name = f"{name}_{uuid.uuid4().hex}{ext}"
                logger.info(f"Renaming file to '{final_name}' due to naming conflict")
            elif if_exists == 'replace':
                logger.info(f"File exists, will replace '{new_file_name}'")
            else:
                logger.error(f"Invalid if_exists option: {if_exists}")
                return ("Invalid if_exists option.",)

        # Step 3: create the file
        url = f"{client['base_url']}/me/drive/root:/{final_name}:/content"
        put_response = requests.put(url, headers=client['headers'], data=data or '')

        if put_response.ok:
            logger.info(f"Successfully created file '{final_name}' in root")
            return ("File created:", put_response.json())
        else:
            logger.error(f"Error creating file: {put_response.status_code} - {put_response.text}")
            return ("Error creating file:", put_response.status_code, put_response.text)
    except Exception as e:
        logger.error(f"Exception occurred while creating file in root: {e}")
        return ("Error:", str(e))