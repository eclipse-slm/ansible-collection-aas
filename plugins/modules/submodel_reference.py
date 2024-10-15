#!/usr/bin/python

# Copyright: (c) 2024, Benjamin Goetz <benjamin.goetz@ipa.fraunhofer.de>
# Apache 2.0
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: submodel_reference

short_description: Registers given submodel reference at shell repository 

# If this is part of a collection, you need to use semantic versioning,
# i.e. the version is of the form "2.5.0" and not "2.4".
version_added: "1.0.0"

description: The module registers a given submodel reference at a shell repository

options:
    scheme: 
        description: Scheme of the connection url for the shell repository
        required: true
        type: str
    host: 
        description: Hostname of the host which runs the shell repository
        required: true
        type: str
    port: 
        description: Port of the shell repository
        required: true
        type: str
    state:
        description: Defines if reference shall be created or deleted
        required: true
        type: str
    submodel_reference:
        description: Submodel Reference that shall be registered
        required: true
        type: dict
    shell_id:
        description: The id of the Shell the submodel reference shall be registered in
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
- name: Register Submodel Reference
  fabos.aas.submodel_reference:
    scheme: http
    host: localhost
    port: 8081
    state: present
    submodel_reference: {{ submodel_reference }}
    shell_id: aas-shell-id
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
from basyx.aas.adapter.json import AASToJsonEncoder
from basyx.aas.model import AssetAdministrationShell, ModelReference


class ShellRepoClient:
    def __init__(self, url):
        self.url = url

    # region UTILS
    def return_response(self, response):
        try:
            return response.status_code, json.loads(response.content)
        except JSONDecodeError:
            return response.status_code, ''

    def cast_to_dict(self, shell: AssetAdministrationShell) -> dict:
        return json.loads(
            json.dumps(shell, cls=AASToJsonEncoder)
        )

    def get_encrypted_id(self, decoded_id: str) -> str:
        return base64.b64encode(bytes(decoded_id, 'utf-8')).decode('ascii')

    def sm_id_exists_in_keys(self, sm_id, submodel_ref):
        return any(sm_id == key['value'] for key in submodel_ref['keys'])
    # endregion

    # region CRUD
    def get_shells(self):
        path = '/shells'

        return self.return_response(
            requests.get(
                url=f'{self.url}{path}'
            )
        )

    def get_shell(self, shell_id):
        path = f'/shells/{self.get_encrypted_id(shell_id)}'

        return self.return_response(
            requests.get(
                url=f'{self.url}{path}'
            )
        )

    def get_submodel_references(self, shell_id):
        path = f'/shells/{self.get_encrypted_id(shell_id)}/submodel-refs'

        return self.return_response(
            requests.get(
                url=f'{self.url}{path}'
            )
        )

    def create_shell(self, shell):
        path = '/shells'

        if isinstance(shell, AssetAdministrationShell):
            shell = self.cast_to_dict(shell)

        return self.return_response(
            requests.post(
                url=f'{self.url}{path}',
                json=shell
            )
        )

    def add_submodel_reference(self, shell_id, submodel_reference: ModelReference):
        path = f'/shells/{self.get_encrypted_id(shell_id)}/submodel-refs'

        if isinstance(submodel_reference, ModelReference):
            submodel_reference = self.cast_to_dict(submodel_reference)

        code, shell = self.get_shell(shell_id)
        if shell is not None and 'submodels' in shell:
            sm_id_to_be_created = submodel_reference['keys'][0]['value']
            if any(self.sm_id_exists_in_keys(sm_id_to_be_created, submodel) for submodel in shell['submodels']):
                return 200, self.cast_to_dict(submodel_reference)

        return self.return_response(
            requests.post(
                url=f'{self.url}{path}',
                json=self.cast_to_dict(submodel_reference)
            )
        )

    def delete_submodel_reference(self, shell_id, submodel_id):
        path = f'/shells/{self.get_encrypted_id(shell_id)}/submodel-refs/{self.get_encrypted_id(submodel_id)}'

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
        submodel_reference=dict(type='dict', required=True),
        shell_id=dict(type='str', required=True)
    )

    result = dict(
        changed=False,
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=False
    )

    shell_repo_url = f'{module.params["scheme"]}://{module.params["host"]}:{module.params["port"]}'
    client = ShellRepoClient(shell_repo_url)

    try:
        status_code, content = client.add_submodel_reference(
            shell_id=module.params['shell_id'],
            submodel_reference=module.params['submodel_reference']
        )

        if status_code == 201:
            result['changed'] = True
    except requests.exceptions.ConnectionError as e:
        module.fail_json(msg=f'Failed to connect to {shell_repo_url}. {e}', **result)

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
