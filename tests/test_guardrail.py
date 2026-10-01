from src.guardrail import process_inputs, PolicyError


POLICIES = {
    "policies": [
        {
            "id": "MED_STRICT",
            "risk": "medical",
            "action": "escalate",
            "min_confidence": 0.95
        },
        {
            "id": "MED_BLOCK",
            "risk": "medical",
            "action": "block",
            "min_confidence": 0.0
        },
        {
            "id": "FIN_STRICT",
            "risk": "financial",
            "action": "sanitize",
            "min_confidence": 0.9
        },
        {
            "id": "FIN_RELAXED",
            "risk": "financial",
            "action": "allow",
            "min_confidence": 0.8
        },
        {
            "id": "GEN_ALLOW",
            "risk": "general",
            "action": "allow",
            "min_confidence": 0.7
        },
        {
            "id": "GEN_SANITIZE",
            "risk": "general",
            "action": "sanitize",
            "min_confidence": 0.0
        }
    ],
    "default_action": "block"
}


# --------------------------------------------------
# Existing behavior tests
# --------------------------------------------------

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


# --------------------------------------------------
# Step 1: Input and policy validation tests
# --------------------------------------------------

def test_confidence_below_zero():
    inputs = [
        {
            "id": "T8",
            "risk": "general",
            "confidence": -0.1
        }
    ]

    try:
        process_inputs(POLICIES, inputs)
        assert False, "Expected PolicyError"
    except PolicyError as exc:
        assert "between 0.0 and 1.0" in str(exc)


def test_confidence_above_one():
    inputs = [
        {
            "id": "T9",
            "risk": "general",
            "confidence": 1.1
        }
    ]

    try:
        process_inputs(POLICIES, inputs)
        assert False, "Expected PolicyError"
    except PolicyError as exc:
        assert "between 0.0 and 1.0" in str(exc)


def test_missing_required_input_field():
    inputs = [
        {
            "id": "T10",
            "risk": "general"
        }
    ]

    try:
        process_inputs(POLICIES, inputs)
        assert False, "Expected PolicyError"
    except PolicyError as exc:
        assert "confidence" in str(exc)


def test_duplicate_policy_id():
    policies = {
        "policies": [
            {
                "id": "DUPLICATE",
                "risk": "general",
                "action": "allow",
                "min_confidence": 0.5
            },
            {
                "id": "DUPLICATE",
                "risk": "medical",
                "action": "block",
                "min_confidence": 0.0
            }
        ],
        "default_action": "block"
    }

    try:
        process_inputs(policies, [])
        assert False, "Expected PolicyError"
    except PolicyError as exc:
        assert "Duplicate policy ID" in str(exc)


def test_empty_policy_list():
    policies = {
        "policies": [],
        "default_action": "block"
    }

    try:
        process_inputs(policies, [])
        assert False, "Expected PolicyError"
    except PolicyError as exc:
        assert "Policy list cannot be empty" in str(exc)


def test_invalid_action():
    policies = {
        "policies": [
            {
                "id": "BAD_ACTION",
                "risk": "general",
                "action": "something_invalid",
                "min_confidence": 0.5
            }
        ],
        "default_action": "block"
    }

    try:
        process_inputs(policies, [])
        assert False, "Expected PolicyError"
    except PolicyError as exc:
        assert "invalid action" in str(exc)


def test_invalid_policy_confidence():
    policies = {
        "policies": [
            {
                "id": "BAD_CONF",
                "risk": "general",
                "action": "allow",
                "min_confidence": 1.5
            }
        ],
        "default_action": "block"
    }

    try:
        process_inputs(policies, [])
        assert False, "Expected PolicyError"
    except PolicyError as exc:
        assert "between 0.0 and 1.0" in str(exc)

def test_tie_breaking_prefers_more_restrictive_action():
    policies = {
        "policies": [
            {
                "id": "TIE_ALLOW",
                "risk": "general",
                "action": "allow",
                "min_confidence": 0.8
            },
            {
                "id": "TIE_BLOCK",
                "risk": "general",
                "action": "block",
                "min_confidence": 0.8
            }
        ],
        "default_action": "block"
    }

    inputs = [
        {
            "id": "TIE_TEST",
            "risk": "general",
            "confidence": 0.9
        }
    ]

    result = process_inputs(policies, inputs)[0]

    assert result["decision"] == "block"
    assert result["reason"].startswith("policy=TIE_BLOCK")
