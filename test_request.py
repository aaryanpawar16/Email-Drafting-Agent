import requests

url = "https://eb2a-2401-4900-7c87-3674-a8be-e614-69a-4c6b.ngrok-free.app/generate-email"

data = {
    "recipient": "Ms. Iyer",
    "purpose": "discuss the upcoming workshop",
    "key_points": [
        "Finalize agenda",
        "Confirm participants",
        "Reserve venue"
    ]
}

try:
    response = requests.post(url, json=data)
    print("Status Code:", response.status_code)
    
    if response.status_code == 200:
        email = response.json()
        print("\n📬 Subject:", email.get("subject", "No subject returned"))
        print("\n📄 Body:\n", email.get("body", "No body returned"))
    else:
        print("❌ Error Response:\n", response.text)

except requests.exceptions.RequestException as e:
    print("❌ Request failed:", e)
