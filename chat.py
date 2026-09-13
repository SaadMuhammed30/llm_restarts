import httpx
from dotenv import load_dotenv
import os
load_dotenv()
key = os.getenv("GEMINI_API_KEY")

# query = input("Enter your prompt: ")
query = "The total number of cyclic isomers possible for a hydrocarbon with the molecular formula C4H6 is"

URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent"

HEADERS = {
    "Content-Type": "application/json",
    "x-goog-api-key": key
}

BODY = {
    "contents": [
        {
            "role": "user",
            "parts": [
                {
                    "text": query
                }
            ],
        }
    ],
    "generationConfig": 
        {
            "thinkingConfig": {
                "includeThoughts": True,
                # "thinkingLevel" : "MINIMAL"Available options: MINIMAL, LOW,  MEDIUM, HIGH
                "thinkingLevel" : "MINIMAL"
            }
        }
}

response = httpx.post(URL, headers=HEADERS, json=BODY, timeout=60)


print("This is the status code: ", response.status_code)
print("This is the response: ", response.json())

print("The answer to the query is\n", response.json()['candidates'][0]['content']['parts'][0]['text'])