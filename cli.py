import json
from main import generate_email

if __name__ == "__main__":
    with open("test_input.json", "r") as f:
        input_data = json.load(f)

    email = generate_email(input_data)
    print("📬 Subject:", email["subject"])
    print("📄 Body:\n", email["body"])
