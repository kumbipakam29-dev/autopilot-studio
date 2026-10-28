# Training Loop: Generate and Import Evidence

This workflow uses the repository's Python evaluator. It is supervised evaluation, not model-weight training.

## Input JSON shape

Create a JSON file with:
- `task_id`
- `baseline_output` and `candidate_output`
- `baseline_review` and `candidate_review`, each containing reviewer-provided scores for `task_success`, `evidence_and_factuality`, `safety_and_permissions`, `format_and_completeness`, and `reproducibility` (each 0–100), and optional `hard_fail_flags`
- `regression_results`, a non-empty object mapping named tests to true/false
- `change_rationale`
- optional `reviewer_approved` (defaults false), `agent_name`, `error_category`, `evidence_notes`

## Run the Python evaluation

```bash
python -m agents.learning_cycle_cli --input cycle.json --output evidence.json
```

The resulting `evidence.json` includes baseline/candidate scores, delta, regression decision, approval status and explicit limitations. It does not train model weights, edit code, call the network or release anything.

## Import into Android dashboard

Open **Training Loop**, choose **Import a real Python learning-cycle JSON record**, and select `evidence.json`. The result is stored in browser local storage on that device and can be exported as a JSON log. It is not synced to a server.

## Evidence standards

Scores must be backed by actual outputs and the same benchmark inputs. Synthetic fixtures only verify the evaluator code and must not be represented as results from a real agent or client task. A higher score is not proof of learning unless the benchmark, scoring criteria and source outputs are independently recorded. Human approval is recorded separately and never deploys code automatically.
