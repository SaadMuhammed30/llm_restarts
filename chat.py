import httpx
from dotenv import load_dotenv
import os
load_dotenv()
key = os.getenv("GEMINI_API_KEY")

# query = input("Enter your prompt: ")
query = "Which power do you think is superior and not used to its fullest potential in fantasy, DC Green Lantern ring or Marvel's Phoenix Force"

URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent"
# URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-kbvepjobflash:generateContent"

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
                "thinkingLevel" : "HIGH"
            }
        }
}



try:
    response = httpx.post(URL, headers=HEADERS, json=BODY, timeout=60)
    print("This is the status code: ", response.status_code)

    if response.status_code != 200:
        if response.status_code == 400:
            print(response.json()['error']['message'])
        elif response.status_code == 401:
            print("Unauthorized. Please check your API key.")
        elif response.status_code == 403:
            print("Forbidden. Please check your API key and permissions.")
        elif response.status_code == 404:
            print(response.json()['error']['message'])
        elif str(response.status_code).startswith('5'):
            print("Server error. Please try again later.")
        print("Response content: ", response.json())
    else:
        print("This is the response: ", response.json())
        print("The answer to the query is\n", response.json()['candidates'][0]['content']['parts'][0]['text'])

except httpx.ConnectError:
    print("Please check if you are connected to the internet....")
    print(httpx.ConnectError.__mro__)
except httpx.NetworkError as e:
    print(f"An error occurred in the network, while making this request: {e}")
except httpx.TransportError as e:
    print(f"A transport error occurred while making the request: {e}")
except httpx.RequestError as e:
    print(f"Please recheck the request body of the API call, it seems to be malformed: {type(e).__name__}")
except httpx.HTTPError as e:
    print(f"An HTTP error occurred: {type(e).__name__}")
except Exception as e:
    print(f"An error occurred: {type(e).__name__s}")      


