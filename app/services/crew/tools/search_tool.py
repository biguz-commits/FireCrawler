from crewai.tools import BaseTool
from pydantic import BaseModel, Field
import json

from app.services.brave.BraveAPI import BraveAPI

params = {
    'country': "us",
    'search_lang': "en",
    'ui_lang': "en-US",
    'count': 20,
    'offset': 0,
    'safesearch': "strict",
    'freshness': "py",
    'text_decorations': False,
    'spellcheck': True,
    'result_filter': "web"
}

brave = BraveAPI()

class BraveSearchInput(BaseModel):
    """Input Schema for Brave Search Service"""
    query: str = Field(..., description="Brave search query")

class BraveSearchTool(BaseTool):
    name : str = "brave_search_tool"
    description: str = (
        "Search the internet using the Brave Search API based on a user query. "
        "Returns a list of search results as JSON objects containing: "
        "title, url, snippet (page summary), source domain, and page_age (ISO timestamp)."
    )
    args_schema = BraveSearchInput

    def _run(self, query: str):
        params["q"] = query
        try:
          raw = brave.search(params, summary=False)
          return brave.clean_for_llm(raw, top_k=6)
        except Exception as e:
            return json.dumps({"ok": False, "error": f"{type(e).__name__}: {e}"})



