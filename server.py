from flask import Flask, request, jsonify
from main import generate_email
import uuid

app = Flask(__name__)

# In-memory agent registry
registered_agents = {}

# Health check
@app.route('/', methods=['GET'])
def home():
    return "✅ Email Drafting Agent is running"

# Email generation endpoint
@app.route('/generate-email', methods=['POST'])
def email_api():
    input_data = request.json
    try:
        email = generate_email(input_data)
        return jsonify(email)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# AgentOS - Register agent
@app.route('/api/agents/register', methods=['POST'])
def register_agent():
    data = request.json
    agent_id = data.get("id", str(uuid.uuid4()))
    agent_name = data.get("name")
    agent_description = data.get("description")
    
    if not agent_name or not agent_description:
        return jsonify({"error": "Missing 'name' or 'description'"}), 400

    agent_info = {
        "agent_id": agent_id,
        "agent_name": agent_name,
        "agent_description": agent_description,
        "input_parameters": {}
    }
    registered_agents[agent_id] = agent_info
    return jsonify(agent_info), 200

# AgentOS - Lookup agent
@app.route('/api/agents/<agent_id>', methods=['GET'])
def lookup_agent(agent_id):
    agent = registered_agents.get(agent_id)
    if not agent:
        return jsonify({"error": "Agent not found"}), 404
    return jsonify(agent), 200

# AgentOS - Delete agent
@app.route('/api/agents/<agent_id>', methods=['DELETE'])
def delete_agent(agent_id):
    if agent_id in registered_agents:
        del registered_agents[agent_id]
        return '', 204
    return jsonify({"error": "Agent not found"}), 404

if __name__ == '__main__':
    app.run(port=5000)
