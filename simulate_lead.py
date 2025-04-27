#!/usr/bin/env python3
import requests, time, json

BASE = "http://127.0.0.1:5000"

def simulate_lead(name, answers, pause_for_followup=False):
    # 1) Submit form
    r = requests.post(f"{BASE}/submit-form", json={"name": name})
    data = r.json()
    lead_id, lead_name = data["lead_id"], data["lead_name"]
    print(f"[submit-form] lead_id={lead_id}")

    # 2) Get greeting
    r = requests.post(f"{BASE}/chat-message", json={"lead_id": lead_id, "lead_name": lead_name})
    print(f"[agent] {r.json()['message']}")

    # 3) If consent, reply “yes”
    r = requests.post(f"{BASE}/chat", json={"lead_id": lead_id, "message": "yes"})
    print(f"[agent] {r.json()['message']}")

    # 4) Provide answers one by one
    for i, ans in enumerate(answers):
        # optionally pause to trigger follow-up before answer i
        if pause_for_followup and i == 1:
            print("…waiting 10 s to trigger follow-up…")
            time.sleep(10)
            # fetch any follow-ups
            r2 = requests.post(f"{BASE}/fetch_followups", json={"lead_id": lead_id})
            for msg in r2.json().get("messages", []):
                print(f"[follow-up] {msg}")
        # send the answer
        r = requests.post(f"{BASE}/chat", json={"lead_id": lead_id, "message": ans})
        print(f"[agent] {r.json()['message']}")

if __name__ == "__main__":
    # normal flow
    simulate_lead("Alice", ["30", "USA", "Product X"])
    # with follow-up pause before country
    simulate_lead("Bob", ["25", "Canada", "Service Y"], pause_for_followup=True)
