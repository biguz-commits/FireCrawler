from dotenv import load_dotenv
import os
import time
import urllib.request
import urllib.parse
import json
import gzip
from io import BytesIO

import ssl
import certifi


load_dotenv()


class BraveAPI:
    def __init__(self):
        self.version = "v1"
        self.poll_sleep_time = 0.05
        self.base = "https://api.search.brave.com/res"

        self.ssl_context = ssl.create_default_context(cafile=certifi.where())

        self.headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip, deflate, br",
            "X-Subscription-Token": os.getenv("BRAVE_API_KEY"),
            "User-Agent": "Mozilla/5.0",
        }

    def _get_response(self, request: urllib.request.Request):
        with urllib.request.urlopen(request, context=self.ssl_context) as response:
            raw = response.read()

            if response.info().get("Content-Encoding") == "gzip":
                buf = BytesIO(raw)
                with gzip.GzipFile(fileobj=buf) as gzip_file:
                    return json.loads(gzip_file.read().decode("utf-8"))

            return json.loads(raw.decode("utf-8"))

    def search(self, params: dict, summary: bool = True):
        path = "/web/search"
        query_string = urllib.parse.urlencode(params)
        endpoint = f"{self.base}/{self.version}{path}?{query_string}"

        request = urllib.request.Request(endpoint, headers=self.headers)
        response = self._get_response(request)

        if not summary:
            return response
        else:
            return self._summary(params, response)

    def _summary(self, params: dict, response: dict):
        params["summary"] = True

        if "summarizer" not in response:
            raise ValueError("No summarizer key found")

        path = "/summarizer/search"
        query = urllib.parse.urlencode(
            {"key": response["summarizer"]["key"], "entity_info": 1}
        )
        endpoint = f"{self.base}/{self.version}{path}?{query}"

        request = urllib.request.Request(endpoint, headers=self.headers)
        results = self._get_response(request)

        while not results:
            time.sleep(self.poll_sleep_time)
            results = self._get_response(request)

        return results

    @staticmethod
    def clean_for_llm(brave_response: dict, top_k: int = 6) -> dict:
        """
        Minimal cleaner: keeps only what an LLM needs.
        Preserves SERP order using mixed.main -> web.results[index] when available.
        """
        query = brave_response.get("query", {}) or {}
        web = brave_response.get("web", {}) or {}
        web_results = web.get("results", []) or []

        mixed = brave_response.get("mixed", {}) or {}
        main = mixed.get("main", []) or []
        indices = [
            item.get("index")
            for item in main
            if isinstance(item, dict) and item.get("type") == "web"
        ]

        if not indices:
            indices = list(range(len(web_results)))

        out_results = []
        for idx in indices:
            if not isinstance(idx, int) or idx < 0 or idx >= len(web_results):
                continue
            r = web_results[idx] or {}
            out_results.append(
                {
                    "title": r.get("title", ""),
                    "url": r.get("url", ""),
                    "snippet": (r.get("description", "") or "")
                    .replace("&quot;", '"')
                    .replace("&#x27;", "'")
                    .strip(),
                    "source": (
                        (r.get("profile", {}) or {}).get("long_name")
                        or (r.get("profile", {}) or {}).get("name")
                        or ""
                    ),
                    "page_age": r.get("page_age", ""),
                }
            )
            if len(out_results) >= top_k:
                break

        return {
            "query": {
                "original": query.get("original", ""),
                "altered": query.get("altered", ""),
                "country": query.get("country", ""),
            },
            "results": out_results,
        }
