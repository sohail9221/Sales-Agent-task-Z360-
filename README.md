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
   git clone https://github.com/sohail9221/Sales-Agent-task-Z360-.git
   cd Sales-Agent-task-Z360-

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

## 📝 Usage Guide

1. **Submit a Lead**
Visit http://127.0.0.1:5000/form, enter a name, and submit.

2. **Chat Interface**
You’ll be redirected to Messaging app. The agent greets the lead and asks permission.

3. **Answer Questions**

Reply Yes → Agent asks age → then country → then interest.

Reply No → Agent ends the conversation and marks status as no_response.

4. **Follow-Up**
If you don’t reply within 24 hours at any step, the agent automatically follows up.

5. **Check CSV Output**
Open leads.csv to see each row updated with age, country, interest, and final status (pending, secured, or no_response).


## 🔄 Simulation
A simple Python script (simulate_lead.py) is provided to automate form-submission, chat interactions, and follow-up pauses. to test Run: 
    ```bash 
    python simulate_lead.py 

## ✅ Test Cases
Basic test scenarios cover full flow, immediate decline, and follow-up behavior. See testing_agent.py for automated pass/fail reports.
Run the file with pytest :
    ```bash
    pytest testing_cases.py

## 📁 Project Structure
```
        .
        ├── app.py                 # Flask server & ADK integration
        ├── sales_agent.py         # Custom ADK Agent implementation
        ├── requirements.txt       # Python dependencies
        ├── leads.csv              # Stores all lead data
        ├── simulate_lead.py       # Script to simulate leads & follow-up delays
        ├── test_agent.py          # Automated test suite with PASS/FAIL output
        ├── templates/
        │   ├── base.html
        │   ├── form.html          # Lead submission form
        │   └── chat.html          # Chat UI
        └── static/                # (optional) CSS/JS assets
```
## 📐 Design Decisions

**Flask for Backend:**

Flask was selected as the web framework due to its lightweight nature, quick setup, and flexibility, making it ideal for a prototype conversational agent without introducing unnecessary complexity.

**ADK Integration in sales_agent.py:**

A dedicated file was created to handle the AI agent logic separately (sales_agent.py) for better code organization, easier scalability, and to keep the server (app.py) focused purely on handling HTTP requests.

**In-Memory Context Management:**

Conversations are managed independently per user session without persistent storage to ensure simplicity and faster response times. This also meets the concurrent conversation requirement without needing external databases.

**Multi-Tab, Concurrent Conversations:**

Since each browser tab/session maintains its own HTTP connection and conversation context, explicit multi-threading was not necessary at the code level. Flask's built-in server handles concurrent client sessions adequately for this scale.

**Simple CSV (leads.csv) for Lead Storage:**

Instead of setting up a full database, a simple CSV file was used to store leads, optimizing for development speed while maintaining human readability and portability.

**Minimalist Frontend:**

Basic HTML templates (form.html, chat.html) were used with minimal styling to simulate user interactions without investing time into frontend frameworks, focusing the project scope on backend and agent intelligence.

**Single Entry Point (app.py):**

Running the application requires only executing app.py, simplifying the deployment and usage for developers and reviewers.


## License
This project is MIT-licensed. Feel free to use or modify.