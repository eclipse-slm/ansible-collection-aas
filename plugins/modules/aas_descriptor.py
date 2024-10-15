#!/usr/bin/python

# Copyright: (c) 2024, Benjamin Goetz <benjamin.goetz@ipa.fraunhofer.de>
# Apache 2.0
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: aas_descriptor

short_description: Registers given shell descriptor at shell registry 

# If this is part of a collection, you need to use semantic versioning,
# i.e. the version is of the form "2.5.0" and not "2.4".
version_added: "1.0.0"

description: The module registers a given shell descriptor at a shell registry

options:
    scheme: 
        description: Scheme of the connection url for the shell registry
        required: true
        type: str
    host: 
        description: Hostname of the host which runs the shell registry
        required: true
        type: str
    port: 
        description: Port of the shell registry
        required: true
        type: str
    state:
        description: Defines if descriptor shall be created or deleted
        required: true
        type: str
    aas_descriptor:
        description: shell Descriptor that shall be registered
        type: dict
    shell_id:
        description: shell id when descriptor shall be deleted
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
- name: Register shell Descriptor
  slm.aas.shell_reference:
    scheme: http
    host: localhost
    port: 8080
    state: present
    aas_descriptor: {{ aas_descriptor }}
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
        path = '/shell-descriptors'

        return self.return_response(
            requests.get(
                url=f'{self.url}{path}'
            )
        )

    def get_descriptor(self, shell_id):
        path = f'/shell-descriptors/{self.get_encrypted_id(shell_id)}'

        return self.return_response(
            requests.get(
                url=f'{self.url}{path}'
            )
        )

    def create_descriptor(self, aas_descriptor):
        path = '/shell-descriptors'

        return self.return_response(
            requests.post(
                url=f'{self.url}{path}',
                json=aas_descriptor
            )
        )

    def delete_descriptor(self, shell_id):
        path = f'/shell-descriptors/{self.get_encrypted_id(shell_id)}'

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
        port=dict(type='str', default='8082'),
        state=dict(type='str', choices=['present', 'absent'], default='present'),
        shell_id=dict(type='str'),
        aas_descriptor=dict(type='dict')
    )

    result = dict(
        changed=False,
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=False,
        required_if=[('state', 'present', ['aas_descriptor']), ('state', 'absent', ['shell_id'])],
    )

    sm_registry_url = f'{module.params["scheme"]}://{module.params["host"]}:{module.params["port"]}'
    client = SmRegistryClient(sm_registry_url)

    try:
        if module.params['state'] == 'present':
            status_code, content = client.create_descriptor(
                aas_descriptor=module.params['aas_descriptor']
            )
            if status_code == 201:
                result['changed'] = True
        else:
            client.delete_descriptor(module.params['shell_id'])
    except requests.exceptions.ConnectionError as e:
        module.fail_json(msg=f'Failed to connect to {sm_registry_url}. {e}', **result)

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
