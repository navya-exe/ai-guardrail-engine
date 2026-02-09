import json
ACTION_PRIORITY = {
    "allow": 1,
    "sanitize": 2,
    "escalate": 3,
    "block": 4
}

def load_json(path):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception:
        return {}

def match_policies(policies, risk):
    return [p for p in policies if p.get("risk") == risk]

def evaluate_policy(policy, confidence):
    min_conf = policy.get("min_confidence", 1.0)
    actions = policy.get("allowed_actions", [])

    if confidence >= min_conf:
        return actions
    else:
        return ["block"]


def resolve_action(action_lists, default_action):
    final_action = default_action

    for actions in action_lists:
        for action in actions:
            if ACTION_PRIORITY.get(action, 0) > ACTION_PRIORITY.get(final_action, 0):
                final_action = action

    return final_action


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
            action_lists = []
            applied = []

            for policy in matched:
                action_lists.append(evaluate_policy(policy, confidence))
                applied.append(policy.get("id"))

            decision = resolve_action(action_lists, default_action)
            reason = f"risk={risk}, confidence={confidence}"

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
    policies_data = load_json("policies.json")
    inputs_data = load_json("inputs.json")

    results = process_inputs(policies_data, inputs_data)
    write_output("output.json", results)

    print("Done. output.json generated.")
