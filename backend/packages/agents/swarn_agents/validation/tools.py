from typing import Dict, Any

def check_compliance_rules(industry: str) -> Dict[str, Any]:
    """Check standard compliance rules for the given industry."""
    rules = {
        "finance": ["KYC", "AML", "PCI-DSS"],
        "healthcare": ["HIPAA"],
        "ecommerce": ["PCI-DSS", "GDPR"]
    }
    return {"industry": industry, "rules": rules.get(industry.lower(), ["GDPR"])}
