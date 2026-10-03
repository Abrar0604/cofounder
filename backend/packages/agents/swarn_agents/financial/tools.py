from typing import Dict, Any

import math

async def check_spend(venture_id: str) -> Dict[str, Any]:
    """Retrieve the current spending and constraints for the venture."""
    # Simulated db lookup
    db_mock = {
        "v1": {"total_spent": 1250.00, "budget": 5000.00, "burn_rate_per_week": 300.00},
        "v2": {"total_spent": 0.00, "budget": 10000.00, "burn_rate_per_week": 0.00},
    }
    
    record = db_mock.get(venture_id)
    if not record:
        return {"error": "unavailable", "message": f"No financial data for venture {venture_id}"}
        
    return {
        "venture_id": venture_id,
        "total_spent": record["total_spent"],
        "budget": record["budget"],
        "burn_rate_per_week": record["burn_rate_per_week"]
    }

async def simulate_revenue_model(params: Dict[str, Any]) -> Dict[str, Any]:
    """Simulate revenue over time given pricing and growth params."""
    try:
        price = float(params.get("price", 10.0))
        users = int(params.get("users", 100))
        growth_rate = float(params.get("growth_rate", 1.1))
    except (ValueError, TypeError):
        return {"error": "invalid_input", "message": "Non-numeric values provided."}
        
    if not (math.isfinite(price) and math.isfinite(growth_rate)):
        return {"error": "invalid_input", "message": "Non-finite numeric values provided."}
        
    if price < 0 or users < 0:
        return {"error": "invalid_input", "message": "Price and users must be non-negative."}
        
    if growth_rate < 0.0 or growth_rate > 3.0:
        return {"error": "invalid_input", "message": "Growth rate must be between 0.0 and 3.0."}
    
    # 12-month projection
    revenue = []
    current_users = users
    for _ in range(12):
        revenue.append(round(current_users * price, 2))
        current_users *= growth_rate
        
    return {"months": 12, "projected_revenue": revenue, "final_mrr": revenue[-1]}
