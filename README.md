📬 Email Drafting Agent

Transform bullet points into polished, professional emails with AI.

Built for the [GenAI AgentOS Mini Challenge 2](https://github.com/genai-works-org/genai-agentos).

---
##Check out Demo
[Email Drafting Agent](https://youtu.be/ibMepP7qhuc?si=4lApIcQQ_lIfWT4Z)
## 💡 What It Does

This agent takes minimal bullet-point input such as:

- Recipient's name or role  
- Purpose of the email  
- Key points to include  

And returns a complete email with:

- ✅ A subject line  
- ✅ A respectful greeting  
- ✅ A well-structured body  
- ✅ A professional closing  

---

## ⚙️ How It Works

The agent uses Jinja templating + prompt engineering to translate structured JSON input into human-like, fluent email content.

### Input Example

{
  "recipient": "Mr. Sharma",
  "purpose": "Request a meeting regarding the Q3 project plan",
  "points": [
    "Discuss project timeline",
    "Align on deliverables",
    "Confirm resource allocation"
  ]
}

Output

📬 Subject: Request a meeting regarding the Q3 project plan

Dear Mr. Sharma,

I hope you're doing well. I'm reaching out to request a meeting regarding the Q3 project plan.

- Discuss project timeline  
- Align on deliverables  
- Confirm resource allocation

Please let me know if you have any questions.

Best regards,  
[YOUR NAME]

🧩 Project Structure
bash
Copy
Edit
email-drafting-agent/
├── genai-agentos/
│   └── cli/
│       ├── src/               # Shared utils, settings, http client
│       ├── http.py
│       ├── cli.py             # Agent registration / management CLI
├── main.py                    # Agent logic
├── server.py                  # Runs the agent server
├── agent.yaml                 # AgentOS config
├── test_input.json            # Sample input
├── README.md                  # You're here!

🚀 How to Run Locally
bash
Copy
Edit
# (1) Clone the repo
git clone https://github.com/your-username/email-drafting-agent.git
cd email-drafting-agent

# (2) Create virtual environment
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate # macOS/Linux

# (3) Install dependencies
pip install -r requirements.txt

# (4) Register agent (optional)
set PYTHONPATH=../..
python genai-agentos/cli/cli.py register_agent --name "email-drafting-agent" --description "Professional email generation from bullet points"

# (5) Run server
python server.py

🌐 (Optional) Live Deployment
Bonus points!

This agent is live at:
https://YOUR-NGROK-URL.ngrok-free.app

You can POST a request like this:
curl -X POST https://YOUR-NGROK-URL.ngrok-free.app/run \
  -H "Content-Type: application/json" \
  -d @test_input.json

📦 Tech Stack
Python 3.10

GenAI AgentOS

typer, httpx, pydantic, jinja2

🙌 Credits
Built by Aaryan Pawar
For GenAI Mini Challenge 2

