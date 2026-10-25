import unittest
from agents.adaptive_factory import (
    classify_task, draft_agent_spec, recommend_agent_profile, recommend_execution
)


class AdaptiveFactoryTests(unittest.TestCase):
    def test_classifies_text_and_reasoning_tasks(self):
        self.assertEqual(classify_task('Summarize this article'), 'text')
        self.assertEqual(classify_task('Do a deep analysis and plan a strategy'), 'reasoning')

    def test_deterministic_work_does_not_need_a_model(self):
        result = recommend_execution('validate JSON', {'free_ram_gb': 1, 'free_vram_gb': 0})
        self.assertEqual(result['route'], 'deterministic_local')
        self.assertFalse(result['execution_performed'])

    def test_small_local_profile_is_candidate_not_verified(self):
        result = recommend_execution('summarize a document', {
            'free_ram_gb': 6, 'free_vram_gb': 0, 'local_runtime_available': True
        })
        self.assertEqual(result['route'], 'local_model_small_candidate')
        self.assertEqual(result['status'], 'candidate_not_verified')
        self.assertFalse(result['execution_performed'])

    def test_no_runtime_does_not_claim_model_is_running(self):
        result = recommend_execution('write code for a script', {
            'free_ram_gb': 32, 'free_vram_gb': 12, 'local_runtime_available': False
        })
        self.assertEqual(result['status'], 'needs_local_runtime_or_review')

    def test_remote_route_is_only_a_candidate_and_needs_approval(self):
        result = recommend_execution('summarize a document', {
            'free_ram_gb': 1, 'free_vram_gb': 0, 'internet_available': True
        }, allow_remote=True)
        self.assertEqual(result['status'], 'approval_and_configuration_required')
        self.assertFalse(result['remote_used'])

    def test_vision_is_blocked_without_specialist_configuration(self):
        result = recommend_execution('analyze this image', {'free_ram_gb': 16, 'free_vram_gb': 8})
        self.assertEqual(result['status'], 'blocked_unconfigured')

    def test_invalid_device_memory_is_rejected(self):
        with self.assertRaises(ValueError):
            recommend_execution('summarize this', {'free_ram_gb': -2})

    def test_non_finite_device_memory_is_rejected(self):
        for value in (float('nan'), float('inf'), float('-inf')):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    recommend_execution('summarize this', {'free_ram_gb': value})

    def test_agent_spec_is_draft_only_and_denies_external_actions(self):
        spec = draft_agent_spec('Cafe Content Helper', 'Draft social content', ['caption', 'calendar'])
        self.assertEqual(spec['agent_id'], 'draft-cafe-content-helper')
        self.assertEqual(spec['status'], 'draft_requires_evaluation')
        self.assertFalse(spec['permissions']['public_publish'])
        self.assertFalse(spec['execution_performed'])

    def test_agent_factory_rejects_unapproved_tools(self):
        with self.assertRaises(ValueError):
            draft_agent_spec('unsafe', 'Do things', ['research'], ['send_email'])

    def test_factory_uses_versioned_router_and_keeps_uninstalled_profile_setup_only(self):
        result = recommend_agent_profile('summarization', {'ram_gb': 12, 'vram_gb': 0})
        self.assertEqual(result['factory_version'], '0.2.1')
        self.assertEqual(result['selected_profile'], 'local-llm-small-q4')
        self.assertEqual(result['route_status'], 'setup_required')
        self.assertFalse(result['execution_ready'])
        self.assertFalse(result['execution_performed'])
        self.assertFalse(result['remote_called'])

    def test_factory_selects_only_explicitly_verified_installed_profile(self):
        result = recommend_agent_profile(
            'summarization',
            {'ram_gb': 12, 'vram_gb': 0},
            installed_profiles={'rules-engine', 'local-llm-small-q4'},
        )
        self.assertEqual(result['selected_profile'], 'local-llm-small-q4')
        self.assertEqual(result['route_status'], 'ready')
        self.assertTrue(result['execution_ready'])
        self.assertFalse(result['execution_performed'])

    def test_factory_rejects_unknown_profile_task_without_remote_execution(self):
        result = recommend_agent_profile(
            'image_generation',
            {'ram_gb': 32, 'vram_gb': 16},
            installed_profiles={'rules-engine'},
            allow_remote=True,
        )
        self.assertEqual(result['route_status'], 'unsupported')
        self.assertFalse(result['execution_performed'])
        self.assertFalse(result['remote_called'])


    def test_factory_normalizes_classifier_text_category_to_supported_catalog_task(self):
        result = recommend_agent_profile('text', {'ram_gb': 12, 'vram_gb': 0})
        self.assertEqual(result['requested_task_type'], 'text')
        self.assertEqual(result['task_type'], 'summarization')
        self.assertEqual(result['selected_profile'], 'local-llm-small-q4')
        self.assertEqual(result['route_status'], 'setup_required')
        self.assertFalse(result['execution_ready'])

    def test_factory_normalizes_code_alias_but_does_not_guess_unknown_tasks(self):
        code = recommend_agent_profile('code', {'ram_gb': 16, 'vram_gb': 8})
        self.assertEqual(code['task_type'], 'coding')
        unknown = recommend_agent_profile('general', {'ram_gb': 32, 'vram_gb': 16})
        self.assertEqual(unknown['route_status'], 'unsupported')
        self.assertFalse(unknown['execution_ready'])


    def test_classification_falls_back_to_verified_local_llm_when_rules_engine_unavailable(self):
        result = recommend_agent_profile(
            'classification',
            {'ram_gb': 12, 'vram_gb': 0},
            installed_profiles={'local-llm-small-q4'},
        )
        self.assertEqual(result['task_type'], 'simple_classification')
        self.assertEqual(result['selected_profile'], 'local-llm-small-q4')
        self.assertEqual(result['route_status'], 'ready')
        self.assertTrue(result['execution_ready'])
        self.assertFalse(result['execution_performed'])
        self.assertFalse(result['remote_called'])

if __name__ == '__main__':
    unittest.main()
