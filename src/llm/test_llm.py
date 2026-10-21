from .ollama_client import OllamaClient


def main():
    llm = OllamaClient()

    response = llm.generate(
        "Reply in one short sentence: "
        "Why is risk management important in crypto trading?"
    )

    print("LLM Response")
    print("------------")
    print("Content:", response.content)
    print("Provider:", response.provider)
    print("Model:", response.model)
    print("Finish reason:", response.finish_reason)


if __name__ == "__main__":
    main()