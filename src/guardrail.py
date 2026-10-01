import json


VALID_ACTIONS = {"allow", "sanitize", "escalate", "block"}


class PolicyError(ValueError):
    """Raised when guardrail input or policy configuration is invalid."""


def load_json(path):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {path}")
    except json.JSONDecodeError:
        raise ValueError(f"Invalid JSON file: {path}")


def validate_inputs(inputs):
    if not isinstance(inputs, list):
        raise PolicyError("Inputs must be a list.")

    for index, item in enumerate(inputs):
        if not isinstance(item, dict):
            raise PolicyError(
                f"Input at index {index} must be an object."
            )

        required_fields = {"id", "risk", "confidence"}
        missing = required_fields - item.keys()

        if missing:
            raise PolicyError(
                f"Input at index {index} is missing required fields: "
                f"{sorted(missing)}"
            )

        confidence = item["confidence"]

        if isinstance(confidence, bool) or not isinstance(
            confidence, (int, float)
        ):
            raise PolicyError(
                f"Input '{item['id']}' confidence must be a number."
            )

        if not 0.0 <= confidence <= 1.0:
            raise PolicyError(
                f"Input '{item['id']}' confidence must be between "
                f"0.0 and 1.0."
            )


def validate_policies(policies_data):
    if not isinstance(policies_data, dict):
        raise PolicyError("Policy configuration must be an object.")

    policies = policies_data.get("policies")

    if not isinstance(policies, list):
        raise PolicyError("'policies' must be a list.")

    if not policies:
        raise PolicyError("Policy list cannot be empty.")

    default_action = policies_data.get("default_action", "block")

    if default_action not in VALID_ACTIONS:
        raise PolicyError(
            f"Invalid default action: {default_action}. "
            f"Valid actions: {sorted(VALID_ACTIONS)}"
        )

    policy_ids = set()

    for index, policy in enumerate(policies):
        if not isinstance(policy, dict):
            raise PolicyError(
                f"Policy at index {index} must be an object."
            )

        required_fields = {
            "id",
            "risk",
            "min_confidence",
            "action",
        }

        missing = required_fields - policy.keys()

        if missing:
            raise PolicyError(
                f"Policy at index {index} is missing required fields: "
                f"{sorted(missing)}"
            )

        policy_id = policy["id"]

        if policy_id in policy_ids:
            raise PolicyError(
                f"Duplicate policy ID: {policy_id}"
            )

        policy_ids.add(policy_id)

        min_confidence = policy["min_confidence"]

        if isinstance(min_confidence, bool) or not isinstance(
            min_confidence, (int, float)
        ):
            raise PolicyError(
                f"Policy '{policy_id}' min_confidence must be a number."
            )

        if not 0.0 <= min_confidence <= 1.0:
            raise PolicyError(
                f"Policy '{policy_id}' min_confidence must be between "
                f"0.0 and 1.0."
            )

        action = policy["action"]

        if action not in VALID_ACTIONS:
            raise PolicyError(
                f"Policy '{policy_id}' contains invalid action: "
                f"{action}"
            )


def match_policies(policies, risk):
    return [p for p in policies if p.get("risk") == risk]


def evaluate_policy(policy, confidence):
    min_conf = policy.get("min_confidence", 1.0)
    action = policy.get("action")

    if confidence >= min_conf:
        return action

    return None


def final_output_for(action):
    if action == "allow":
        return None

    if action == "sanitize":
        return (
            "This response cannot be shown. "
            "Please consult a qualified professional."
        )

    if action == "escalate":
        return "Sent for human review"

    return "Output blocked"


def process_inputs(policies_data, inputs_data):
    validate_policies(policies_data)
    validate_inputs(inputs_data)

    results = []

    policies = policies_data["policies"]
    default_action = policies_data.get("default_action", "block")

    for item in inputs_data:
        risk = item["risk"]
        confidence = item["confidence"]

        matched = match_policies(policies, risk)

        if not matched:
            decision = default_action
            applied = []
            reason = "no matching policy"

        else:
            applicable = []

            for policy in matched:
                action = evaluate_policy(policy, confidence)

                if action is not None:
                    applicable.append((policy, action))

            if not applicable:
                decision = default_action
                applied = [policy["id"] for policy in matched]

                reason = (
                    f"no policy threshold met: "
                    f"risk={risk}, confidence={confidence}"
                )

            else:
                selected_policy, action = max(
                    applicable,
                    key=lambda item: item[0].get("min_confidence", 0.0)
                )

                decision = action

                applied = [
                    policy["id"]
                    for policy, _ in applicable
                ]

                reason = (
                    f"policy={selected_policy['id']}, "
                    f"risk={risk}, confidence={confidence}"
                )

        results.append({
            "id": item["id"],
            "decision": decision,
            "applied_policies": applied,
            "final_output": final_output_for(decision),
            "reason": reason
        })

    return results


def write_output(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


if __name__ == "__main__":
    policies_data = load_json("config/policies.json")
    inputs_data = load_json("data/inputs.json")

    results = process_inputs(policies_data, inputs_data)

    write_output("examples/output.json", results)

    print("Done. examples/output.json generated.")