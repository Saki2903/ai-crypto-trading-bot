
import os
from dotenv import load_dotenv
from google import genai

# Load API key from the project root .env file
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY পাওয়া যায়নি। "
        "Project root-এর .env ফাইল পরীক্ষা করো।"
    )

client = genai.Client(api_key=api_key)

print("Connecting to Gemini API...")

try:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=(
            "Reply in Bengali in one short sentence: "
            "Why is risk management important in crypto trading?"
        ),
        config={
            "max_output_tokens": 100,
            "temperature": 0,
        },
    )

    print("\nGemini response:")
    print(response.text or "কোনো text response পাওয়া যায়নি।")

except Exception as error:
    print("\nGemini API test failed.")
    print("Error type:", type(error).__name__)
    print("Details:", str(error))
