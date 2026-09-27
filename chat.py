import sys
import httpx
import json
from dotenv import load_dotenv
import os
load_dotenv()
KEY = os.getenv("GEMINI_API_KEY")
URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent"
HEADERS = {
    "Content-Type": "application/json",
    "x-goog-api-key": KEY
}

def extract_text_from_response(response_json):
    try:
        return (response_json['candidates'][0]['content']['parts'][0]['text'])
    except (KeyError, IndexError):
        return ("No valid answer found in the response.")

def call_api(body):
    try:
        response = httpx.post(URL, headers=HEADERS, json=body, timeout=60)

        return response       



    except httpx.ConnectError:
        print("Please check if you are connected to the internet....")
        # print(httpx.ConnectError.__mro__)
    except httpx.NetworkError as e:
        print(f"An error occurred in the network, while making this request: {type(e).__name__}")
    except httpx.TimeoutException as e:
        print(f"The request timed out: {type(e).__name__}")
    except httpx.TransportError as e:
        print(f"A transport error occurred while making the request: {type(e).__name__}")
    except httpx.RequestError as e:
        print(f"Please recheck the request body of the API call, it seems to be malformed: {type(e).__name__}")
    except httpx.HTTPError as e:
        print(f"An HTTP error occurred: {type(e).__name__}")
    except Exception as e:
        print(f"An error occurred: {type(e).__name__}")      



def build_request_body(query, thinking_Level="LOW"):
    return {
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
                    "thinkingLevel" : thinking_Level
                }
            }
    }

def main():
    flagEmpty = True
    while flagEmpty:
        query = input("Enter your prompt: ")
    # query = ""

        if query.strip()=="":
            print("Please enter a prompt to continue....")
        else:
            flagEmpty = False
    thinking_Level = input("Enter the thinking level (MINIMAL, LOW, MEDIUM, HIGH): ").strip().upper()
    if thinking_Level not in ["MINIMAL", "LOW", "MEDIUM", "HIGH"]:
        print("Invalid thinking level. Defaulting to LOW.")
        thinking_Level = "LOW"
    body = build_request_body(query, thinking_Level)

    response = call_api(body)

    if response is None:
        print("No response received from the API.")
        sys.exit()


    try:
        responseInJSON = response.json()
    except json.JSONDecodeError:
        print("Failed to decode JSON response. Response content: ", response)
    
    print("This is the status code: ", response.status_code)
    responseErrorMessage = responseInJSON.get('error', {}).get('message', 'No error message provided')

    if response.status_code != 200:
        if response.status_code == 400:
            print(responseErrorMessage)
        elif response.status_code == 401:
            print("Unauthorized. Please check your API key.")
        elif response.status_code == 403:
            print("Forbidden. Please check your API key and permissions.")
        elif response.status_code == 404:
            print(responseErrorMessage)
        elif str(response.status_code).startswith('5'):
            print("Server error. Please try again later.")
        print("Response content: ", responseInJSON)
    else:
        try:
            finishReason = responseInJSON['candidates'][0]['finishReason']
        except (KeyError, IndexError):
            finishReason = None
    
        if finishReason != "STOP":
            print("The request failed with an error. Please check the response for details.")
            print("Response content: ", responseInJSON)
            sys.exit()

        text = extract_text_from_response(responseInJSON)
        print("This is the response: ", text)

   

if __name__ == "__main__":
    main()