from langchain_core.callbacks import (
    CallbackManagerForToolRun,
)
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.tools import BaseTool
from notion_client import Client


class SearchMyNotionInput(BaseModel):
    """Input for the Notion search tool."""

    query: str = Field(description="search query to look up")
    sort_last_editing_time: bool = Field(description="Show the most recently edited documents first.", default=True)
    start_cursor: str | None = Field(
        description="A cursor value returned in a previous response that If supplied, limits the response to results "
        "starting after the cursor. If not supplied, then the first page of results is returned. "
    )
    page_size: int = Field(description="The number of documents to return", max=100)


class SearchMyNotion(BaseTool):
    """Tool that queries the Notion Search API."""

    name: str = "search_my_notion"
    description: str = (
        "A search over documents in Notion workspace. "
        "If the user is asking to search something in his notes, you can use this tool. "
        "If an error occurs, show to user all debug information."
    )
    client: Client
    max_results: int = 5
    args_schema: type[BaseModel] = SearchMyNotionInput

    def _run(
        self,
        query: str,
        sort_last_editing_time: bool = True,
        start_cursor: str | None = None,
        page_size: int = 10,
        run_manager: CallbackManagerForToolRun | None = None,
    ) -> dict | str:
        """Use the tool."""
        try:
            return self.client.search(
                query=query,
                sort={
                    "direction": "descending" if sort_last_editing_time else "ascending",
                    "timestamp": "last_edited_time",
                },
                start_cursor=start_cursor,
                page_size=page_size,
            )  # type: ignore
        except Exception as e:
            return repr(e)


class GetNotionPageContentInput(BaseModel):
    """Notion page id input."""

    page_id: str = Field(description="Page id to get content from.")
    start_cursor: str | None = Field(
        description="If supplied, this endpoint will return a page of results starting after the cursor provided. "
        "If not supplied, this endpoint will return the first page of results."
    )


class GetNotionPageContent(BaseTool):
    """Tool that gets the page content from Notion API."""

    name: str = "get_notion_page_content"
    description: str = (
        "A method to get a page content in Notion workspace. "
        "If the user is asking to get some content from his notes, you can use this tool. "
        "If an error occurs, show to user all debug information."
    )
    client: Client
    max_results: int = 5
    args_schema: type[BaseModel] = GetNotionPageContentInput

    def _run(
        self,
        page_id: str,
        start_cursor: str | None = None,
        page_size: int = 10,
        run_manager: CallbackManagerForToolRun | None = None,
    ) -> dict | str:
        """Use the tool."""
        try:
            return self.client.blocks.children.list(page_id, start_cursor=start_cursor, page_size=10)  # type: ignore
        except Exception as e:
            return repr(e)
