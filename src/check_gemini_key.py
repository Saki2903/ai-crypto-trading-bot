
from dotenv import dotenv_values

key = dotenv_values(".env").get("GEMINI_API_KEY", "")

print("Key found:", bool(key))
print("Key configured:", bool(key))
print("Length:", len(key))
print("Leading/trailing whitespace:", key != key.strip())
print("Contains quotes:", '"' in key or "'" in key)
