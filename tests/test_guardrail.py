from src.guardrail import process_inputs


POLICIES = {
    "policies": [
        {
            "id": "MED_STRICT",
            "risk": "medical",
            "allowed_actions": ["escalate"],
            "min_confidence": 0.95
        },
        {
            "id": "MED_BLOCK",
            "risk": "medical",
            "allowed_actions": ["block"],
            "min_confidence": 0.0
        },
        {
            "id": "FIN_STRICT",
            "risk": "financial",
            "allowed_actions": ["sanitize", "escalate"],
            "min_confidence": 0.9
        },
        {
            "id": "FIN_RELAXED",
            "risk": "financial",
            "allowed_actions": ["allow"],
            "min_confidence": 0.8
        },
        {
            "id": "GEN_ALLOW",
            "risk": "general",
            "allowed_actions": ["allow"],
            "min_confidence": 0.7
        },
        {
            "id": "GEN_SANITIZE",
            "risk": "general",
            "allowed_actions": ["sanitize"],
            "min_confidence": 0.0
        }
    ],
    "default_action": "block"
}


def test_allow():
    inputs = [
        {
            "id": "T1",
            "risk": "general",
            "confidence": 0.92
        }
    ]

    result = process_inputs(POLICIES, inputs)[0]

    assert result["decision"] == "allow"


def test_sanitize():
    inputs = [
        {
            "id": "T2",
            "risk": "general",
            "confidence": 0.55
        }
    ]

    result = process_inputs(POLICIES, inputs)[0]

    assert result["decision"] == "sanitize"


def test_escalate():
    inputs = [
        {
            "id": "T3",
            "risk": "medical",
            "confidence": 0.96
        }
    ]

    result = process_inputs(POLICIES, inputs)[0]

    assert result["decision"] == "escalate"


def test_block():
    inputs = [
        {
            "id": "T4",
            "risk": "medical",
            "confidence": 0.82
        }
    ]

    result = process_inputs(POLICIES, inputs)[0]

    assert result["decision"] == "block"


def test_unknown_risk():
    inputs = [
        {
            "id": "T5",
            "risk": "unknown",
            "confidence": 0.99
        }
    ]

    result = process_inputs(POLICIES, inputs)[0]

    assert result["decision"] == "block"
    assert result["applied_policies"] == []


def test_low_confidence():
    inputs = [
        {
            "id": "T6",
            "risk": "financial",
            "confidence": 0.65
        }
    ]

    result = process_inputs(POLICIES, inputs)[0]

    assert result["decision"] == "block"


def test_multiple_matching_policies():
    inputs = [
        {
            "id": "T7",
            "risk": "medical",
            "confidence": 0.96
        }
    ]

    result = process_inputs(POLICIES, inputs)[0]

    assert result["decision"] == "escalate"
    assert "MED_STRICT" in result["applied_policies"]
    assert "MED_BLOCK" in result["applied_policies"]
    assert result["reason"].startswith("policy=MED_STRICT")