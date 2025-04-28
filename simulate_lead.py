#!/usr/bin/env python3
import requests, time, json

BASE = "http://127.0.0.1:5000"

def simulate_lead(name, answers, pause_for_followup=False):
    print("\n" + "="*50)
    print(f"🚀 Starting Simulation for Lead: {name}")
    print("="*50 + "\n")

    # 1) Submit form
    print("--- Submitting Lead Form ---")
    r = requests.post(f"{BASE}/submit-form", json={"name": name})
    data = r.json()
    lead_id, lead_name = data["lead_id"], data["lead_name"]
    print(f"[submit-form] Lead Registered -> lead_id = {lead_id}\n")

    # 2) Get initial greeting
    print("--- Receiving Initial Greeting ---")
    r = requests.post(f"{BASE}/chat-message", json={"lead_id": lead_id, "lead_name": lead_name})
    print(f"[agent] {r.json()['message']}\n")

    # 3) Consent: Reply “yes”
    print("--- Sending Consent Response (yes) ---")
    r = requests.post(f"{BASE}/chat", json={"lead_id": lead_id, "message": "yes"})
    print(f"[agent] {r.json()['message']}\n")

    # 4) Provide answers one by one
    for i, ans in enumerate(answers):
        # optionally pause to trigger follow-up before answer i
        if pause_for_followup and i == 1:
            print("--- Pausing to Trigger Follow-Up ---")
            print("…Waiting for 10 seconds to simulate inactivity…\n")
            time.sleep(10)

            # fetch follow-up message(s)
            print("--- Fetching Follow-Up Messages ---")
            r2 = requests.post(f"{BASE}/fetch_followups", json={"lead_id": lead_id})
            for msg in r2.json().get("messages", []):
                print(f"[follow-up] {msg}")
            print()

        # send the answer
        print(f"--- Sending Answer {i+1} ---")
        print(f"Input: {ans}")
        r = requests.post(f"{BASE}/chat", json={"lead_id": lead_id, "message": ans})
        print(f"[agent] {r.json()['message']}\n")

    print("="*50)
    print(f"✅ Simulation Completed for Lead: {name}")
    print("="*50 + "\n")

if __name__ == "__main__":
    # normal flow
    simulate_lead("Alice", ["30", "USA", "Product X"])

    # with follow-up pause before answering country
    simulate_lead("Bob", ["25", "Canada", "Service Y"], pause_for_followup=True)

   