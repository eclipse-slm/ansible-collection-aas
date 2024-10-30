import unittest

from plugins.modules.convert_to_sm import convert_to_submodel

unittest.TestLoader.sortTestMethodsUsing = None


class UnitTests(unittest.TestCase):
    sm_id = "test_id"

    object_1 = {
        'collection1': {
            'collection2': {
                'collection3': {
                    'collection4': {
                        'key1': "value1"
                    }
                }
            }
        }
    }

    object_2 = {
        'collection_1': {
            'collection_2': {
                'key_3_1': 'value_3_1',
            },
            'key_2_1': 'value_2_1',
            'key_2_2': 'value_2_2'
        },
        'key_1_1': 'value_1_1'
    }

    submodel = convert_to_submodel(sm_id, object_1)
    submodel_elements = submodel['submodelElements']
    submodel_elements_length = len(submodel_elements)

    print(object_1)
    print(submodel)

    submodel = convert_to_submodel(sm_id, object_2)
    submodel_elements = submodel['submodelElements']
    submodel_elements_length = len(submodel_elements)

    print(object_2)
    print(submodel)


if __name__ == '__main__':
    unittest.main()
