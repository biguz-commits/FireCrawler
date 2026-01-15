from crewai.tools import BaseTool
from pydantic import BaseModel, Field
import json
import bs4
import urllib.request
import ssl
import certifi


class HtmlToolInput(BaseModel):
    url : str = Field(..., description="The url as a string of the html page to be parsed")

class HtmlTool(BaseTool):
    name = "html_tool"
    description: str = (
        "Fetch an HTML page from a given URL and extract its main textual content. "
        "Parses the page, collects readable paragraph text (<p> tags) from the main section, "
        "and returns the cleaned text as a single string separated by blank lines."
    )
    args_schema = HtmlToolInput

    def _run(self, url: str):
        ctx = ssl.create_default_context(cafile=certifi.where())

        try:
          req = urllib.request.Request(
              url,
              headers={"User-Agent": "Mozilla/5.0"}
          )

          html = urllib.request.urlopen(req, context=ctx).read()
          soup = bs4.BeautifulSoup(html, "html.parser")

          main_tag = soup.find("main") or soup
          paragraphs = main_tag.find_all("p")

          texts = []
          for p in paragraphs:
              text = p.get_text(strip=True)
              if text:
                  texts.append(text)

          return "\n\n".join(texts) if texts else []

        except Exception as e:
            return json.dumps({"ok": False, "error": f"{type(e).__name__}: {e}"})

