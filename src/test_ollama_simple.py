import ollama

response = ollama.chat(
    model="qwen3:4b",
    messages=[
        {
    "role": "user",
    "content": "Do not explain or reason. Output exactly: OK"
}
    ],
    think=True,
    options={"num_predict": 300},
)

print("Finish:", response.done_reason)
print("Content:", repr(response.message.content))