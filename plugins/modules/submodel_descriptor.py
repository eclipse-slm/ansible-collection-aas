#!/usr/bin/python

# Copyright: (c) 2024, Benjamin Goetz <benjamin.goetz@ipa.fraunhofer.de>
# Apache 2.0
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: submodel_descriptor

short_description: Registers given submodel descriptor at submodel registry 

# If this is part of a collection, you need to use semantic versioning,
# i.e. the version is of the form "2.5.0" and not "2.4".
version_added: "1.0.0"

description: The module registers a given submodel descriptor at a submodel registry

options:
    scheme: 
        description: Scheme of the connection url for the submodel registry
        required: true
        type: str
    host: 
        description: Hostname of the host which runs the submodel registry
        required: true
        type: str
    port: 
        description: Port of the submodel registry
        required: true
        type: str
    state:
        description: Defines if descriptor shall be created or deleted
        required: true
        type: str
    submodel_descriptor:
        description: Submodel Descriptor that shall be registered
        required: true
        type: dict
# Specify this value according to your collection
# in format of namespace.collection.doc_fragment_name
# extends_documentation_fragment:
#     - my_namespace.my_collection.my_doc_fragment_name

author:
    - Benjamin Goetz (@ipa-big)
'''

EXAMPLES = r'''
# Pass in a message
- name: Register Submodel Descriptor
  fabos.aas.submodel_reference:
    scheme: http
    host: localhost
    port: 8080
    state: present
    submodel_descriptor: {{ submodel_descriptor }}
'''

RETURN = r''''''
try:
    from ansible.module_utils.basic import AnsibleModule
except ModuleNotFoundError as e:
    print(e)
    print("Skip import of AnsibleModule (for Testing only)")

import base64
import json
from json import JSONDecodeError

import requests


class SmRegistryClient:
    def __init__(self, url):
        self.url = url

    # region UTILS
    def get_encrypted_id(self, decoded_id: str) -> str:
        return base64.b64encode(bytes(decoded_id, 'utf-8')).decode('ascii')

    def return_response(self, response):
        try:
            return response.status_code, json.loads(response.content)
        except JSONDecodeError:
            return response.status_code, ''
    # endregion

    # region CRUD
    def get_descriptors(self):
        path = '/submodel-descriptors'

        return self.return_response(
            requests.get(
                url=f'{self.url}{path}'
            )
        )

    def get_descriptor(self, submodel_id):
        path = f'/submodel-descriptors/{self.get_encrypted_id(submodel_id)}'

        return self.return_response(
            requests.get(
                url=f'{self.url}{path}'
            )
        )

    def create_descriptor(self, submodel_descriptor):
        path = '/submodel-descriptors'

        return self.return_response(
            requests.post(
                url=f'{self.url}{path}',
                json=submodel_descriptor
            )
        )

    def delete_descriptor(self, submodel_id):
        path = f'/submodel-descriptors/{self.get_encrypted_id(submodel_id)}'

        return self.return_response(
            requests.delete(
                url=f'{self.url}{path}'
            )
        )
    # endregion


def run_module():
    module_args = dict(
        scheme=dict(type='str', choices=['http', 'https'], default='http'),
        host=dict(type='str', required=True),
        port=dict(type='str', default='8081'),
        state=dict(type='str', choices=['present', 'absent'], default='present'),
        submodel_descriptor=dict(type='dict', required=True)
    )

    result = dict(
        changed=False,
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=False
    )

    sm_registry_url = f'{module.params["scheme"]}://{module.params["host"]}:{module.params["port"]}'
    client = SmRegistryClient(sm_registry_url)

    client.create_descriptor(
        submodel_descriptor=module.params['submodel_descriptor']
    )

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
