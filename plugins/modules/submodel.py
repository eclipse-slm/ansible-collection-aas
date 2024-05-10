#!/usr/bin/python

# Copyright: (c) 2024, Benjamin Goetz <benjamin.goetz@ipa.fraunhofer.de>
# Apache 2.0
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: submodel

short_description: Registers given submodel at repository 

# If this is part of a collection, you need to use semantic versioning,
# i.e. the version is of the form "2.5.0" and not "2.4".
version_added: "1.0.0"

description: The module registers a given submodel at a submodel repository

options:
    submodel:
        description: Facts that shall be converted into a submodel
        required: true
        type: dict
    id:
        description: The id the submodel shall have
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

import base64
import json
from json import JSONDecodeError

import requests
from basyx.aas import model
from basyx.aas.adapter.json import AASToJsonEncoder
from basyx.aas.model import ModelReference, Key, KeyTypes


class SmRepoClient:
    def __init__(self, url):
        self.url = url

    # region UTILS:
    def cast_sm_to_dict(self, submodel) -> dict:
        return json.loads(
            json.dumps(submodel, cls=AASToJsonEncoder)
        )

    def get_sm_as_dict(self, submodel) -> dict:
        if isinstance(submodel, model.Submodel):
            submodel = self.cast_sm_to_dict(submodel)
        return submodel

    def get_encrypted_sm_id_from_submodel(self, submodel) -> str:
        if isinstance(submodel, dict):
            return base64.b64encode(bytes(submodel['id'], 'utf-8')).decode('ascii')
        else:
            return base64.b64encode(bytes(submodel.id, 'utf-8')).decode('ascii')

    def get_encrypted_sm_id_from_id(self, sm_id: str) -> str:
        return base64.b64encode(bytes(sm_id, 'utf-8')).decode('ascii')

    def return_response(self, response):
        try:
            return response.status_code, json.loads(response.content)
        except JSONDecodeError:
            return response.status_code, ''

    # endregion

    # region CRUD
    def create(self, submodel, force=False):
        path = '/submodels'

        if isinstance(submodel, model.Submodel):
            submodel = self.cast_sm_to_dict(submodel)

        r = requests.post(
            url=f'{self.url}{path}',
            json=self.get_sm_as_dict(submodel),
        )

        if r.status_code == 409 and force:
            return self.update(submodel)

        return self.return_response(r)

    def update(self, submodel):
        path = f'/submodels/{self.get_encrypted_sm_id_from_submodel(submodel)}'

        return self.return_response(
            requests.put(
                url=f'{self.url}{path}',
                json=self.get_sm_as_dict(submodel),
            )
        )


        try:
            return r.status_code, json.loads(r.content)
        except JSONDecodeError:
            return r.status_code, ''

    def get_all(self):
        path = '/submodels'

        return self.return_response(
            requests.get(
                url=f'{self.url}{path}'
            )
        )

    def get_one(self, sm_id: str):
        path = f'/submodels/{self.get_encrypted_sm_id_from_id(sm_id)}'

        return self.return_response(
            requests.get(
                url=f'{self.url}{path}'
            )
        )

    def delete(self, sm_id: str):
        path = f'/submodels/{self.get_encrypted_sm_id_from_id(sm_id)}'

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
        submodel=dict(type='dict', required=True),
        force=dict(type='bool', default=True)
    )

    result = dict(
        reference=dict(),
        submodel_descriptor=dict(),
        changed=False,
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=False
    )

    sm_repo_url = f'{module.params["scheme"]}://{module.params["host"]}:{module.params["port"]}'
    client = SmRepoClient(sm_repo_url)

    client.create(
        module.params['submodel'],
        module.params['force']
    )

    sm_id = module.params['submodel']['id']
    sm_id_enc = client.get_encrypted_sm_id_from_id(sm_id)
    sm_url =  f'{sm_repo_url}/{sm_id_enc}'

    result['reference'] = json.loads(
        json.dumps(
            ModelReference(
                key=[Key(type_=KeyTypes.SUBMODEL, value=sm_id)],
                type_=ModelReference.__name__
            ),
            cls=AASToJsonEncoder
        )
    )

    result['submodel_descriptor'] = {
        "id": sm_id,
        "endpoints": [
            {
                "interface": "http",
                "protocolInformation": {
                    "href": sm_url
                }
            }
        ]
    }

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
