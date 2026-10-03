from typing import Literal
from .errors import SkipLlm
from packages.decisions.swarn_decisions.definitions.route_model_tier import RouteModelState

async def choose_model_tier(
    deps, 
    session, 
    ctx, 
    venture_id: str, 
    task_summary: str, 
    step_name: str,
    expected_output: Literal['classification','short_text','long_text','structured_analysis','legal_or_financial'] = 'structured_analysis'
) -> Literal['strong', 'cheap']:
    
    state = RouteModelState(
        step_name=step_name,
        task_summary_redacted=task_summary,
        expected_output=expected_output
    )
    
    # Normally deps.decisions.run_decision(ctx, 'route_model_tier', state)
    # Using a mocked interface for now based on D4
    decision = await deps.decisions.run('route_model_tier', state)
    
    outcome = decision.outcome # e.g. AUTO, ESCALATE
    choice = decision.choice
    
    if outcome == 'ESCALATE':
        return 'strong'
        
    if choice == 'no_llm_needed':
        raise SkipLlm("No LLM needed for this step based on decision.")
    elif choice == 'haiku':
        return 'cheap'
    else: # 'sonnet', 'other'
        return 'strong'
