from crewai import LLM

def get_client():

    ollama_llm = LLM(
        model="ollama/llama3.1:latest",
        base_url="http://localhost:11434"
    )

    return ollama_llm


if __name__ == '__main__':
    llm = get_client()
    response = llm.call("Rispondi solo con la parola: OK")
    print(response)
