import sys
import httpx
import json
from dotenv import load_dotenv
import os
load_dotenv()
KEY = os.getenv("GROQ_API_KEY")

MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

URL = "https://api.groq.com/openai/v1/chat/completions"
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {KEY}"
}

def extract_text_from_response(response_json):
    try:
        with open("grok_responses_without_thinking.json", "a", encoding="utf-8") as f:
            json.dump(response_json, f, indent=4, ensure_ascii=False)
            f.write("\n")
    except OSError as e:
        print(f"Could not write the response to the log file: {type(e).__name__}")

    try:
        return (response_json['choices'][0]['message']['content'])
    except (KeyError, IndexError):
        return ("No valid answer found in the response.")

def extract_reasoning_from_response(response_json):
    try:
        return response_json['choices'][0]['message'].get('reasoning')
    except (KeyError, IndexError):
        return None

def call_api(body):
    try:
        response = httpx.post(URL, headers=HEADERS, json=body, timeout=60)

        return response

    except httpx.ConnectError:
        print("Please check if you are connected to the internet....")
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


def build_request_body(messages, reasoning_Effort="LOW", show_thinking=False):
    body = {
        "model": MODEL,
        "messages": messages
    }
    if reasoning_Effort:
        body["reasoning_effort"] = reasoning_Effort.lower()
    if show_thinking:
        # "parsed" puts the chain-of-thought in message.reasoning instead of
        # inlining it in the content. "hidden" drops it entirely.
        body["reasoning_format"] = "parsed"
    return body

def main():
    if not KEY:
        print("XAI_API_KEY is not set. Please add it to your .env file.")
        return

    messages = []
    flagEmpty = True
    reasoning_Effort = input("Enter the reasoning effort (LOW, HIGH, or leave empty for the model default): ").strip().upper()
    if reasoning_Effort not in ["LOW", "HIGH", ""]:
        print("Invalid reasoning effort. Defaulting to LOW.")
        reasoning_Effort = "LOW"

    show_thinking = input("Show the model's thinking? (y/N): ").strip().lower() in ("y", "yes")

    while flagEmpty:
        query = input("Enter your prompt: ")

        if query.strip() == "":
            print("Please enter a prompt to continue....")
            continue

        if query.lower() in ("exit", "quit"):
            print("Exiting the program.")
            break

        input1 = {"role": "user", "content": query}
        body = build_request_body(messages + [input1], reasoning_Effort, show_thinking)
        response = call_api(body)
        if response is None:
            print("No response received from the API.")
            continue
        try:
            responseInJSON = response.json()
        except json.JSONDecodeError:
            print("Failed to decode JSON response. Response content: ", response)
            continue
        responseErrorMessage = responseInJSON.get('error', 'No error message provided')
        if isinstance(responseErrorMessage, dict):
            responseErrorMessage = responseErrorMessage.get('message', 'No error message provided')
        if response.status_code != 200:
            if response.status_code == 400:
                print(responseErrorMessage)
            elif response.status_code == 401:
                print("Unauthorized. Please check your API key.")
            elif response.status_code == 403:
                print("Forbidden. Please check your API key and permissions.")
            elif response.status_code == 404:
                print(responseErrorMessage)
            elif response.status_code == 429:
                print("Rate limited. Please slow down and try again later.")
            elif str(response.status_code).startswith('5'):
                print("Server error. Please try again later.")
            print("Response content: ", responseInJSON)
            continue
        else:
            try:
                finishReason = responseInJSON['choices'][0]['finish_reason']
            except (KeyError, IndexError):
                finishReason = None

            if finishReason != "stop":
                print("The request failed with an error. Please check the response for details.")
                print("Response content: ", responseInJSON)
                continue

            if show_thinking:
                reasoning = extract_reasoning_from_response(responseInJSON)
                if reasoning:
                    print("\n--- Thinking ---")
                    print(reasoning)
                    print("--- End of thinking ---\n")
                else:
                    print("(No reasoning was returned for this response.)")

            text = extract_text_from_response(responseInJSON)
            print("This is the response: ", text)
        messages.append(input1)
        output = {"role": "assistant", "content": text}
        messages.append(output)


if __name__ == "__main__":
    main()
