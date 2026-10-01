from guardrail import PolicyError, load_json, process_inputs

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


def test_threshold_exactly_equal_to_confidence():
    inputs = [
        {
            "id": "T16",
            "risk": "medical",
            "confidence": 0.95
        }
    ]

    result = process_inputs(POLICIES, inputs)[0]

    assert result["decision"] == "escalate"


def test_confidence_zero():
    inputs = [
        {
            "id": "T17",
            "risk": "medical",
            "confidence": 0.0
        }
    ]

    result = process_inputs(POLICIES, inputs)[0]

    assert result["decision"] == "block"


def test_confidence_one():
    inputs = [
        {
            "id": "T18",
            "risk": "general",
            "confidence": 1.0
        }
    ]

    result = process_inputs(POLICIES, inputs)[0]

    assert result["decision"] == "allow"


def test_empty_inputs():
    result = process_inputs(POLICIES, [])

    assert result == []


def test_malformed_json(tmp_path):
    json_file = tmp_path / "invalid.json"
    json_file.write_text("{ invalid json }")

    try:
        load_json(json_file)
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert "Invalid JSON file" in str(exc)


def test_invalid_default_action():
    policies = {
        "policies": [
            {
                "id": "VALID_POLICY",
                "risk": "general",
                "action": "allow",
                "min_confidence": 0.5
            }
        ],
        "default_action": "invalid_action"
    }

    try:
        process_inputs(policies, [])
        assert False, "Expected PolicyError"
    except PolicyError as exc:
        assert "Invalid default action" in str(exc)


def test_invalid_input_confidence_type():
    inputs = [
        {
            "id": "T19",
            "risk": "general",
            "confidence": "high"
        }
    ]

    try:
        process_inputs(POLICIES, inputs)
        assert False, "Expected PolicyError"
    except PolicyError as exc:
        assert "confidence must be a number" in str(exc)


def test_boolean_confidence_is_rejected():
    inputs = [
        {
            "id": "T20",
            "risk": "general",
            "confidence": True
        }
    ]

    try:
        process_inputs(POLICIES, inputs)
        assert False, "Expected PolicyError"
    except PolicyError as exc:
        assert "confidence must be a number" in str(exc)


def test_invalid_policy_confidence_type():
    policies = {
        "policies": [
            {
                "id": "BAD_CONF_TYPE",
                "risk": "general",
                "action": "allow",
                "min_confidence": "high"
            }
        ],
        "default_action": "block"
    }

    try:
        process_inputs(policies, [])
        assert False, "Expected PolicyError"
    except PolicyError as exc:
        assert "min_confidence must be a number" in str(exc)


def test_missing_required_policy_field():
    policies = {
        "policies": [
            {
                "id": "MISSING_ACTION",
                "risk": "general",
                "min_confidence": 0.5
            }
        ],
        "default_action": "block"
    }

    try:
        process_inputs(policies, [])
        assert False, "Expected PolicyError"
    except PolicyError as exc:
        assert "action" in str(exc)


def test_tie_breaking_escalate_over_sanitize():
    policies = {
        "policies": [
            {
                "id": "TIE_SANITIZE",
                "risk": "general",
                "action": "sanitize",
                "min_confidence": 0.8
            },
            {
                "id": "TIE_ESCALATE",
                "risk": "general",
                "action": "escalate",
                "min_confidence": 0.8
            }
        ],
        "default_action": "block"
    }

    inputs = [
        {
            "id": "TIE_TEST_2",
            "risk": "general",
            "confidence": 0.9
        }
    ]

    result = process_inputs(policies, inputs)[0]

    assert result["decision"] == "escalate"
    assert result["reason"].startswith("policy=TIE_ESCALATE")


def test_inputs_must_be_a_list():
    inputs = {
        "id": "T21",
        "risk": "general",
        "confidence": 0.9
    }

    try:
        process_inputs(POLICIES, inputs)
        assert False, "Expected PolicyError"
    except PolicyError as exc:
        assert "Inputs must be a list" in str(exc)
