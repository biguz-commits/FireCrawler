from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field
import json

class SimilarityResearchToolInput(BaseModel):
    query : str = Field(..., description="Query string to be used for similarity search")


class SimilarityResearchTool(BaseTool):
    name : str = "similarity_research_tool"
    description: str = (
        "Execute a semantic similarity search on a vector collection using the provided query texts. "
        "The tool computes embedding similarity and returns the most relevant stored documents, "
        "including their content, identifiers, and similarity scores."
    )

    args_schema: Type[BaseModel] = SimilarityResearchToolInput

    def _run(self, query: str):

        try:
          sims = self.collection.query(
              query_texts=[query],
              n_results=4
          )
          return sims
        except Exception as e:
            return json.dumps({"ok": False, "error": f"{type(e).__name__}: {e}"})

