import requests

url = "https://43cd-2401-4900-ac88-4a86-742b-381d-6875-e3b0.ngrok-free.app/generate-email"

data = {
    "recipient": "Ms. Iyer",
    "purpose": "discuss the upcoming workshop",
    "key_points": [
        "Finalize agenda",
        "Confirm participants",
        "Reserve venue"
    ]
}

response = requests.post(url, json=data)
print("Status Code:", response.status_code)
print("Response:", response.json())
