# AI Sales Assistant

A conversational sales agent built with Google’s Agent Development Kit (ADK) and Flask.  
Handles multiple leads concurrently, walks each lead through a structured information-gathering flow (age, country, interest), persists data to `leads.csv`, and automatically follows up with unresponsive leads.

---

## 🚀 Features

- **Structured Conversation Flow**  
  Sequentially asks for age, country, and interest, and only marks a lead **secured** once all data is collected.  
- **Concurrent Lead Handling**  
  Each lead has its own ADK session and Runner keyed by `lead_id`, allowing parallel chats without interference.  
- **Automated Follow-Ups**  
  If a lead doesn’t reply within 60 s, the agent sends a “Just checking in…” message.  
- **Persistent Storage**  
  All lead data and statuses are stored in `leads.csv` for easy review and export.  

---

## 🎯 Prerequisites

- Python 3.10+  
- pip  
- Google ADK credentials (set via `GOOGLE_API_KEY`)  

---

## 🔧 Setup & Installation

1. **Clone the repository**  
   ```bash
   git clone https://github.com/your-username/ai-sales-assistant.git
   cd ai-sales-assistant

2. **Create & activate a virtual environment**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate


3. **Install dependencies**
    ```bash
    pip install -r requirements.txt

4. **Running the App**
    ```bash
    python app.py

By default, Flask runs at http://127.0.0.1:5000.

## Usage Guide

1. **Submit a Lead**
Visit http://127.0.0.1:5000/form, enter a name, and submit.

2. **Chat Interface**
You’ll be redirected to Messaging app. The agent greets the lead and asks permission.

3. **Answer Questions**

Reply Yes → Agent asks age → then country → then interest.

Reply No → Agent ends the conversation and marks status as no_response.

4. **Follow-Up**
If you don’t reply within 60 s at any step, the agent automatically follows up.

5. **Check CSV Output**
Open leads.csv to see each row updated with age, country, interest, and final status (pending, secured, or no_response).

## Project Structure

.
├── app.py                 # Flask server & ADK integration

├── sales_agent.py         # Custom ADK Agent implementation

├── requirements.txt       # Python dependencies

├── leads.csv              # Stores all lead data

├── templates/
│   ├── base.html

│   ├── form.html          # Lead submission form

│   └── chat.html          # Chat UI

└── static/                # (optional) CSS/JS assets

##  Design Decisions

**Explicit lead_id Passing**
Front-end sends lead_id on every request, avoiding shared Flask session cookies and mixing between tabs.

**In-Memory Runner Map**
A global runners: Dict[lead_id, Runner] holds each lead’s ADK Runner and session context.

**CSV for Persistence**
Chosen for simplicity and human readability—no external database required.

**Background Follow-Up Thread**
A single daemon thread scans inactivity and enqueues follow-ups, ensuring timely reminders.

## License
This project is MIT-licensed. Feel free to use or modify.