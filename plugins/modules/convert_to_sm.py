#!/usr/bin/python

# Copyright: (c) 2024, Benjamin Goetz <benjamin.goetz@ipa.fraunhofer.de>
# Apache 2.0
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from email.policy import default

DOCUMENTATION = r'''
---
module: convert_to_sm

short_description: Converts facts to submodel 

# If this is part of a collection, you need to use semantic versioning,
# i.e. the version is of the form "2.5.0" and not "2.4".
version_added: "1.0.0"

description: The module consumes facts and converts them into an AAS-compatible (Asset Administration Shell) submodel.

options:
    facts:
        description: Facts that shall be converted into a submodel
        required: true
        type: dict
    id:
        description: The id the submodel shall have
        required: true
        type: str
    parent:
        description: The parent id 
        required: false
        type: str
    semantic:
        description: Add a ConceptDescription to the submodel
        required: true
        type: str
# Specify this value according to your collection
# in format of namespace.collection.doc_fragment_name
# extends_documentation_fragment:
#     - my_namespace.my_collection.my_doc_fragment_name

author:
    - Benjamin Goetz (@ipa-big)
'''

EXAMPLES = r'''
# Pass in a message
- setup:

- name: Convert ansible facts to submodel
  fabos.aas.convert_to_sm:
    facts: {{ ansible_facts }}
    id: submodel_id
'''

RETURN = r'''
# These are examples of possible return values, and in general should use other names for return values.
submodel:
    description: The submodel derived from 'facts' argument.
    type: dict
    returned: always
    sample: 'hello world'
'''
try:
    from ansible.module_utils.basic import AnsibleModule
except ModuleNotFoundError as e:
    print(e)
    print("Skip import of AnsibleModule (for Testing only)")

import inspect
import json
import logging
import re

import basyx
from basyx.aas import model
from basyx.aas.adapter.json import AASToJsonEncoder
from basyx.aas.model import Property, AASConstraintViolation
from basyx.aas.model.datatypes import String

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
    element_key = get_id_short(element_key)
    return model.SubmodelElementCollection(
        id_short=element_key,
        value=smece
    )


def convert_submodel_elements_to_string(submodel_elements):
    casted_submodel_elements = []
    for se in submodel_elements:
        casted_submodel_elements.append(
            process_property(None, str(se.value), '').get_property()
        )

    return casted_submodel_elements


def create_submodel_element_list(id_short, submodel_elements):
    try:
        submodel_element_list = model.SubmodelElementList(
            id_short=id_short,
            value=submodel_elements,
            type_value_list_element=type(submodel_elements[0]),
            value_type_list_element=submodel_elements[0].value_type
        )
    except AASConstraintViolation as e:
        if e.constraint_id == 109:
            smele = convert_submodel_elements_to_string(submodel_elements)
            submodel_element_list = model.SubmodelElementList(
                id_short=id_short,
                value=smele,
                type_value_list_element=type(smele[0]),
                value_type_list_element=smele[0].value_type
            )
        else:
            raise e

    return submodel_element_list


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
            return create_submodel_element_list(
                id_short=element_key,
                submodel_elements=smele
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
            level_element = process_level_element(element_key, element_value, level_key)
            if level_element is not None:
                if isinstance(level_element, PropertySetElement):
                    submodel_element = level_element.get_property()
                else:
                    submodel_element = level_element
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


def convert_to_submodel(sm_id, dictionary, parent=None, semantic=None):
    submodel = model.Submodel(sm_id)

    if parent is not None:
        submodel.parent = model.ExternalReference(
            (model.Key(
                type_=model.KeyTypes.ASSET_ADMINISTRATION_SHELL,
                value=parent
            ),)
        )

    if semantic is not None:
        submodel.semantic_id = model.ExternalReference(
            (model.Key(
                type_=model.KeyTypes.CONCEPT_DESCRIPTION,
                value=semantic
            ),)
        )

    submodel.submodel_element = process_level(dictionary, "")

    return json.loads(
        json.dumps(submodel, cls=AASToJsonEncoder)
    )


def run_module():
    module_args = dict(
        id=dict(type='str', required=True),
        facts=dict(type='dict', required=True),
        parent=dict(type='str', default=None),
        semantic=dict(type='str', default=None),
    )

    result = dict(
        changed=False,
        submodel=dict()
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=False
    )

    result['submodel'] = convert_to_submodel(
        module.params['id'],
        module.params['facts'],
        module.params['parent'],
        module.params['semantic']
    )

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
