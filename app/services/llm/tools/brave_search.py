from app.services.llm.tools.BraveAPI import BraveAPI
from dotenv import load_dotenv
import json

load_dotenv()

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

async def brave_search(query: str, top_k: int = 10):
    """
    :param query: A string for the user query.
    :return: Raw Brave output, or cleaned (LLM-ready) payload.
    """
    params["q"] = query
    raw = brave.search(params, summary=False)
    return brave.clean_for_llm(raw, top_k=top_k)


if __name__ == "__main__":
    import asyncio

    q = "Who is the USA President ?"
    data = asyncio.run(brave_search(q,top_k=10))
    print(json.dumps(data, indent=2, ensure_ascii=False))
