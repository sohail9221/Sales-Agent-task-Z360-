import requests, pytest, time

BASE = "http://127.0.0.1:5000"

def get_status(lead_id):
    import pandas as pd
    df = pd.read_csv("leads.csv")
    return df.loc[df.lead_id==lead_id, "status"].iloc[0]

def test_full_flow(tmp_path):
    # submit
    r = requests.post(f"{BASE}/submit-form", json={"name": "TestUser"})
    lead_id = r.json()["lead_id"]
    # greet & consent
    requests.post(f"{BASE}/chat-message", json={"lead_id": lead_id, "lead_name": "TestUser"})
    requests.post(f"{BASE}/chat", json={"lead_id": lead_id, "message": "yes"})
    # answer questions quickly
    for ans in ["40","UK","Service Z"]:
        requests.post(f"{BASE}/chat", json={"lead_id": lead_id, "message": ans})
    # final status
    assert get_status(lead_id) == "secured"

def test_no_response(tmp_path):
    r = requests.post(f"{BASE}/submit-form", json={"name": "DeclineUser"})
    lid = r.json()["lead_id"]
    requests.post(f"{BASE}/chat-message", json={"lead_id": lid, "lead_name": "DeclineUser"})
    requests.post(f"{BASE}/chat", json={"lead_id": lid, "message": "no"})
    assert get_status(lid) == "no_response"

def test_followup(tmp_path):
    r = requests.post(f"{BASE}/submit-form", json={"name": "SlowUser"})
    lid = r.json()["lead_id"]
    requests.post(f"{BASE}/chat-message", json={"lead_id": lid, "lead_name": "SlowUser"})
    requests.post(f"{BASE}/chat", json={"lead_id": lid, "message": "yes"})
    # wait >60 s for follow-up
    time.sleep(61)
    resp = requests.post(f"{BASE}/fetch_followups", json={"lead_id": lid})
    assert "Just checking in" in resp.json()["messages"][0]
    # then continue and finish
    for a in ["22","Germany","Product Y"]:
        requests.post(f"{BASE}/chat", json={"lead_id": lid, "message": a})
    assert get_status(lid) == "secured"
