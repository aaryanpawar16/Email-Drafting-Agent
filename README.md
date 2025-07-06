# 📧 Email Drafting Agent

An AI-powered agent that transforms bullet-point-style input into professional, polished email drafts.

---

## 💡 Features

- Accepts minimal input:
  - Recipient's name or role
  - Purpose of the email
  - Bullet points for details
- Generates:
  - Subject line
  - Greeting
  - Organized body
  - Polite closing

---

## ⚙️ Setup Instructions

```bash
git clone https://github.com/your-username/email-drafting-agent.git
cd email-drafting-agent
python -m venv venv
venv\Scripts\activate  # For Windows
pip install -r requirements.txt
python server.py
🔁 Test Locally
bash
Copy
Edit
python test_request.py
📨 Sample Input
json
Copy
Edit
{
  "recipient": "Ms. Iyer",
  "purpose": "discuss the upcoming workshop",
  "key_points": ["Finalize agenda", "Confirm participants", "Reserve venue"]
}
✅ Sample Output
json
Copy
Edit
{
  "subject": "Regarding Discuss the upcoming workshop",
  "body": "Dear Ms. Iyer,\n\nI hope you're doing well. I'm reaching out to discuss the upcoming workshop.\n\n- Finalize agenda\n- Confirm participants\n- Reserve venue\n\nPlease let me know if you have any questions.\n\nBest regards,\n[Your Name]"
}
🌐 Live Demo (Bonus)
👉 Try it live

📚 How It Works
Built using Python + Flask

Uses a prompt-like template inside main.py to generate emails

server.py handles API requests

test_request.py sends a sample POST request

📦 AgentOS Registration
This agent is registered and callable via GenAI AgentOS.

🧑‍💻 Author
Aaryan Pawar

python
Copy
Edit

---

✅ **Let me know if you'd like me to generate your `requirements.txt` or help write any missing file.**  
You're ready to publish and submit!








Ask ChatGPT
