from ollama import generate

def llm(prompt: str):
    response = generate('deepseek-r1:1.5b', prompt, stream=False)
    print(response['response'])

