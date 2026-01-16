from app.services.rag.RagPipeline import RagPipeline


class FileProcessController:

    def __init__(self,
                 pdf_path: str):
        self.pdf_path = pdf_path

    def process(self):
        pipeline = RagPipeline(self.pdf_path)
        pipeline.db_store()

