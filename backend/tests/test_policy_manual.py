from src.policy.engine import PolicyEngine, PolicyDecision
from src.tools.base import RiskLevel

def test_audit_mode():
    print("Testing AUDIT mode...")
    engine = PolicyEngine(mode="audit")
    
    decision = engine.check_permission("test_tool", RiskLevel.HIGH, {})
    print(f"High Risk Tool in Audit: {decision}")
    assert decision == PolicyDecision.ALLOW

def test_enforce_mode():
    print("Testing ENFORCE mode...")
    engine = PolicyEngine(mode="enforce")
    
    # Low Risk -> Allow
    d1 = engine.check_permission("list_files", RiskLevel.LOW, {})
    print(f"Low Risk Tool: {d1}")
    assert d1 == PolicyDecision.ALLOW
    
    # Medium Risk -> Allow
    d2 = engine.check_permission("read_emails", RiskLevel.MEDIUM, {})
    print(f"Medium Risk Tool: {d2}")
    assert d2 == PolicyDecision.ALLOW
    
    # High Risk -> Require Approval
    d3 = engine.check_permission("send_email", RiskLevel.HIGH, {})
    print(f"High Risk Tool: {d3}")
    assert d3 == PolicyDecision.REQUIRE_APPROVAL

if __name__ == "__main__":
    try:
        test_audit_mode()
        test_enforce_mode()
        print("ALL POLICY TESTS PASSED!")
    except AssertionError as e:
        print(f"TEST FAILED: {e}")
    except Exception as e:
        print(f"ERROR: {e}")
