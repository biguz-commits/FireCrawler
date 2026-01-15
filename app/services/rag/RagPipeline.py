import re
import uuid
from typing import Dict, Optional

from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import chromadb


class RagPipeline:
    def __init__(
        self,
        pdf_path: str,
        db_path: str = "/Users/tommasobiganzoli/Desktop/firecrawl-agent/app/db_storage",
        collection_name: str = "firecrawl-agent",
    ):
        self.chunk_size = 500
        self.chunk_overlap = 150
        self.pdf_path = pdf_path

        self.db_path = db_path
        self.collection_name = collection_name

        self._client: Optional[chromadb.ClientAPI] = None
        self._collection = None

    @property
    def client(self):
        if self._client is None:
            self._client = chromadb.PersistentClient(path=self.db_path)
        return self._client

    @property
    def collection(self):
        if self._collection is None:
            self._collection = self.client.get_or_create_collection(
                name=self.collection_name
            )
        return self._collection

    def pdf_to_token_chunks(self) -> Dict[str, str]:
        reader = PdfReader(self.pdf_path)
        pages_text = []

        for page in reader.pages:
            text = page.extract_text() or ""
            pages_text.append(text)

        full_text = "\n".join(pages_text)

        full_text = full_text.replace("\r", "\n")
        full_text = re.sub(r"[ \t]+", " ", full_text)
        full_text = re.sub(r"\n{3,}", "\n\n", full_text)
        full_text = full_text.strip()

        if not full_text:
            return {}

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap
        )
        texts = text_splitter.split_text(full_text)

        return {
            str(uuid.uuid4()): chunk.strip()
            for chunk in texts
            if chunk.strip()
        }

    @classmethod
    def get_collection(
            cls,
            db_path: str = "/Users/tommasobiganzoli/Desktop/firecrawl-agent/app/db_storage",
            collection_name: str = "firecrawl-agent",
    ):
        client = chromadb.PersistentClient(path=db_path)
        return client.get_or_create_collection(name=collection_name)

    def db_store(self):
        chunks = self.pdf_to_token_chunks()
        if not chunks:
            return

        self.collection.upsert(
            ids=list(chunks.keys()),
            documents=list(chunks.values()),
        )


