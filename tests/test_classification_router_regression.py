import unittest
from pathlib import Path
from agents.integrated_agent_router import build_agent_package


class ClassificationRouterRegressionTests(unittest.TestCase):
    def test_classify_text_maps_to_supported_catalog_task(self):
        catalog = Path(__file__).resolve().parents[1] / 'agents' / 'model_profiles.json'
        package = build_agent_package(
            'Classifier', 'Classify text', ['classification'], 'classify text',
            {'ram_gb': 2}, {'rules-engine'}, catalog_path=catalog,
        )
        self.assertEqual(package['model_route']['task_type'], 'simple_classification')
        self.assertEqual(package['model_route']['route_status'], 'ready')
        self.assertFalse(package['execution_performed'])
        self.assertFalse(package['external_actions_performed'])


if __name__ == '__main__':
    unittest.main()
