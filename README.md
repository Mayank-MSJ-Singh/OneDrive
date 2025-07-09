# 🔥 OneDrive MCP Server

## 🛠️ Tool Reference

| Tool                                     | Description                         | Parameters                                                                                                                                                                                  |
| ---------------------------------------- | ----------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **onedrive\_rename\_item**               | Rename file or folder by ID         | `file_id` (str): Item ID<br>`new_name` (str): New name                                                                                                                                      |
| **onedrive\_move\_item**                 | Move item to another folder         | `item_id` (str): Item ID<br>`new_parent_id` (str): Destination folder ID                                                                                                                    |
| **onedrive\_delete\_item**               | Delete item by ID                   | `item_id` (str): Item ID                                                                                                                                                                    |
| **onedrive\_read\_file\_content**        | Read content of a file              | `file_id` (str): File ID                                                                                                                                                                    |
| **onedrive\_overwrite\_file\_by\_id**    | Overwrite file content              | `file_id` (str): File ID<br>`new_content` (str): New content                                                                                                                                |
| **onedrive\_create\_file**               | Create file in a folder             | `parent_folder_id` (str): Folder ID<br>`new_file_name` (str): File name<br>`data` (str, optional): File content<br>`if_exists` (error/rename/replace): Conflict resolution (default: error) |
| **onedrive\_create\_file\_in\_root**     | Create file in root                 | `new_file_name` (str): File name<br>`data` (str, optional): File content<br>`if_exists` (error/rename/replace): Conflict resolution (default: error)                                        |
| **onedrive\_create\_folder**             | Create folder inside another folder | `parent_folder_id` (str): Folder ID<br>`new_folder_name` (str): Folder name<br>`behavior` (fail/replace/rename): Conflict resolution (default: fail)                                        |
| **onedrive\_create\_folder\_in\_root**   | Create folder in root               | `folder_name` (str): Folder name                                                                                                                                                            |
| **onedrive\_list\_root\_files\_folders** | List items in root                  | –                                                                                                                                                                                           |
| **onedrive\_list\_inside\_folder**       | List items in a folder              | `folder_id` (str): Folder ID                                                                                                                                                                |
| **onedrive\_search\_item\_by\_name**     | Search files/folders by name        | `itemname` (str): Search query                                                                                                                                                              |
| **onedrive\_search\_folder\_by\_name**   | Search folders by name              | `folder_name` (str): Folder name                                                                                                                                                            |
| **onedrive\_get\_item\_by\_id**          | Get metadata by ID                  | `item_id` (str): Item ID                                                                                                                                                                    |
| **onedrive\_list\_shared\_items**        | List items shared with user         | –                                                                                                                                                                                           |
| **onedrive\_create\_share\_link**        | Create shareable link               | `item_id` (str): Item ID<br>`link_type` (view/edit/embed): Permissions (default: view)<br>`scope` (anonymous/organization): Audience (default: anonymous)                                   |

## ⚡ Key Features

* **Dual Transport**

  * SSE endpoint: `/sse`
  * Streamable HTTP endpoint: `/mcp` (enable JSON response with `--json-response`)
* **Auth**: Add `x-auth-token` header to each request
* **Structured Errors**: Clear error messages for easier debugging
* **Logging**: Choose log level with `--log-level` (DEBUG, INFO, WARNING, ERROR, CRITICAL)

