from typing import Dict
from .base.agent_spec import AgentSpec

from .market_intel.graph import get_spec as get_market_intel_spec
from .validation.graph import get_spec as get_validation_spec
from .financial.graph import get_spec as get_financial_spec
from .legal.graph import get_spec as get_legal_spec
from .web.graph import get_spec as get_web_spec
from .marketing.graph import get_spec as get_marketing_spec
from .sales.graph import get_spec as get_sales_spec
from .support.graph import get_spec as get_support_spec

AGENT_SPECS: Dict[str, AgentSpec] = {
    "market_intel": get_market_intel_spec(),
    "validation": get_validation_spec(),
    "financial": get_financial_spec(),
    "legal": get_legal_spec(),
    "web": get_web_spec(),
    "marketing": get_marketing_spec(),
    "sales": get_sales_spec(),
    "support": get_support_spec()
}
