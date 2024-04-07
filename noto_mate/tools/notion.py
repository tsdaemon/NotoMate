import os

from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.tools import tool
from notion_client import Client

notion_client = Client(auth=os.environ["NOTION_API_KEY"])


class SearchMyNotionInput(BaseModel):
    """Input for the Notion search tool."""

    query: str = Field(description="Search query to look up")
    sort_last_editing_time: bool = Field(description="Show the most recently edited documents first.", default=True)
    start_cursor: str | None = Field(
        description="A cursor value returned in a previous response that If supplied, limits the response to results "
        "starting after the cursor. If not supplied, then the first page of results is returned. "
    )
    page_size: int = Field(description="The number of documents to return", max=100, default=10)


@tool(args_schema=SearchMyNotionInput)
def search_my_notion(
    query: str, sort_last_editing_time: bool = True, page_size: int = 10, start_cursor: str | None = None
) -> dict:
    """Search over documents in Notion workspace.
    If the user is asking to search something in his notes, you can use this tool.
    If an error occurs, show to user all debug information.
    """
    return notion_client.search(
        query=query,
        sort={
            "direction": "descending" if sort_last_editing_time else "ascending",
            "timestamp": "last_edited_time",
        },
        start_cursor=start_cursor,
        page_size=page_size,
    )  # type: ignore


class GetNotionPageContentInput(BaseModel):
    """Notion page id input."""

    page_id: str = Field(description="Page id to get content from.")
    start_cursor: str | None = Field(
        description="If supplied, this endpoint will return a page of results starting after the cursor provided. "
        "If not supplied, this endpoint will return the first page of results."
    )


@tool(args_schema=GetNotionPageContentInput)
def get_notion_page_content(page_id: str, start_cursor: str | None = None) -> dict:
    """Get a page content in Notion workspace.
    If the user is asking to get some content from his notes, you can use this tool.
    If an error occurs, show to user all debug information."""
    return notion_client.blocks.children.list(page_id, start_cursor=start_cursor, page_size=10)  # type: ignore


# Create tools
tools = [search_my_notion, get_notion_page_content]
