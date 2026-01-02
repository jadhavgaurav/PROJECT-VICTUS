import logging
from enum import Enum
from typing import Any, Dict, Optional
from ..tools.base import RiskLevel
from ..config import settings

logger = logging.getLogger(__name__)

class PolicyDecision(str, Enum):
    ALLOW = "allow"
    DENY = "deny"
    REQUIRE_APPROVAL = "require_approval"

class PolicyEngine:
    def __init__(self, mode: str = None):
        self.mode = mode or settings.POLICY_MODE
        self.logger = logger

    def check_permission(
        self, 
        tool_name: str, 
        risk_level: RiskLevel, 
        args: Dict[str, Any], 
        user_id: Optional[str] = None
    ) -> PolicyDecision:
        """
        Determines if a tool execution is allowed.
        """
        self.logger.info(f"Policy Check: tool={tool_name}, risk={risk_level}, mode={self.mode}")

        # In AUDIT mode, we log but allow everything (except maybe strictly forbidden things?)
        # The prompt says: "Audit mode logs but does not block."
        if self.mode == "audit":
            self.logger.info(f"AUDIT MODE: Allowed action {tool_name} (risk: {risk_level})")
            return PolicyDecision.ALLOW

        # ENFORCE mode logic
        if risk_level == RiskLevel.LOW or risk_level == RiskLevel.MEDIUM:
            return PolicyDecision.ALLOW
        
        if risk_level == RiskLevel.HIGH:
            # High risk requires approval
            return PolicyDecision.REQUIRE_APPROVAL
        
        # Default strict fallback
        return PolicyDecision.DENY

# Global instance
policy_engine = PolicyEngine()
