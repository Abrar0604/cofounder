from typing import Dict, Any

async def check_spend(venture_id: str) -> Dict[str, Any]:
    """Retrieve the current spending and constraints for the venture."""
    # In a real setup, this would query the db
    return {
        "venture_id": venture_id,
        "total_spent": 1250.00,
        "budget": 5000.00,
        "burn_rate_per_week": 300.00
    }

async def simulate_revenue_model(params: Dict[str, Any]) -> Dict[str, Any]:
    """Simulate revenue over time given pricing and growth params."""
    price = params.get("price", 10.0)
    users = params.get("users", 100)
    growth_rate = params.get("growth_rate", 1.1)
    
    # 12-month projection
    revenue = []
    current_users = users
    for _ in range(12):
        revenue.append(round(current_users * price, 2))
        current_users *= growth_rate
        
    return {"months": 12, "projected_revenue": revenue, "final_mrr": revenue[-1]}
