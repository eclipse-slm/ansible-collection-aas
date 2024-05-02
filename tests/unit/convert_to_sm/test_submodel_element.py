import unittest

from plugins.module_utils.convert import convert_to_submodel


class UnitTests(unittest.TestCase):
    sm_id = "test_id"

    object = {
        'key1': 'value1',
        'key2': 1,
        'key3': 5.7,
        'key4': True
    }

    expected = {
        'length': len(object),
        "value_type": ["xs:string", "xs:integer", "xs:float", "xs:boolean"],
    }

    submodel = convert_to_submodel(sm_id, object)
    submodel_elements = submodel['submodelElements']

    def test_count_of_submodel_elements(self):
        actual = len(self.submodel_elements)
        expected = self.expected['length']

        # Check Count
        self.assertEqual(
            actual,
            expected,
            'Submodel Count does not match expected length'
        )

    def test_id_short_of_submodel_elements(self):
        self.submodel_elements

        # Assert one submodel element with expected idShort is in list of submodel elements
        for expected in self.object:
            self.assertTrue(
                any(se['idShort'] == expected for se in self.submodel_elements),
                f'List of submodel elements does not contain a submodel with idShort == "{expected}"'
            )

    def test_value_type_of_submodel_elements(self):
        for index, o in enumerate(self.object):
            expected = self.expected['value_type'][index]

            # Assert value_type
            self.assertTrue(
                any(se['valueType'] == expected for se in self.submodel_elements),
                f'No submodel element has a value type == "{expected}"'
            )

    def test_value_of_submodel_elements(self):
        for o in self.object:
            expected = str(self.object[o]).lower()

            # Assert value
            self.assertTrue(
                any(se['value'] == expected for se in self.submodel_elements),
                f'No submodel element has expected value ==  "{expected}"'
            )


if __name__ == '__main__':
    unittest.main()
