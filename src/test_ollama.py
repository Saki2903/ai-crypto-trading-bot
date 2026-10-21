import ollama

print("Testing Qwen3 - no thinking...")

response = ollama.chat(
    model="qwen3:4b",
    messages=[
        {
            "role": "user",
            "content": "Say only: Hello"
        }
    ],
    options={
        "temperature": 0,
        "num_predict": 300,
    },
)

print("\nRaw response:")
print(response)

print("\nAI response:")
print(repr(response.message.content))

print("\nGeneration status:", response.done_reason)