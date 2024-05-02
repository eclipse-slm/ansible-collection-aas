import unittest

from plugins.modules.convert_to_sm import convert_to_submodel

unittest.TestLoader.sortTestMethodsUsing = None


class UnitTests(unittest.TestCase):
    sm_id = "test_id"

    object = {
        'collection1': {
            'key1': "1",
            'key2': "2",
            'key3': "3"
        },
        'collection2': {
            'key1': 1,
            'key2': 2,
            'key3': 3
        },
        'collection3': {
            'key1': 1.4,
            'key2': 2.7,
            'key3': 3.1
        },
        'collection4': {
            'key1': True,
            'key2': False,
            'key3': False
        },
        'collection5': {}
    }

    submodel = convert_to_submodel(sm_id, object)
    submodel_elements = submodel['submodelElements']
    submodel_elements_length = len(submodel_elements)

    expected = {
        'length': len(object),
        'model_type': 'SubmodelElementCollection',
        'id_short': list(object.keys())[0],
        'type_value': 'Property',
        'collections': {
            'collection1': {
                'length_list': len(object['collection1']),
                'value_type': 'xs:string'
            },
            'collection2': {
                'length_list': len(object['collection2']),
                'value_type': 'xs:integer'
            },
            'collection3': {
                'length_list': len(object['collection3']),
                'value_type': 'xs:float'
            },
            'collection4': {
                'length_list': len(object['collection4']),
                'value_type': 'xs:boolean'
            },
            'collection5': {
                'length_list': len(object['collection5']),
                'value_type': 'xs:string'
            }
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

    def test_submodel_element_collection_length(self):
        for se in self.submodel_elements:
            key = se['idShort']

            try:
                self.assertEqual(
                    len(se['value']),
                    self.expected['collections'][key]['length_list']
                )
            except KeyError as ke:
                if self.expected['collections'][key]['length_list'] > 0:
                    raise ke

    def test_submodel_element_collection_values(self):
        for se in self.submodel_elements:
            key = se['idShort']

            try:
                for sec in se['value']:
                    self.assertEqual(
                        sec['value'],
                        str(self.object[key][sec['idShort']]).lower()
                    )
            except KeyError as ke:
                if self.expected['collections'][key]['length_list'] > 0:
                    raise ke

    def test_submodel_element_collection_value_types(self):
        for se in self.submodel_elements:
            key = se['idShort']

            try:
                for sec in se['value']:
                    self.assertEqual(
                        sec['valueType'],
                        self.expected['collections'][key]['value_type']
                    )
            except KeyError as ke:
                if self.expected['collections'][key]['length_list'] > 0:
                    raise ke


if __name__ == '__main__':
    unittest.main()
