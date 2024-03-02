from chains.notion import agent_executor as notion_chain
from fastapi import FastAPI
from fastapi.responses import RedirectResponse, Response
from langserve import add_routes
from openai_functions_agent import agent_executor as openai_functions_agent_chain

app = FastAPI()


@app.get("/")
async def redirect_root_to_docs() -> Response:
    return RedirectResponse("/docs")


# Edit this to add the chain you want to add
add_routes(app, openai_functions_agent_chain, path="/search-agent")
add_routes(app, notion_chain, path="/notion-agent")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
