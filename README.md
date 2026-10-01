AI Guardrail Engine
A lightweight, policy-driven AI safety layer for evaluating AI-generated outputs against configurable risk policies and confidence thresholds.
The engine provides deterministic decisions such as allow, sanitize, escalate, or block based on structured risk and confidence inputs.

Overview

Modern AI applications need a reliable decision layer between model output and the end user.
An AI model may produce content that requires different handling depending on:
- Risk category
- Classification confidence
- Configured policy thresholds
- Default safety behaviour

The AI Guardrail Engine separates this policy enforcement logic from the AI model itself.
The current system accepts a risk category and confidence score, evaluates the configured policies, and produces a structured decision.

                    Input
                      │
                      ▼
             Risk + Confidence
                      │
                      ▼
             Input Validation
                      │
                      ▼
               Match Policies
                      │
                      ▼
            Check Confidence
                      │
                      ▼
             Select Policy
                      │
                      ▼
             Resolve Action
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
        Allow      Sanitize    Escalate
                      │
                      ▼
                    Block

Key Features

Policy-driven decisions
Policies are stored separately from the application logic in:
config/policies.json
This allows policy behavior to be changed without modifying the core engine.
Confidence-based policy evaluation
Every policy defines a minimum confidence threshold.
A policy becomes applicable when:
confidence >= min_confidence
Four supported actions
Action	Behavior
allow	Permit the output
sanitize	Replace the output with a safer response
escalate	Send the case for human review
block	Prevent the output from being shown


Deterministic policy resolution
When multiple policies match the same risk category, the engine:
1. Matches policies by risk.
2. Checks confidence thresholds.
3. Removes policies whose thresholds are not satisfied.
4. Selects the applicable policy with the highest threshold.
5. Uses that policy's configured action.
If multiple applicable policies have the same threshold, action priority is used:
allow < sanitize < escalate < block
Therefore, a tie is resolved toward the more restrictive action.
Input and policy validation
The engine validates:
- Required input fields
- Confidence values
- Policy structure
- Policy IDs
- Duplicate policy IDs
- Policy confidence thresholds
- Supported actions
- Default action
- Empty policy configurations
- Invalid data types
Invalid configurations raise a custom:
PolicyError
Command-line interface
The engine can be executed directly from the terminal:
guardrail evaluate \
  --policies config/policies.json \
  --input data/inputs.json
The CLI writes the evaluation results to:
examples/output.json
Automated testing
The project currently contains:
27 tests
covering normal behavior, validation, boundary conditions, malformed input, policy conflicts, and tie-breaking.
Current test result:
27 passed
Code quality and coverage
The project uses:
- Ruff for linting
- pytest for testing
- pytest-cov for code coverage
- GitHub Actions for CI
Current local coverage:
77%
Architecture
The project follows a small Python package structure:
ai-guardrail-engine/
│
├── src/
│   └── guardrail/
│       ├── __init__.py
│       ├── core.py
│       └── cli.py
│
├── config/
│   └── policies.json
│
├── data/
│   └── inputs.json
│
├── examples/
│   └── output.json
│
├── tests/
│   └── test_guardrail.py
│
├── .github/
│   └── workflows/
│       └── tests.yml
│
├── pyproject.toml
├── requirements.txt
├── README.md
└── LICENSE
Core Components
src/guardrail/core.py
Contains the main policy engine.
Responsibilities include:
- Loading JSON configuration
- Validating inputs
- Validating policies
- Matching policies by risk
- Evaluating confidence thresholds
- Resolving applicable policies
- Selecting the final action
- Producing structured results
- Writing JSON output
The main processing function is:
process_inputs(policies_data, inputs_data)
src/guardrail/cli.py
Provides the command-line interface.
Example:
guardrail evaluate \
  --policies config/policies.json \
  --input data/inputs.json
The CLI loads the supplied files, evaluates the inputs, and writes the resulting decisions.
config/policies.json
Contains the configurable policy definitions.
Example:
{
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
    }
  ],
  "default_action": "block"
}
Each policy contains:
Field	Description
id	Unique policy identifier
risk	Risk category the policy applies to
action	Action taken when the policy applies
min_confidence	Minimum confidence required


The configuration also defines:
"default_action": "block"
This provides a deterministic fallback when no applicable policy exists.
Policy Evaluation
Suppose an input contains:
{
  "id": "R1",
  "risk": "medical",
  "confidence": 0.96
}
The engine finds:
MED_STRICT
threshold = 0.95
action = escalate
and:
MED_BLOCK
threshold = 0.00
action = block
Both policies satisfy the confidence threshold:
0.96 >= 0.95
0.96 >= 0.00
The engine therefore selects the policy with the highest applicable threshold:
MED_STRICT
and produces:
escalate
This allows more specific policies to override broader fallback policies.
Structured Output
The engine produces structured JSON results.
Example:
{
  "id": "R1",
  "decision": "escalate",
  "applied_policies": [
    "MED_STRICT",
    "MED_BLOCK"
  ],
  "final_output": "Sent for human review",
  "reason": "policy=MED_STRICT, risk=medical, confidence=0.96"
}
Output fields
Field	Description
id	Identifier of the evaluated input
decision	Final action selected
applied_policies	Policies whose thresholds were satisfied
final_output	Resulting output behavior
reason	Explanation of the policy decision


Validation
The engine rejects invalid inputs and policy configurations before evaluation.
Examples of invalid configurations include:
Confidence < 0.0
Confidence > 1.0
Missing required fields
Invalid confidence types
Duplicate policy IDs
Invalid policy actions
Invalid policy thresholds
Invalid default actions
Empty policy lists
Malformed JSON
For example:
PolicyError("Policy 'MED_STRICT' min_confidence must be between 0.0 and 1.0.")
This prevents invalid configuration from silently producing unsafe decisions.
Installation
Clone the repository:
git clone https://github.com/navya-exe/ai-guardrail-engine.git
cd ai-guardrail-engine
Install the project in editable mode:
python -m pip install -e .
Install development dependencies:
python -m pip install -r requirements.txt
Usage
Evaluate inputs
Run:
guardrail evaluate \
  --policies config/policies.json \
  --input data/inputs.json
Expected output:
Evaluation complete. Output written to examples/output.json
The generated results are stored in:
examples/output.json
Testing
Run the complete test suite:
python -m pytest -q
Current result:
27 passed
Code Coverage
Run tests with coverage:
python -m pytest --cov=guardrail --cov-report=term-missing
Current coverage:
77%
Coverage currently includes:
guardrail/__init__.py    100%
guardrail/cli.py           0%
guardrail/core.py         89%

TOTAL                     77%
The CLI currently has limited direct test coverage because the majority of behavior is exercised through the core policy engine.
Code Quality
The project uses Ruff for static analysis and formatting checks.
Run:
ruff check .
Expected:
All checks passed!
Continuous Integration
GitHub Actions automatically runs the project's quality checks.
The CI pipeline performs:
Checkout repository
        │
        ▼
Set up Python
        │
        ▼
Install dependencies
        │
        ▼
Install project
        │
        ▼
Ruff
        │
        ▼
Pytest + Coverage
This helps prevent regressions when changes are pushed to the repository or submitted through pull requests.
Design Principles
Separation of policy and implementation
Policy configuration is stored in JSON rather than embedded directly in Python.
This makes policy changes easier to manage independently from application logic.
Deterministic decisions
The same input and policy configuration produce the same decision.
Explicit fallback behavior
If no policy matches, or no applicable policy satisfies the confidence threshold, the engine uses:
block
by default.
Fail-fast validation
Invalid inputs and policy configurations are rejected before policy evaluation begins.
Testable core logic
The policy engine can be tested independently through:
process_inputs(...)
This keeps the core decision logic independent from the CLI and file system interface.
Current Limitations
The current implementation focuses on the policy enforcement layer.
It does not yet perform:
- Risk classification from raw text
- LLM inference
- Prompt-injection detection
- Jailbreak detection
- PII detection
- Toxicity classification
- Malicious-content classification
- Real PII redaction
- Persistent audit logging
- Authentication
- Distributed execution
- Policy versioning
The current engine assumes that the risk category and confidence score are already available.
Roadmap
The project is being developed incrementally toward a more complete AI safety enforcement layer.
Planned capabilities include:
Classification
Add a pluggable classifier interface:
classify(text) -> (risk, confidence)
with:
- Keyword/regex baseline
- Structured LLM classification
Safety detection
Add detection for:
- PII
- Prompt injection
- Jailbreak patterns
Sanitization
Replace the current generic sanitization response with actual redaction of detected sensitive content.
Audit logging
Add structured JSONL audit records containing:
- Timestamp
- Input ID
- Selected policy
- Decision
- Policy version
- Policy hash
API
Expose the engine through:
POST /evaluate
using:
- FastAPI
- Pydantic
Containerization
Add Docker support for reproducible deployment.
Evaluation
Create a labeled evaluation dataset and measure:
- Precision
- Recall
- F1 score
- Confusion matrix
- Policy decision accuracy
Technologies
- Python
- JSON
- pytest
- pytest-cov
- Ruff
- argparse
- setuptools
- Git
- GitHub Actions
Project Status
Current implementation includes:
- Policy-based risk evaluation
- Confidence threshold handling
- Input validation
- Policy validation
- Duplicate policy detection
- Deterministic policy resolution
- Action tie-breaking
- Allow / sanitize / escalate / block actions
- Default blocking behavior
- Structured JSON output
- Python package structure
- Editable installation
- Command-line interface
- Automated tests
- Ruff linting
- Test coverage
- GitHub Actions CI
Current test status:
27 tests passed
77% code coverage
Ruff checks passed
