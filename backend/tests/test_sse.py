import requests
import json
import sys

def test_sse():
    url = "http://localhost:8000/api/chat"
    payload = {
        "message": "What is the weather in Mumbai?",
        "session_id": "test_session_sse_tool"
    }
    headers = {
        "Content-Type": "application/json"
    }

    print(f"Connecting to {url}...")
    try:
        with requests.post(url, json=payload, headers=headers, stream=True) as response:
            if response.status_code != 200:
                print(f"Error: {response.status_code}")
                print(response.text)
                return

            print("Connected! Listening for events...")
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    print(f"RECEIVED: {decoded_line}")
                    
                    if decoded_line.startswith("event: done"):
                        print("Done event received.")
                        break
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    test_sse()
