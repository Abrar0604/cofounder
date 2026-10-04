from packages.agents.swarn_agents.orchestrator.state import OrchestratorState
from langgraph.types import interrupt

async def ask_for_survey(deps, state: OrchestratorState) -> dict:
    # Generate the survey payload (this could be done dynamically by LLM in real-world, but we hardcode for now as a realistic stub or use simple prompt)
    payload = {
        "type": "survey",
        "title": "Need more context for your venture",
        "questions": [
            {
                "id": "target_customer",
                "text": "Who is your primary target customer?",
                "options": ["B2B Enterprise", "B2B SMB", "B2C Consumers"]
            },
            {
                "id": "price_band",
                "text": "What is the expected price band?",
                "options": ["Low Cost", "Mid Tier", "Premium"]
            }
        ]
    }
    
    # Pause execution, wait for user to answer
    survey_results = interrupt(payload)
    
    return {
        "survey_results": survey_results,
        "needs_clarification": False
    }
