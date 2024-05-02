import unittest

from plugins.modules.convert_to_sm import convert_to_submodel


class UnitTests(unittest.TestCase):
    sm_id = "test_id"

    object = {
        'list1': [
            {
                'key1': "1",
                'key2': 2,
                'key3': 3.1,
                'key4': False
            },
            {
                'key1': "1",
                'key2': 2,
                'key3': 3.1,
                'key4': False
            },
        ],
    }

    submodel = convert_to_submodel(sm_id, object)
    submodel_elements = submodel['submodelElements']
    submodel_elements_length = len(submodel_elements)
    submodel_element = submodel_elements[0]

    expected = {
        'length': len(object),
        'modelType': 'SubmodelElementList',
    }

    print(object)
    print(submodel)

    def test_length_of_submodel_elements(self):
        self.assertEqual(
            self.submodel_elements_length,
            self.expected['length']
        )

    def test_model_type_of_submodel_element(self):
        self.assertEqual(
            self.submodel_element['modelType'],
            self.expected['modelType']
        )

    def test_list_element_length(self):
        for index, le in enumerate(self.object['list1']):
            smecv = self.submodel_element['value'][index]['value']
            self.assertEqual(
                len(smecv),
                len(le)
            )


if __name__ == '__main__':
    unittest.main()
