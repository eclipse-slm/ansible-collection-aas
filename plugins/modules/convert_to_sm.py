#!/usr/bin/python
import inspect
import json
import logging
import re

import basyx
from basyx.aas import model
from basyx.aas.adapter.json import AASToJsonEncoder
from basyx.aas.model import Property
from basyx.aas.model.datatypes import String

# Copyright: (c) 2018, Terry Jones <terry.jones@example.org>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r'''
---
module: convert_to_sm

short_description: This is my test module

# If this is part of a collection, you need to use semantic versioning,
# i.e. the version is of the form "2.5.0" and not "2.4".
version_added: "1.0.0"

description: This is my longer description explaining my test module.

options:
    name:
        description: This is the message to send to the test module.
        required: true
        type: str
    new:
        description:
            - Control to demo if the result of this module is changed or not.
            - Parameter description can be a list as well.
        required: false
        type: bool
# Specify this value according to your collection
# in format of namespace.collection.doc_fragment_name
# extends_documentation_fragment:
#     - my_namespace.my_collection.my_doc_fragment_name

author:
    - Your Name (@yourGitHubHandle)
'''

EXAMPLES = r'''
# Pass in a message
- name: Test with a message
  my_namespace.my_collection.my_test:
    name: hello world

# pass in a message and have changed true
- name: Test with a message and changed output
  my_namespace.my_collection.my_test:
    name: hello world
    new: true

# fail the module
- name: Test failure of the module
  my_namespace.my_collection.my_test:
    name: fail me
'''

RETURN = r'''
# These are examples of possible return values, and in general should use other names for return values.
original_message:
    description: The original name param that was passed in.
    type: str
    returned: always
    sample: 'hello world'
message:
    description: The output message that the test module generates.
    type: str
    returned: always
    sample: 'goodbye'
'''
__metaclass__ = type

from __future__ import (absolute_import, division, print_function)
from ansible.module_utils.basic import AnsibleModule

logger = logging.getLogger(__name__)


def get_id_short(id_short, level_key=''):
    if id_short is None:
        return id_short

    if level_key is None:
        level_key = ''

    no_special_chars = re.sub('[^a-zA-Z0-9_]', '', id_short)
    no_letter_at_start_pattern = re.compile('^[^a-zA-Z].*$')

    # if id short has no letter as first char and level_key is defined:
    if no_letter_at_start_pattern.match(no_special_chars) and len(level_key) > 0:
        # append level key to idshort
        return f'{level_key}_{no_special_chars}'
    else:
        # replace all chars not being a letter:
        return re.sub(r'^[^a-zA-Z]*', '', no_special_chars)


class PropertySetElement(Property):
    def __key(self):
        return self.id_short

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        return self.__key() == other.__key()

    def get_property(self):
        return Property(
            id_short=self.id_short,
            value=self.value,
            value_type=self.value_type
        )


def process_dict(element_key, element_value):
    logger.debug(f'{inspect.stack()[0][3]}: {element_key}, {element_value}')
    smece = process_level(element_value, element_key)
    return model.SubmodelElementCollection(
        id_short=element_key,
        value=smece
    )


def process_list(element_key, element_value):
    logger.debug(f'{inspect.stack()[0][3]}: {element_key}, {element_value}')
    smele = list(process_level(element_value, element_key))

    if len(smele) > 0:
        if isinstance(smele[0], model.SubmodelElementCollection):
            return model.SubmodelElementList(
                id_short=element_key,
                value=smele,
                type_value_list_element=type(smele[0])
            )
        else:
            return model.SubmodelElementList(
                id_short=element_key,
                value=smele,
                type_value_list_element=type(smele[0]),
                value_type_list_element=smele[0].value_type
            )
    else:
        return model.SubmodelElementList(
            id_short=element_key,
            value=smele,
            type_value_list_element=Property,
            value_type_list_element=String
        )


def process_property(key, value, level_key) -> PropertySetElement:
    logger.debug(f'{inspect.stack()[0][3]}: {key}, {value}')
    try:
        if isinstance(value, bool):
            value_type = basyx.aas.model.datatypes.Boolean
        elif isinstance(value, int):
            value_type = basyx.aas.model.datatypes.Integer
        elif isinstance(value, float):
            value_type = basyx.aas.model.datatypes.Float
        else:
            value_type = basyx.aas.model.datatypes.String

        id_short = get_id_short(key, level_key)

        if id_short == '':
            return None

        prop = PropertySetElement(
            id_short=id_short,
            value_type=value_type,
            value=value
        )

        return prop
    except basyx.aas.model.base.AASConstraintViolation as e:
        print(e)


def process_level_element(element_key, element_value, level_key):
    logger.debug(f'{inspect.stack()[0][3]}: {element_key}, {element_value}')
    if isinstance(element_value, dict):
        return process_dict(element_key, element_value)
    elif isinstance(element_value, list):
        return process_list(element_key, element_value)
    else:
        try:
            return process_property(element_key, element_value, level_key)
        except AttributeError as e:
            print(e)


def process_level(level_elements, level_key):
    submodel_elements = set()
    return_submodel_elements = []

    # Process Lists:
    if isinstance(level_elements, list):
        for index, element_value in enumerate(level_elements):
            element_key = None
            submodel_element = process_level_element(element_key, element_value, level_key)
            if submodel_element is not None:
                submodel_elements.add(submodel_element)
    # Process Properties / Dicts:
    else:
        for element_key in level_elements:
            element_value = level_elements[element_key]
            submodel_element = process_level_element(element_key, element_value, level_key)
            if submodel_element is not None:
                submodel_elements.add(submodel_element)

    # Convert PropertySetElement to Property:
    for submodel_element in submodel_elements:
        if isinstance(submodel_element, PropertySetElement):
            return_submodel_elements.append(submodel_element.get_property())
        else:
            return_submodel_elements.append(submodel_element)

    return return_submodel_elements


def convert_to_submodel(sm_id, dictionary):
    submodel = model.Submodel(sm_id)
    submodel.submodel_element = process_level(dictionary, "")

    return json.loads(
        json.dumps(submodel, cls=AASToJsonEncoder)
    )


def run_module():
    module_args = dict(
        facts=dict(type='dict', required=True)
    )

    result = dict(
        changed=False,
        submodel=dict()
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=False
    )

    result['submodel'] = convert_to_submodel(module.params['facts'])

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
