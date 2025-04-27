from typing import List, Tuple
import pandas as pd
from google.adk.agents import BaseAgent
from google.adk.events import Event, EventActions
from google.genai import types

CSV_FILE = "leads.csv"

def _append_to_csv(lead_id: str, field: str, value: str) -> None:
    df = pd.read_csv(CSV_FILE)
    df.loc[df['lead_id'] == lead_id, field] = value
    # Check if all required fields are filled
    row = df.loc[df['lead_id'] == lead_id].iloc[0]
    if all(str(row[q[0]]).strip() for q in SalesAgent().questions):
        df.loc[df['lead_id'] == lead_id, 'status'] = 'secured'
    else:
        df.loc[df['lead_id'] == lead_id, 'status'] = 'pending'
    df.to_csv(CSV_FILE, index=False)


def _set_status_in_csv(lead_id: str, status: str) -> None:
    """Convenience to update only the status column."""
    df = pd.read_csv(CSV_FILE)
    df.loc[df['lead_id'] == lead_id, 'status'] = status
    df.to_csv(CSV_FILE, index=False)

class SalesAgent(BaseAgent):
    questions: List[Tuple[str,str]] = []

    def __init__(self):
        super().__init__(
            name="sales_flow_agent",
            description="Collects age, country, interest from leads"
        )
        self.questions = [
            ("age",      "What is your age?"),
            ("country",  "Which country are you from?"),
            ("interest", "What product or service are you interested in?")
        ]

    async def _run_async_impl(self, ctx):
        state = ctx.session.state
        last = (ctx.user_content.parts[0].text or "").strip().lower()
         # 0) Handle the special follow-up trigger
        if last == "__followup__":
            # Only send one follow-up per pending session
            print(f"Follow-up triggered for session {ctx.session.id}")
            if state.get("stage") not in (None, "ended"):
                yield Event(
                    author=self.name,
                    content=types.Content(parts=[types.Part(
                        text="Just checking in to see if you're still interested. "
                             "Let me know when you're ready to continue."
                    )]),
                    actions=EventActions(state_delta={"follow_up_sent": True})
                )
            return

        # 1) First-turn greeting → persist stage="asked_permission"
        if state.get("stage") is None:
            yield Event(
                author=self.name,
                content=types.Content(parts=[types.Part(
                    text=f"Hey {state['name']}, thank you for filling out the form. May I ask you some questions?"
                )]),
                actions=EventActions(state_delta={"stage": "asked_permission"})
            )
            return

        # 2) “No” branch → persist status="no_response" & stage="ended"
        if state.get("stage") == "asked_permission" and last in ("no", "not now"):
            # **Update the CSV status column to 'no_response'**
            _set_status_in_csv(ctx.session.id, "no_response")
            yield Event(
                author=self.name,
                content=types.Content(parts=[types.Part(
                    text="Alright, no problem. Have a great day!"
                )]),
                actions=EventActions(state_delta={
                    "status": "no_response",
                    "stage": "ended"
                })
            )
            return

        # 3) “Yes” branch → move into question #1
        if state.get("stage") == "asked_permission" and last in ("yes", "sure", "ok"):
            first_prompt = self.questions[0][1]
            yield Event(
                author=self.name,
                content=types.Content(parts=[types.Part(text=first_prompt)]),
                actions=EventActions(state_delta={"stage": 1})
            )
            return

        # 4) Handle subsequent questions
        idx = state.get("stage", 0)
        if isinstance(idx, int) and idx > 0:
            # store the previous answer
            prev_key = self.questions[idx - 1][0]
            _append_to_csv(ctx.session.id, prev_key, last)
            _set_status_in_csv(ctx.session.id, "pending")

        # 5) Ask next question or finish
        if isinstance(idx, int) and idx < len(self.questions):
            _, prompt = self.questions[idx]
            new_stage = idx + 1
            yield Event(
                author=self.name,
                content=types.Content(parts=[types.Part(text=prompt)]),
                actions=EventActions(state_delta={"stage": new_stage})
            )
        else:
            df = pd.read_csv(CSV_FILE)
            row = df.loc[df['lead_id'] == ctx.session.id].iloc[0]
            if all(str(row[q[0]]).strip() for q in self.questions):
                _set_status_in_csv(ctx.session.id, "secured")
            # done
            yield Event(
                author=self.name,
                content=types.Content(parts=[types.Part(
                    text="Thank you for your time. Have a great day!"
                )]),
                actions=EventActions(state_delta={"status": "secured", "stage": "ended"})
            )
            return
