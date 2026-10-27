# Market Research Specialist: supervised learning-cycle example

This is a reproducible *offline example* for the local-business niche researcher capability. It does not browse, fetch live listings, or verify a real prospect. Use only facts already collected from an official public source and record the source URL and check date separately.

## One-task workflow

1. Supply a business category, location, and a short list of already-reviewed facts to `APS-CR-01` (the local business niche researcher).
2. Treat its content angles as hypotheses, not factual claims about the business.
3. Prepare a baseline draft and a proposed candidate draft. Record the exact reviewer rubric scores for each; do not have the runner invent review scores.
4. Run the same fixed offline regression fixtures against both outputs. A passing fixture means only that the specified test passed.
5. Use `agents.learning_cycle.run_learning_cycle` to produce the comparison record.
6. Review the record and decide manually whether to make a separate code/prompt change. The helper never edits its own code, trains model weights, or releases a candidate.

## Example supplied input

```json
{
  "business_type": "interior design studio",
  "location": "Ahmedabad",
  "facts": [
    "Official website describes residential interior design services",
    "Official contact page lists a business enquiry email"
  ],
  "services": ["residential interiors"]
}
```

These facts are illustrative sample input only. Replace them with accurately checked, dated evidence before using this for a real business.

## Expected safe interpretation

- The capability may return general content-angle hypotheses such as customer FAQs, process explainers, or behind-the-scenes concepts.
- It cannot prove that the business is active, wants marketing help, has weak social content, or will pay.
- Prospect qualification needs source verification, a relevant offer hypothesis, and a human review.
- No outreach is sent and no post is published by this example.
- If the candidate's reviewed score is lower than baseline, or any regression test fails, the candidate is rejected even if someone set the approval flag.
- A better score only makes a candidate eligible for human consideration; it does not auto-merge or auto-release.

## Local test command

From the repository root:

```bash
python -m unittest discover -s tests -v
```

The command has been documented here, but the latest GitHub Actions run is not yet verified in this report.
