from flask import Flask, render_template, jsonify, request, url_for
from flask_cors import CORS
import uuid
import os
import pandas as pd
from datetime import timedelta
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from sales_flow_agent import SalesFlowAgent, CSV_FILE
from google.genai import types

app = Flask(__name__)
CORS(app)
app.secret_key = 'your_secret_key'
app.permanent_session_lifetime = timedelta(days=7)

# In-memory map of lead_id → Runner
runners = {}

# Ensure leads.csv exists
CSV_COLUMNS = ['lead_id', 'name', 'age', 'country', 'interest', 'status']
if not os.path.exists(CSV_FILE):
    pd.DataFrame(columns=CSV_COLUMNS).to_csv(CSV_FILE, index=False)

# Shared ADK session service
session_svc = InMemorySessionService()

# A random ID we use client-side to know when to clear localStorage
server_session_id = str(uuid.uuid4())

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/form')
def form():
    return render_template('form.html')

@app.route('/submit-form', methods=['POST'])
def submit_form():
    data = request.json or {}
    name = data.get('name')
    if not name:
        return jsonify(status='error', message='Name is required'), 400

    lead_id = str(uuid.uuid4())
    # Seed the CSV row
    pd.DataFrame([{
        'lead_id': lead_id,
        'name': name,
        'age': '',
        'country': '',
        'interest': '',
        'status': 'pending'
    }]).to_csv(CSV_FILE, mode='a', header=False, index=False)

    # Return redirect URL plus the lead_id/name so the front‐end can open /chat?…
    redirect_url = url_for('chat_get', lead_id=lead_id, lead_name=name)
    return jsonify({
        'status': 'success',
        'redirect_url': redirect_url,
        'lead_id': lead_id,
        'lead_name': name
    })

@app.route('/chat', methods=['GET'])
def chat_get():
    # Render chat.html, passing lead_id & lead_name from query string
    lead_id   = request.args.get('lead_id')
    lead_name = request.args.get('lead_name')
    if not lead_id or not lead_name:
        return "Missing lead_id or lead_name", 400

    return render_template(
        'chat.html',
        lead_id=lead_id,
        lead_name=lead_name,
        server_session_id=server_session_id
    )

@app.route('/chat', methods=['POST'])
def chat_post():
    data     = request.json or {}
    lead_id  = data.get('lead_id')
    user_msg = (data.get('message') or '').strip()

    if not lead_id or not user_msg:
        return jsonify(message='Missing lead_id or message'), 400

    # Initialize runner & ADK session once per lead_id
    if lead_id not in runners:
        agent = SalesFlowAgent()
        runners[lead_id] = Runner(
            agent=agent,
            app_name="sales_app",
            session_service=session_svc
        )
        if not session_svc.get_session(app_name="sales_app",user_id=lead_id, session_id=lead_id):
            session_svc.create_session(
                app_name="sales_app",
                user_id=lead_id,
                session_id=lead_id,
                state={"name": data.get('lead_name', '')}
            )

    runner = runners[lead_id]
    content = types.Content(role='user', parts=[types.Part(text=user_msg)])
    events  = runner.run(
        user_id=lead_id,
        session_id=lead_id,
        new_message=content
    )

    # Grab the first assistant reply
    try:
        ev = next(events)
        reply = ev.content.parts[0].text
    except StopIteration:
        reply = "Sorry, no reply from agent."

    return jsonify(message=reply)

@app.route('/chat-message', methods=['POST'])
def chat_message():
    data      = request.json or {}
    lead_id   = data.get('lead_id')
    lead_name = data.get('lead_name')

    if not lead_id or not lead_name:
        return jsonify(error='Missing lead_id or lead_name'), 400

    # Initialize runner & ADK session once per lead_id
    if lead_id not in runners:
        agent = SalesFlowAgent()
        runners[lead_id] = Runner(
            agent=agent,
            app_name="sales_app",
            session_service=session_svc
        )
        if not session_svc.get_session(app_name="sales_app", user_id=lead_id,session_id= lead_id):
            session_svc.create_session(
                app_name="sales_app",
                user_id=lead_id,
                session_id=lead_id,
                state={"name": lead_name}
            )

    runner = runners[lead_id]
    content = types.Content(role='user', parts=[types.Part(text="__trigger__")])
    events  = runner.run(
        user_id=lead_id,
        session_id=lead_id,
        new_message=content
    )

    try:
        ev = next(events)
        reply = ev.content.parts[0].text
    except StopIteration:
        reply = "Oops, no response from agent."

    return jsonify(message=reply)

if __name__ == '__main__':
    app.run(debug=True)
