from decimal import Decimal
from sqlalchemy import text
from .prices import PRICES_PER_MILLION

async def record_llm_usage(
    session, 
    ctx, 
    venture_id: str, 
    agent: str, 
    model: str, 
    input_tokens: int, 
    output_tokens: int, 
    run_id: str
) -> None:
    input_price_pm, output_price_pm = PRICES_PER_MILLION.get(model, (0.0, 0.0))
    
    cost_usd = (input_tokens / 1_000_000.0) * input_price_pm + (output_tokens / 1_000_000.0) * output_price_pm
    
    stmt = text("""
        INSERT INTO llm_usage (
            tenant_id, venture_id, agent, model, 
            input_tokens, output_tokens, cost_usd, run_id
        ) VALUES (
            :tenant_id, :venture_id, :agent, :model, 
            :input_tokens, :output_tokens, :cost_usd, :run_id
        )
    """)
    
    await session.execute(stmt, {
        "tenant_id": ctx.tenant_id,
        "venture_id": venture_id,
        "agent": agent,
        "model": model,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cost_usd": Decimal(str(cost_usd)),
        "run_id": run_id
    })
