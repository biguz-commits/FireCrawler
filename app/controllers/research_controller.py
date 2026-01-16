from app.services.crew.crew import ResearchCrew


class ResearchController:

    @staticmethod
    def run(query: str):

        inputs = {
            "query": query,
        }
        try:
            output = ResearchCrew().crew().kickoff(inputs)
            return output.raw
        except Exception as e:
            raise Exception(f"An error occurred while running the crew: {e}")

if __name__ == "__main__":
    ResearchController().run("Who is Larry Page ?")