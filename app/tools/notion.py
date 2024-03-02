from langchain_core.callbacks import (
    CallbackManagerForToolRun,
)
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.tools import BaseTool
from notion_client import Client


class NotionSearchInput(BaseModel):
    """Input for the Notion search tool."""

    query: str = Field(description="search query to look up")
    sort_last_editing_time: bool = Field(description="Show the most recently edited documents first.", default=True)
    start_cursor: str | None = Field(
        description="A cursor value returned in a previous response that If supplied, limits the response to results "
        "starting after the cursor. If not supplied, then the first page of results is returned. "
    )
    page_size: int = Field(description="The number of documents to return", max=100)


class NotionSearch(BaseTool):
    """Tool that queries the Notion Search API."""

    name: str = "search_notion_json"
    description: str = (
        "A search over documents in Notion workspace. "
        "If the user is asking to search something in his notes, you can use this tool. "
        "If an error occurs, show to user all debug information."
    )
    client: Client
    max_results: int = 5
    args_schema: type[BaseModel] = NotionSearchInput

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
