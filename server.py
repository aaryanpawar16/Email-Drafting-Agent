from flask import Flask, request, jsonify
from main import generate_email

app = Flask(__name__)

# 👇 New route for the root URL
@app.route('/', methods=['GET'])
def home():
    return "✅ Email Drafting Agent is running"

@app.route('/generate-email', methods=['POST'])
def email_api():
    input_data = request.json
    try:
        email = generate_email(input_data)
        return jsonify(email)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(port=5000)
