import argparse

from .core import load_json, process_inputs, write_output


def main():
    parser = argparse.ArgumentParser(
        description="AI Guardrail Engine"
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True
    )

    evaluate_parser = subparsers.add_parser(
        "evaluate",
        help="Evaluate inputs against guardrail policies"
    )

    evaluate_parser.add_argument(
        "--policies",
        required=True,
        help="Path to the policy JSON file"
    )

    evaluate_parser.add_argument(
        "--input",
        required=True,
        dest="input_file",
        help="Path to the input JSON file"
    )

    evaluate_parser.add_argument(
        "--output",
        default="examples/output.json",
        help="Path for the output JSON file"
    )

    args = parser.parse_args()

    if args.command == "evaluate":
        policies_data = load_json(args.policies)
        inputs_data = load_json(args.input_file)

        results = process_inputs(
            policies_data,
            inputs_data
        )

        write_output(args.output, results)

        print(f"Evaluation complete. Output written to {args.output}")


if __name__ == "__main__":
    main()
