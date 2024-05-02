import json
import logging
import os
import sys
import unittest

from plugins.modules.convert_to_sm import convert_to_submodel

logger = logging.getLogger()
logger.level = logging.INFO
stream_handler = logging.StreamHandler(sys.stdout)


class UnitTests(unittest.TestCase):
    sm_id = "test_id"
    facts_abs_file_path = os.path.join(
        os.path.dirname(__file__),
        'resources/facts.json'
    )

    with open(facts_abs_file_path) as fp:
        facts = json.load(fp)

    # SETUP / TEAR DOWN:
    def setUp(self):
        logger.addHandler(stream_handler)

    def tearDown(self):
        logger.removeHandler(stream_handler)

    # TESTS:
    def test_convert_ansible_facts(self):
        facts_as_sm = convert_to_submodel(self.sm_id, self.facts)

        # print(self.facts)
        # print()
        # print(facts_as_sm)
        # with open('resources/facts_as_sm.json', 'w') as fp:
        #     json.dump(facts_as_sm, fp, indent=2)

        length_facts = len(self.facts)
        length_facts_as_sm = len(facts_as_sm['submodelElements'])

        self.assertEqual(length_facts, length_facts_as_sm)


if __name__ == '__main__':
    unittest.main()
