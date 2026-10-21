
import json
from contextlib import redirect_stdout
from io import StringIO

import src.main as workflow
from src.main import MockLLM
from src.agents.ai_decision_agent import AIDecisionAgent


def main():
    # 1. Verify that the AI agent uses the offline MockLLM.
    agent = AIDecisionAgent(llm=MockLLM())

    assert agent.llm.__class__ is MockLLM

    response = agent.llm.generate("Offline test only")

    assert response.provider == "mock"
    assert response.model == "offline-demo"

    payload = json.loads(response.content)

    assert payload["action"] == "HOLD"
    assert payload["confidence"] == 0.0

    print("PASS: offline MockLLM response verified.")

    # 2. Run the complete offline workflow and capture its output.
    output = StringIO()

    with redirect_stdout(output):
        workflow.main()

    workflow_output = output.getvalue()

    # 3. Verify the research, decision, and risk stages.
    expected_output = [
        "--- Market Research ---",
        "--- News Sentiment ---",
        "--- AI Proposal (Mock) ---",
        "Action: HOLD",
        "Confidence: 0.0",
        "--- Risk Validation ---",
        "Status: REJECT",
        "HOLD proposals do not authorize an order.",
        "No order was created or executed.",
    ]

    for expected in expected_output:
        assert expected in workflow_output, (
            f"Expected workflow output was missing: {expected}"
        )

    print("PASS: market research and news sentiment stages verified.")
    print("PASS: AI HOLD proposal verified.")
    print("PASS: Risk Engine rejected the HOLD proposal.")
    print("PASS: no order was created or executed.")
    print("No external API request or real trade occurred.")


if __name__ == "__main__":
    main()
