\# AI Guardrail Engine



A lightweight, policy-driven AI guardrail engine that evaluates AI-generated outputs using risk categories and confidence thresholds.



The system determines how an output should be handled using four possible actions:



\- Allow

\- Sanitize

\- Escalate

\- Block



The project demonstrates how configurable policy rules can be used to create a deterministic decision layer around AI-generated content.



\---



\## Introduction



Modern AI systems can generate responses that require different levels of handling depending on their risk category and the confidence associated with the classification.



For example:



\- A high-confidence general response may be allowed.

\- A financial response may require sanitization.

\- A high-confidence medical response may require human review.

\- An unknown risk category may be blocked by default.



This project implements a small policy evaluation engine that makes these decisions using configurable policies rather than hard-coded decision rules.



The engine does not generate or classify the AI response itself.



Instead, it acts as a decision layer that receives:



1\. A risk category

2\. A confidence score

3\. A set of configurable policies



and produces a structured decision.



\### High-level flow



```text

Input

&#x20; |

&#x20; v

Risk Category

&#x20; |

&#x20; v

Match Policies

&#x20; |

&#x20; v

Check Confidence Threshold

&#x20; |

&#x20; v

Select Applicable Policy

&#x20; |

&#x20; v

Determine Action

&#x20; |

&#x20; v

Structured Output





Key Features

1\. Policy-driven evaluation



Policies are stored separately from the Python implementation in:



config/policies.json



This allows policy behavior to be changed without modifying the core Python logic.



2\. Risk-based policy matching



Each input contains a risk category such as:



medical

financial

general

unknown



The engine finds policies associated with the corresponding risk category.



3\. Confidence thresholds



Each policy defines a minimum confidence threshold.



For example:



{

&#x20;   "id": "MED\_STRICT",

&#x20;   "risk": "medical",

&#x20;   "allowed\_actions": \["escalate"],

&#x20;   "min\_confidence": 0.95

}



This policy applies when:



confidence >= 0.95

4\. Multiple actions



The engine supports four actions:



allow

sanitize

escalate

block

5\. Default blocking behavior



If no policy matches an input, or if no matching policy satisfies its confidence threshold, the engine falls back to:



block



This provides a deterministic fallback for unsupported or low-confidence cases.



Project Structure

ai-guardrail-engine/

|

├── src/

│   └── guardrail.py

|

├── config/

│   └── policies.json

|

├── data/

│   └── inputs.json

|

├── tests/

│   └── test\_guardrail.py

|

├── examples/

│   └── output.json

|

├── README.md

├── requirements.txt

├── .gitignore

└── LICENSE

Directory Explanation

src/



Contains the main Python implementation:



src/guardrail.py



This contains the core policy evaluation logic.



config/



Contains policy configuration:



config/policies.json



Policies are kept separate from the application logic so they can be modified independently.



data/



Contains example inputs:



data/inputs.json



Each input contains a risk category and confidence score.



Example:



{

&#x20;   "id": "R1",

&#x20;   "risk": "medical",

&#x20;   "output": "You should take this medicine daily",

&#x20;   "confidence": 0.96

}

tests/



Contains automated tests:



tests/test\_guardrail.py



The tests verify the main decision paths of the engine.



examples/



Contains generated example output:



examples/output.json



This provides a sample of the engine's decisions.



How the Policy Engine Works



The policy evaluation process consists of several steps.



Step 1 — Read the input



The engine extracts the risk category and confidence score.



For example:



risk = medical

confidence = 0.96

Step 2 — Match policies



The engine finds all policies associated with the risk category.



For:



risk = medical



the matching policies are:



MED\_STRICT

MED\_BLOCK

Step 3 — Check confidence thresholds



Each matching policy is evaluated independently.



For:



confidence = 0.96



the engine checks:



MED\_STRICT

0.96 >= 0.95

True



and:



MED\_BLOCK

0.96 >= 0.00

True



Both policies are applicable.



Step 4 — Select the most specific applicable policy



When multiple policies apply, the engine selects the applicable policy with the highest minimum confidence threshold.



Therefore:



MED\_STRICT → 0.95

MED\_BLOCK  → 0.00



results in:



MED\_STRICT



being selected.



Its configured action is:



escalate

Why the Policy Logic Was Changed



The original implementation used an action-priority system:



allow < sanitize < escalate < block



This created a problem when multiple policies matched the same risk category.



For example:



MED\_STRICT

threshold = 0.95

action = escalate



MED\_BLOCK

threshold = 0.00

action = block



For an input with:



confidence = 0.96



both policies matched.



Because block had the highest priority, the original implementation could return:



block



even though the more specific MED\_STRICT policy should produce:



escalate



The policy resolution logic was therefore redesigned.



The new process is:



1\. Match policies by risk

2\. Check each policy's confidence threshold

3\. Ignore policies whose threshold is not satisfied

4\. Collect applicable policies

5\. Select the applicable policy with the highest threshold

6\. Use that policy's action



This makes the policy behavior more meaningful and deterministic.



Supported Actions

Allow



The output is permitted.



decision = allow



The final output is:



null



because the original output can continue through the system.



Sanitize



The output is replaced with a predefined safer message.



decision = sanitize



Example:



This response cannot be shown. Please consult a qualified professional.

Escalate



The output is sent for human review.



decision = escalate



Example:



Sent for human review

Block



The output is prevented from being shown.



decision = block



Example:



Output blocked

Example Decisions



The example input dataset contains several different scenarios.



ID	Risk	Confidence	Decision

R1	medical	0.96	escalate

R2	medical	0.82	block

R3	medical	0.60	block

R4	financial	0.93	sanitize

R5	financial	0.88	allow

R6	financial	0.81	allow

R7	financial	0.65	block

R8	general	0.92	allow

R9	general	0.75	allow

R10	general	0.55	sanitize

R11	general	0.40	sanitize

R12	general	0.20	sanitize

R13	unknown	0.99	block

R14	unknown	0.50	block

R15	unknown	0.10	block



This dataset demonstrates all four supported actions.



Structured Output



The engine generates structured JSON containing the decision and the policies involved.



Example:



{

&#x20;   "id": "R1",

&#x20;   "decision": "escalate",

&#x20;   "applied\_policies": \[

&#x20;       "MED\_STRICT",

&#x20;       "MED\_BLOCK"

&#x20;   ],

&#x20;   "final\_output": "Sent for human review",

&#x20;   "reason": "policy=MED\_STRICT, risk=medical, confidence=0.96"

}



The output contains:



id



Identifies the input being evaluated.



decision



The final action selected by the engine.



Possible values:



allow

sanitize

escalate

block

applied\_policies



Lists the policies whose confidence thresholds were satisfied.



final\_output



Contains the resulting output behavior.



reason



Provides a human-readable explanation of why the decision was selected.



Automated Testing



The project includes an automated test suite using pytest.



The tests cover:



Allow

Sanitize

Escalate

Block

Unknown risk

Low confidence

Multiple matching policies



Run the tests using:



python -m pytest -q



Current test result:



7 passed



The test suite is important because it verifies the policy engine's behavior automatically and helps prevent future changes from breaking the decision logic.



Running the Project



From the project root:



python src/guardrail.py



The program reads:



config/policies.json

data/inputs.json



and generates:



examples/output.json

Running Tests



Install pytest:



python -m pip install pytest



Run:



python -m pytest -q



Expected result:



7 passed

Design Principles

Separation of configuration and logic



Policies are stored in JSON instead of being embedded directly into Python.



This makes policy changes easier to manage.



Deterministic decisions



The same policy configuration and input produce the same decision.



Explicit fallback behavior



Unknown risks and inputs that do not satisfy any policy threshold fall back to:



block

Testable core logic



The main policy processing function can be tested independently:



process\_inputs(...)



This allows the decision engine to be tested without relying only on file-based execution.



Current Limitations



This project is intentionally lightweight and focuses on policy evaluation.



It does not currently implement:



Prompt-injection detection

Jailbreak detection

PII detection

Toxicity classification

Malicious-content classification

LLM inference

Authentication

Distributed execution

Policy versioning

Persistent policy storage



The system assumes that the risk category and confidence score are already available.



Therefore, this project is a policy enforcement and decision layer, not a complete AI safety platform.



Future Improvements



Potential future improvements include:



Policy validation



Validate policy files before execution.



Input validation



Validate required fields and confidence values.



For example:



0.0 <= confidence <= 1.0

Better action semantics



Policies currently contain an allowed\_actions list.



Future versions could define explicit action-selection rules instead of relying on the first configured action when multiple actions are present.



Command-line interface



A CLI could support commands such as:



python -m guardrail evaluate input.json

Continuous Integration



GitHub Actions could automatically:



Install dependencies

Run tests

Validate Python syntax

Check code quality

Report failures on pull requests

Additional tests



Future tests could cover:



Invalid confidence values

Missing fields

Invalid actions

Duplicate policy IDs

Malformed JSON

Empty input

Invalid policy configuration

Technologies Used

Python

JSON

pytest

Git

GitHub

Project Status



The current implementation includes:



Policy-based risk evaluation

Confidence threshold handling

Multiple policy resolution

Allow, sanitize, escalate, and block actions

Default blocking behavior

Structured JSON output

Automated tests

Organized project structure



Test status:



7 tests passed

Author



Ch. Navya Naidu



B.Tech — Computer Science \& Engineering (AI \& ML)

