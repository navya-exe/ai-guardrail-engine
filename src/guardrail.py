import json

def load_json(path):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {path}")
    except json.JSONDecodeError:
        raise ValueError(f"Invalid JSON file: {path}")


def match_policies(policies, risk):
    return [p for p in policies if p.get("risk") == risk]


def evaluate_policy(policy, confidence):
    min_conf = policy.get("min_confidence", 1.0)
    actions = policy.get("allowed_actions", [])

    if confidence >= min_conf:
        return actions

    return []


def final_output_for(action):
    if action == "allow":
        return None

    if action == "sanitize":
        return "This response cannot be shown. Please consult a qualified professional."

    if action == "escalate":
        return "Sent for human review"

    return "Output blocked"


def process_inputs(policies_data, inputs_data):
    results = []

    policies = policies_data.get("policies", [])
    default_action = policies_data.get("default_action", "block")

    for item in inputs_data:
        risk = item.get("risk")
        confidence = item.get("confidence", 0.0)

        matched = match_policies(policies, risk)

        if not matched:
            decision = default_action
            applied = []
            reason = "no matching policy"

        else:
            applicable = []

            for policy in matched:
                actions = evaluate_policy(policy, confidence)

                if actions:
                    applicable.append((policy, actions))

            if not applicable:
                decision = default_action
                applied = [policy.get("id") for policy in matched]

                reason = (
                    f"no policy threshold met: "
                    f"risk={risk}, confidence={confidence}"
                )

            else:
                selected_policy, actions = max(
                    applicable,
                    key=lambda item: item[0].get("min_confidence", 0.0)
                )

                decision = actions[0]

                applied = [
                    policy.get("id")
                    for policy, _ in applicable
                ]

                reason = (
                    f"policy={selected_policy.get('id')}, "
                    f"risk={risk}, confidence={confidence}"
                )

        results.append({
            "id": item.get("id"),
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
