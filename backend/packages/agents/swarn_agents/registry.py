from typing import Dict
from .base.agent_spec import AgentSpec

from .market_intel.graph import get_spec as get_market_intel_spec
from .validation.graph import get_spec as get_validation_spec
from .financial.graph import get_spec as get_financial_spec

AGENT_SPECS: Dict[str, AgentSpec] = {
    "market_intel": get_market_intel_spec(),
    "validation": get_validation_spec(),
    "financial": get_financial_spec()
}
