import contextlib
import logging
import os
import json
from collections.abc import AsyncIterator
from typing import Any, Dict, List
import asyncio

import click
import mcp.types as types
from mcp.server.lowlevel import Server
from mcp.server.sse import SseServerTransport
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from starlette.applications import Starlette
from starlette.responses import Response
from starlette.routing import Mount, Route
from starlette.types import Receive, Scope, Send
from dotenv import load_dotenv

from tools import (
    # Base
    auth_token_context,

    # Both Items (Files & Folders)
    onedrive_rename_item,
    onedrive_move_item,
    onedrive_delete_item,

    # Files
    onedrive_read_file_content,
    onedrive_overwrite_file_by_id,
    onedrive_create_file,
    onedrive_create_file_in_root,

    # Folders
    onedrive_create_folder,
    onedrive_create_folder_in_root,

    # Search & List
    onedrive_list_root_files_folders,
    onedrive_list_inside_folder,
    onedrive_search_item_by_name,
    onedrive_search_folder_by_name,
    onedrive_get_item_by_id,

    #Sharing
    onedrive_list_shared_items,
    onedrive_create_share_link
)


# Configure logging
logger = logging.getLogger(__name__)

load_dotenv()

ONEDRIVE_MCP_SERVER_PORT = int(os.getenv("ONEDRIVE_MCP_SERVER_PORT", "5000"))

@click.command()
@click.option("--port", default=ONEDRIVE_MCP_SERVER_PORT, help="Port to listen on for HTTP")
@click.option(
    "--log-level",
    default="INFO",
    help="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
)
@click.option(
    "--json-response",
    is_flag=True,
    default=False,
    help="Enable JSON responses for StreamableHTTP instead of SSE streams",
)

def main(
    port: int,
    log_level: str,
    json_response: bool,
) -> int:
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Create the MCP server instance
    app = Server("onedrive-mcp-server")
#-------------------------------------------------------------------------------------


    @app.list_tools()
    async def list_tools() -> list[types.Tool]:
        return [
            # File Operations
            types.Tool(
                name="onedrive_rename_item",
                description="Rename a file or folder in OneDrive by its ID.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "file_id": {"type": "string", "description": "ID of the file/folder to rename"},
                        "new_name": {"type": "string", "description": "New name for the item"}
                    },
                    "required": ["file_id", "new_name"]
                }
            ),
            types.Tool(
                name="onedrive_move_item",
                description="Move an item to a different folder in OneDrive.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "item_id": {"type": "string", "description": "ID of the item to move"},
                        "new_parent_id": {"type": "string", "description": "ID of the destination folder"}
                    },
                    "required": ["item_id", "new_parent_id"]
                }
            ),
            types.Tool(
                name="onedrive_delete_item",
                description="Delete an item from OneDrive by its ID.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "item_id": {"type": "string", "description": "ID of the item to delete"}
                    },
                    "required": ["item_id"]
                }
            ),

            # File Content Operations
            types.Tool(
                name="onedrive_read_file_content",
                description="Read the content of a file from OneDrive by its ID.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "file_id": {"type": "string", "description": "ID of the file to read"}
                    },
                    "required": ["file_id"]
                }
            ),
            types.Tool(
                name="onedrive_overwrite_file_by_id",
                description="Overwrite the content of an existing file in OneDrive.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "file_id": {"type": "string", "description": "ID of the file to overwrite"},
                        "new_content": {"type": "string", "description": "New content for the file"}
                    },
                    "required": ["file_id", "new_content"]
                }
            ),

            # File Creation
            types.Tool(
                name="onedrive_create_file",
                description="Create a new file in a specific OneDrive folder.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "parent_folder_id": {"type": "string", "description": "ID of the parent folder"},
                        "new_file_name": {"type": "string", "description": "Name for the new file"},
                        "data": {"type": "string", "description": "Content for the new file (optional)"},
                        "if_exists": {
                            "type": "string",
                            "enum": ["error", "rename", "replace"],
                            "default": "error",
                            "description": "Behavior when file exists: 'error' (abort), 'rename' (create unique name), 'replace' (overwrite)"
                        }
                    },
                    "required": ["parent_folder_id", "new_file_name"]
                }
            ),
            types.Tool(
                name="onedrive_create_file_in_root",
                description="Create a new file in the root of OneDrive.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "new_file_name": {"type": "string", "description": "Name for the new file"},
                        "data": {"type": "string", "description": "Content for the new file (optional)"},
                        "if_exists": {
                            "type": "string",
                            "enum": ["error", "rename", "replace"],
                            "default": "error",
                            "description": "Behavior when file exists: 'error' (abort), 'rename' (create unique name), 'replace' (overwrite)"
                        }
                    },
                    "required": ["new_file_name"]
                }
            ),

            # Folder Operations
            types.Tool(
                name="onedrive_create_folder",
                description="Create a new folder in a specific OneDrive parent folder.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "parent_folder_id": {"type": "string", "description": "ID of the parent folder"},
                        "new_folder_name": {"type": "string", "description": "Name for the new folder"},
                        "behavior": {
                            "type": "string",
                            "enum": ["fail", "replace", "rename"],
                            "default": "fail",
                            "description": "Conflict resolution: 'fail' (return error), 'replace' (overwrite), 'rename' (unique name)"
                        }
                    },
                    "required": ["parent_folder_id", "new_folder_name"]
                }
            ),
            types.Tool(
                name="onedrive_create_folder_in_root",
                description="Create a new folder in the root of OneDrive.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "folder_name": {"type": "string", "description": "Name for the new folder"}
                    },
                    "required": ["folder_name"]
                }
            ),

            # Listing & Searching
            types.Tool(
                name="onedrive_list_root_files_folders",
                description="List all files and folders in the root of OneDrive.",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            ),
            types.Tool(
                name="onedrive_list_inside_folder",
                description="List all items inside a specific folder.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "folder_id": {"type": "string", "description": "ID of the folder to list"}
                    },
                    "required": ["folder_id"]
                }
            ),
            types.Tool(
                name="onedrive_search_item_by_name",
                description="Search for items by name in OneDrive.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "itemname": {"type": "string", "description": "Name or partial name to search for"}
                    },
                    "required": ["itemname"]
                }
            ),
            types.Tool(
                name="onedrive_search_folder_by_name",
                description="Search for folders by name in OneDrive.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "folder_name": {"type": "string", "description": "Name or partial name to search for"}
                    },
                    "required": ["folder_name"]
                }
            ),
            types.Tool(
                name="onedrive_get_item_by_id",
                description="Get item details by its ID.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "item_id": {"type": "string", "description": "ID of the item to retrieve"}
                    },
                    "required": ["item_id"]
                }
            ),

            # Sharing & Permissions
            types.Tool(
                name="onedrive_list_shared_items",
                description="List all items shared with the current user in OneDrive.",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            ),
            types.Tool(
                name="onedrive_create_share_link",
                description="Create a sharing link for a OneDrive item.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "item_id": {"type": "string", "description": "ID of the item to share"},
                        "link_type": {
                            "type": "string",
                            "enum": ["view", "edit", "embed"],
                            "default": "view",
                            "description": "Link permissions: 'view' (read-only), 'edit' (read-write), 'embed' (embeddable)"
                        },
                        "scope": {
                            "type": "string",
                            "enum": ["anonymous", "organization"],
                            "default": "anonymous",
                            "description": "Link audience: 'anonymous' (anyone), 'organization' (company only)"
                        }
                    },
                    "required": ["item_id"]
                }
            )
        ]

    @app.call_tool()
    async def call_tool(
            name: str, arguments: dict
    ) -> List[types.TextContent | types.ImageContent | types.EmbeddedResource]:

        # File Operations
        if name == "onedrive_rename_item":
            try:
                result = onedrive_rename_item(
                    file_id=arguments["file_id"],
                    new_name=arguments["new_name"]
                )
                return [
                    types.TextContent(
                        type="text",
                        text=json.dumps(result, indent=2),
                    )
                ]
            except Exception as e:
                logger.exception(f"Error renaming item: {e}")
                return [
                    types.TextContent(
                        type="text",
                        text=f"Error: {str(e)}",
                    )
                ]

        elif name == "onedrive_move_item":
            try:
                result = onedrive_move_item(
                    item_id=arguments["item_id"],
                    new_parent_id=arguments["new_parent_id"]
                )
                return [
                    types.TextContent(
                        type="text",
                        text=json.dumps(result, indent=2),
                    )
                ]
            except Exception as e:
                logger.exception(f"Error moving item: {e}")
                return [
                    types.TextContent(
                        type="text",
                        text=f"Error: {str(e)}",
                    )
                ]

        elif name == "onedrive_delete_item":
            try:
                result = onedrive_delete_item(
                    item_id=arguments["item_id"]
                )
                return [
                    types.TextContent(
                        type="text",
                        text=result,
                    )
                ]
            except Exception as e:
                logger.exception(f"Error deleting item: {e}")
                return [
                    types.TextContent(
                        type="text",
                        text=f"Error: {str(e)}",
                    )
                ]

        # File Content Operations
        elif name == "onedrive_read_file_content":
            try:
                result = onedrive_read_file_content(
                    file_id=arguments["file_id"]
                )
                return [
                    types.TextContent(
                        type="text",
                        text=result if isinstance(result, str) else json.dumps(result, indent=2),
                    )
                ]
            except Exception as e:
                logger.exception(f"Error reading file content: {e}")
                return [
                    types.TextContent(
                        type="text",
                        text=f"Error: {str(e)}",
                    )
                ]

        elif name == "onedrive_overwrite_file_by_id":
            try:
                result = onedrive_overwrite_file_by_id(
                    file_id=arguments["file_id"],
                    new_content=arguments["new_content"]
                )
                return [
                    types.TextContent(
                        type="text",
                        text=json.dumps(result, indent=2),
                    )
                ]
            except Exception as e:
                logger.exception(f"Error overwriting file: {e}")
                return [
                    types.TextContent(
                        type="text",
                        text=f"Error: {str(e)}",
                    )
                ]

        # File Creation
        elif name == "onedrive_create_file":
            try:
                result = onedrive_create_file(
                    parent_folder_id=arguments["parent_folder_id"],
                    new_file_name=arguments["new_file_name"],
                    data=arguments.get("data"),
                    if_exists=arguments.get("if_exists", "error")
                )
                return [
                    types.TextContent(
                        type="text",
                        text=json.dumps(result, indent=2),
                    )
                ]
            except Exception as e:
                logger.exception(f"Error creating file: {e}")
                return [
                    types.TextContent(
                        type="text",
                        text=f"Error: {str(e)}",
                    )
                ]

        elif name == "onedrive_create_file_in_root":
            try:
                result = onedrive_create_file_in_root(
                    new_file_name=arguments["new_file_name"],
                    data=arguments.get("data"),
                    if_exists=arguments.get("if_exists", "error")
                )
                return [
                    types.TextContent(
                        type="text",
                        text=json.dumps(result, indent=2),
                    )
                ]
            except Exception as e:
                logger.exception(f"Error creating file in root: {e}")
                return [
                    types.TextContent(
                        type="text",
                        text=f"Error: {str(e)}",
                    )
                ]

        # Folder Operations
        elif name == "onedrive_create_folder":
            try:
                result = onedrive_create_folder(
                    parent_folder_id=arguments["parent_folder_id"],
                    new_folder_name=arguments["new_folder_name"],
                    behavior=arguments.get("behavior", "fail")
                )
                return [
                    types.TextContent(
                        type="text",
                        text=json.dumps(result, indent=2),
                    )
                ]
            except Exception as e:
                logger.exception(f"Error creating folder: {e}")
                return [
                    types.TextContent(
                        type="text",
                        text=f"Error: {str(e)}",
                    )
                ]

        elif name == "onedrive_create_folder_in_root":
            try:
                result = onedrive_create_folder_in_root(
                    folder_name=arguments["folder_name"]
                )
                return [
                    types.TextContent(
                        type="text",
                        text=json.dumps(result, indent=2),
                    )
                ]
            except Exception as e:
                logger.exception(f"Error creating folder in root: {e}")
                return [
                    types.TextContent(
                        type="text",
                        text=f"Error: {str(e)}",
                    )
                ]

        # Listing & Searching
        elif name == "onedrive_list_root_files_folders":
            try:
                result = onedrive_list_root_files_folders()
                return [
                    types.TextContent(
                        type="text",
                        text=json.dumps(result, indent=2),
                    )
                ]
            except Exception as e:
                logger.exception(f"Error listing root items: {e}")
                return [
                    types.TextContent(
                        type="text",
                        text=f"Error: {str(e)}",
                    )
                ]

        elif name == "onedrive_list_inside_folder":
            try:
                result = onedrive_list_inside_folder(
                    folder_id=arguments["folder_id"]
                )
                return [
                    types.TextContent(
                        type="text",
                        text=json.dumps(result, indent=2),
                    )
                ]
            except Exception as e:
                logger.exception(f"Error listing folder contents: {e}")
                return [
                    types.TextContent(
                        type="text",
                        text=f"Error: {str(e)}",
                    )
                ]

        elif name == "onedrive_search_item_by_name":
            try:
                result = onedrive_search_item_by_name(
                    itemname=arguments["itemname"]
                )
                return [
                    types.TextContent(
                        type="text",
                        text=json.dumps(result, indent=2),
                    )
                ]
            except Exception as e:
                logger.exception(f"Error searching items: {e}")
                return [
                    types.TextContent(
                        type="text",
                        text=f"Error: {str(e)}",
                    )
                ]

        elif name == "onedrive_search_folder_by_name":
            try:
                result = onedrive_search_folder_by_name(
                    folder_name=arguments["folder_name"]
                )
                return [
                    types.TextContent(
                        type="text",
                        text=json.dumps(result, indent=2),
                    )
                ]
            except Exception as e:
                logger.exception(f"Error searching folders: {e}")
                return [
                    types.TextContent(
                        type="text",
                        text=f"Error: {str(e)}",
                    )
                ]

        elif name == "onedrive_get_item_by_id":
            try:
                result = onedrive_get_item_by_id(
                    item_id=arguments["item_id"]
                )
                return [
                    types.TextContent(
                        type="text",
                        text=json.dumps(result, indent=2),
                    )
                ]
            except Exception as e:
                logger.exception(f"Error getting item by ID: {e}")
                return [
                    types.TextContent(
                        type="text",
                        text=f"Error: {str(e)}",
                    )
                ]

        # Sharing & Permissions
        elif name == "onedrive_list_shared_items":
            try:
                result = onedrive_list_shared_items()
                return [
                    types.TextContent(
                        type="text",
                        text=json.dumps(result, indent=2),
                    )
                ]
            except Exception as e:
                logger.exception(f"Error listing shared items: {e}")
                return [
                    types.TextContent(
                        type="text",
                        text=f"Error: {str(e)}",
                    )
                ]

        elif name == "onedrive_create_share_link":
            try:
                result = onedrive_create_share_link(
                    item_id=arguments["item_id"],
                    link_type=arguments.get("link_type", "view"),
                    scope=arguments.get("scope", "anonymous")
                )
                return [
                    types.TextContent(
                        type="text",
                        text=json.dumps(result, indent=2),
                    )
                ]
            except Exception as e:
                logger.exception(f"Error creating share link: {e}")
                return [
                    types.TextContent(
                        type="text",
                        text=f"Error: {str(e)}",
                    )
                ]

        else:
            return [
                types.TextContent(
                    type="text",
                    text=f"Unknown OneDrive tool: {name}",
                )
            ]



#---------------------------------------------------------------------------------------------

    # Set up SSE transport
    sse = SseServerTransport("/messages/")

    async def handle_sse(request):
        logger.info("Handling SSE connection")

        # Extract auth token from headers (allow None - will be handled at tool level)
        auth_token = request.headers.get('x-auth-token')

        # Set the auth token in context for this request (can be None)
        token = auth_token_context.set(auth_token or "")
        try:
            async with sse.connect_sse(
                    request.scope, request.receive, request._send
            ) as streams:
                await app.run(
                    streams[0], streams[1], app.create_initialization_options()
                )
        finally:
            auth_token_context.reset(token)

        return Response()

    # Set up StreamableHTTP transport
    session_manager = StreamableHTTPSessionManager(
        app=app,
        event_store=None,  # Stateless mode - can be changed to use an event store
        json_response=json_response,
        stateless=True,
    )

    async def handle_streamable_http(
            scope: Scope, receive: Receive, send: Send
    ) -> None:
        logger.info("Handling StreamableHTTP request")

        # Extract auth token from headers (allow None - will be handled at tool level)
        headers = dict(scope.get("headers", []))
        auth_token = headers.get(b'x-auth-token')
        if auth_token:
            auth_token = auth_token.decode('utf-8')

        # Set the auth token in context for this request (can be None/empty)
        token = auth_token_context.set(auth_token or "")
        try:
            await session_manager.handle_request(scope, receive, send)
        finally:
            auth_token_context.reset(token)

    @contextlib.asynccontextmanager
    async def lifespan(app: Starlette) -> AsyncIterator[None]:
        """Context manager for session manager."""
        async with session_manager.run():
            logger.info("Application started with dual transports!")
            try:
                yield
            finally:
                logger.info("Application shutting down...")

    # Create an ASGI application with routes for both transports
    starlette_app = Starlette(
        debug=True,
        routes=[
            # SSE routes
            Route("/sse", endpoint=handle_sse, methods=["GET"]),
            Mount("/messages/", app=sse.handle_post_message),

            # StreamableHTTP route
            Mount("/mcp", app=handle_streamable_http),
        ],
        lifespan=lifespan,
    )

    logger.info(f"Server starting on port {port} with dual transports:")
    logger.info(f"  - SSE endpoint: http://localhost:{port}/sse")
    logger.info(f"  - StreamableHTTP endpoint: http://localhost:{port}/mcp")

    import uvicorn

    uvicorn.run(starlette_app, host="0.0.0.0", port=port)

    return 0


if __name__ == "__main__":
    main()