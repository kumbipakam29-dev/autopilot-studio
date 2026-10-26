# AutoPilot Studio — Evidence-Based Quality Learning Loop

**Status:** v1 framework proposed for review. This is not a connected media generator and does not fine-tune model weights.

## Principle

Inspired by Bhagavad Gita 2.47: work diligently, learn from evidence, and do not treat desired results as proof that the work succeeded. Agent names are symbolic company role labels. Reference: https://vedabase.io/en/library/bg/2/47/

## Workflow

1. Plan the task, domain, brief, target dimensions/duration and golden test suite version.
2. Generate a candidate using an explicitly configured adapter. No provider/model is silently chosen.
3. Inspect with real tool outputs and/or independent reviewer evidence. Missing checks score zero.
4. Score on weighted rubric. Pass needs 85/100 overall AND every hard gate >=90/100.
5. Feed failed check IDs and specific remediation to the next attempt.
6. Retry up to three times by default; absolute cap is five. Repeated failure becomes a stopped/escalated task, never a fake success.
7. Keep prior failures and turn recurring failures into regression tests.
8. Compare exact model versions over the same golden cases. At least five distinct cases are required for review. Recommend, but never promote automatically.
9. Passing QA does not permit public publishing, spending, account changes, outreach or payment claims. Those remain separate approval gates.

## Domain checklists

- Video / Drishti-Video: frame_bounds, text_legibility, story_and_pacing, audio_sync, duration_valid, export_playable, rights_cleared, human_review.
- Music / Svara-Music: export_playable, no_clipping, loudness_consistent, arrangement_quality, mix_balance, rights_cleared, human_review.
- Image / Chitrakara-Image: dimensions_valid, no_text_overflow, brief_match, composition_quality, text_legibility, rights_cleared, human_review.
- Website / Vishwakarma-Web: responsive_layout, no_overflow, links_valid, forms_verified_or_absent, accessibility_basics, content_accuracy, browser_test, human_review.

All scores are 0–100. Hard-gate failure blocks delivery even if the total score is high. The human_review field must not be completed by a model's self-assertion. For visual checks, inspect actual rendered pixels/screenshots, not just a prompt. For music, inspect exported audio and measurements, then listen. For websites, use browser tests and screenshots. A form can pass only when it is demonstrably functional or deliberately removed/documented absent.

## Run

~~~bash
python -m unittest discover -s tests -p 'test_*.py' -v
python runtime/quality_loop.py --demo
~~~

The demo uses synthetic fixture data: its first video attempt fails layout checks, then a second fixture passes after feedback. It does not generate video or call a real model.

A connected adapter should implement generator(context) -> artifact report and call:

~~~python
from runtime.quality_loop import run_learning_loop

result = run_learning_loop(
    task_id="unique-task-id",
    domain="video",  # video | music | image | website
    generator=your_configured_generator_adapter,
    max_attempts=3,
    history_path="runtime/quality-runs.jsonl",
)
~~~

The report should include actual check scores, artifact_ref, agent_id/version and model_id/version. Keep secrets and unnecessary personal data out of logs. Use measured browser/media evidence and independent reviewer scores.

For model comparison, use compare_model_candidates(records, min_cases=5), with one record per unique golden case. The system reports scores, pass rates, case counts and review recommendations; it never automatically activates a version. Compare safety, correctness and latency/cost as well as quality before approval.

## Registry and present limitations

- agents/quality_registry.json stores symbolic role names, versioning policy and a candidate-model template. The existing task router registry is not silently rewritten.
- The retry/scoring framework, remediation feedback, JSONL history option, candidate-version comparator, and tests are included in this branch.
- No model provider, video/image renderer, audio-analysis tool or browser automation adapter is connected here. So this change itself has not produced or inspected real media and has not trained a model.
- Never lower the passing bar, erase failures, train on customer data without permission, or promote on one lucky output.
