import logging
import sys
import time
import unittest

import requests
from basyx.aas import model
from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_for

from plugins.modules.submodel import SmRepoClient

logger = logging.getLogger()
logger.level = logging.INFO
stream_handler = logging.StreamHandler(sys.stdout)

AAS_ENV_PORT = 8081
CONTAINER = (DockerContainer('eclipsebasyx/aas-environment:2.0.0-SNAPSHOT')
             .with_exposed_ports(AAS_ENV_PORT))


class UnitTests(unittest.TestCase):
    aas_env_exposed_port = AAS_ENV_PORT
    aas_env_base_url = f'http://localhost:{str(aas_env_exposed_port)}'

    se_property_id = 'test_property_id_short'
    se_property_value = 'test_property_value'
    sm_repo_client = None

    # SETUP / TEAR DOWN:
    @classmethod
    def setUpClass(cls):
        logger.addHandler(stream_handler)
        cls.startContainer()

    @classmethod
    def tearDownClass(cls):
        logger.removeHandler(stream_handler)

    @classmethod
    def is_env_available(cls) -> bool:
        aas_env_swagger_url = f'{UnitTests.aas_env_base_url}/swagger-ui/index.html'

        try:
            r = requests.get(aas_env_swagger_url)
            print(f'Response code: {r.status_code}')

            if r.status_code == 200:
                return True
            else:
                return False
        except requests.exceptions.ConnectionError:
            return False

    @classmethod
    def startContainer(cls):
        CONTAINER.start()
        UnitTests.aas_env_exposed_port = CONTAINER.get_exposed_port(AAS_ENV_PORT)

        url = f'http://localhost:{UnitTests.aas_env_exposed_port}'
        UnitTests.aas_env_base_url = url
        UnitTests.sm_repo_client = SmRepoClient(url=url)

        logger.info(f'AAS Env port exposed at: {UnitTests.aas_env_exposed_port}')
        logger.info(f'AAS Env base url: {UnitTests.aas_env_base_url}')

        while not wait_for(condition=UnitTests.is_env_available):
            time.sleep(1)

    def get_submodel(self, prop_value=''):
        if prop_value == '':
            prop_value = self.se_property_value

        return model.Submodel(
            id_='test-submodel-id',
            submodel_element={
                model.Property(
                    id_short=self.se_property_id,
                    value_type=model.datatypes.String,
                    value=prop_value,
                )
            }
        )

    def test_01_get_all_expect_none(self):
        status_code, content = UnitTests.sm_repo_client.get_all()

        self.assertEqual(
            200,
            status_code
        )

        self.assertEqual(
            0,
            len(content['result'])
        )

    def test_02_register_sm_expect_201(self):
        status_code, content = UnitTests.sm_repo_client.create(self.get_submodel())

        self.assertEqual(
            201,
            status_code
        )

    def test_03_register_sm_expect_409(self):
        status_code, content = UnitTests.sm_repo_client.create(self.get_submodel())

        self.assertEqual(
            409,
            status_code
        )

    def test_04_get_all_expect_one(self):
        status_code, content = UnitTests.sm_repo_client.get_all()

        self.assertEqual(
            200,
            status_code
        )

        self.assertEqual(
            1,
            len(content['result'])
        )

    def test_05_update_sm_expect_204(self):
        new_submodel = self.get_submodel('new_value')

        status_code, content = UnitTests.sm_repo_client.update(new_submodel)

        self.assertEqual(
            204,
            status_code
        )

    def test_06_get_sm_expect_200(self):
        status_code, content = UnitTests.sm_repo_client.get_one(self.get_submodel().id)

        self.assertEqual(
            200,
            status_code
        )

    def test_07_get_sm_expect_updated_prop_value(self):
        status_code, content = UnitTests.sm_repo_client.get_one(self.get_submodel().id)

        old_prop_value = self.se_property_value
        new_prop_value = content['submodelElements'][0]['value']

        self.assertNotEquals(
            old_prop_value,
            new_prop_value
        )

    def test_08_register_sm_force_expect_204(self):
        status_code, content = UnitTests.sm_repo_client.create(self.get_submodel(), True)

        self.assertEqual(
            204,
            status_code
        )

    def test_09_get_sm_expect_updated_prop_value(self):
        status_code, content = UnitTests.sm_repo_client.get_one(self.get_submodel().id)

        old_prop_value = self.se_property_value
        new_prop_value = content['submodelElements'][0]['value']

        self.assertEqual(
            old_prop_value,
            new_prop_value
        )

    def test_10_delete_sm_expect_204(self):
        status_code, content = UnitTests.sm_repo_client.delete(self.get_submodel().id)

        self.assertEqual(
            204,
            status_code
        )

    def test_11_get_all_expect_none(self):
        status_code, content = UnitTests.sm_repo_client.get_all()

        self.assertEqual(
            200,
            status_code
        )

        self.assertEqual(
            0,
            len(content['result'])
        )
