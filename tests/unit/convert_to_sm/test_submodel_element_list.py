import unittest

from plugins.modules.convert_to_sm import convert_to_submodel


class UnitTests(unittest.TestCase):
    sm_id = "test_id"

    object = {
        'list1': ["1", "2", "3"],
        'list2': [1, 2, 3],
        'list3': [1.3, 2.5, 3.1],
        'list4': [True, False, False],
        'list5': [],
    }

    submodel = convert_to_submodel(sm_id, object)
    submodel_elements = submodel['submodelElements']
    submodel_elements_length = len(submodel_elements)

    expected = {
        'length': len(object),
        'model_type': 'SubmodelElementList',
        'id_short': list(object.keys())[0],
        'type_value': 'Property',
        'lists': {
            'list1': {
                'length_list': len(object['list1']),
                'value_type': 'xs:string'
            },
            'list2': {
                'length_list': len(object['list2']),
                'value_type': 'xs:integer'
            },
            'list3': {
                'length_list': len(object['list3']),
                'value_type': 'xs:float'
            },
            'list4': {
                'length_list': len(object['list4']),
                'value_type': 'xs:boolean'
            },
            'list5': {
                'length_list': len(object['list5']),
                'value_type': 'xs:string'
            },
        }
    }

    print(object)
    print(submodel)

    def test_submodel_elements_length(self):
        # Check Submodel Element Length
        self.assertEqual(
            self.submodel_elements_length,
            self.expected['length']
        )

    def test_submodel_element_type(self):
        # Check Submodel Model Type
        for se in self.submodel_elements:
            self.assertEqual(
                se['modelType'],
                self.expected['model_type']
            )

    def test_submodel_element_list_length(self):
        for se in self.submodel_elements:
            key = se['idShort']

            try:
                actual = len(se['value'])
                expected = self.expected['lists'][key]['length_list']

                self.assertEqual(
                    actual,
                    expected
                )
            except KeyError as ke:
                if self.expected['lists'][key]['length_list'] > 0:
                    raise ke

    def test_submodel_element_list_type_value(self):
        for se in self.submodel_elements:
            self.assertEqual(
                se['typeValueListElement'],
                self.expected['type_value']
            )

    def test_submodel_element_list_value_type(self):
        for se in self.submodel_elements:
            key = se['idShort']
            self.assertEqual(
                se['valueTypeListElement'],
                self.expected['lists'][key]['value_type']
            )

    def test_submodel_element_list_values(self):
        for se in self.submodel_elements:
            key = se['idShort']

            try:
                for expected in self.object[key]:
                    self.assertTrue(
                        any(value_element['value'] == str(expected).lower() for value_element in se['value'])
                    )
            except KeyError as ke:
                if self.expected['lists'][key]['length_list'] > 0:
                    raise ke

    def test_submodel_element_list_element_value_types(self):
        for se in self.submodel_elements:
            key = se['idShort']

            try:
                for index, elm in enumerate(se['value']):
                    self.assertEqual(
                        elm['valueType'],
                        str(self.expected['lists'][key]['value_type'])
                    )
            except KeyError as ke:
                if self.expected['lists'][key]['length_list'] > 0:
                    raise ke

    def test_submodel_element_list_element_model_type(self):
        for se in self.submodel_elements:
            key = se['idShort']

            try:
                for index, elm in enumerate(se['value']):
                    self.assertEqual(
                        elm['modelType'],
                        str(self.expected['type_value'])
                    )
            except KeyError as ke:
                if self.expected['lists'][key]['length_list'] > 0:
                    raise ke


if __name__ == '__main__':
    unittest.main()
