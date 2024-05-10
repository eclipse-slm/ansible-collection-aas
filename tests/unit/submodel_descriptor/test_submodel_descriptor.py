import logging
import sys
import time
import unittest

import requests
from aas_reg_client import SubmodelDescriptor, Endpoint, ProtocolInformation
from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_for

from plugins.modules.submodel_descriptor import SmRegistryClient

logger = logging.getLogger()
logger.level = logging.INFO
stream_handler = logging.StreamHandler(sys.stdout)


SM_REG_PORT = 8080
CONTAINER = (DockerContainer('eclipsebasyx/submodel-registry-log-mem:2.0.0-milestone-02')
             .with_exposed_ports(SM_REG_PORT))


class UnitTests(unittest.TestCase):
    sm_reg_exposed_port = SM_REG_PORT
    sm_reg_base_url = f'http://localhost:{str(sm_reg_exposed_port)}'

    shell_repo_client = None

    test_submodel_descriptor = {
        'id': 'sm-id',
        'endpoints': [
            {
                'interface': 'http',
                'protocolInformation': {
                    'href': 'http://localhost:8081/submodels/sm-id'
                }
            }
        ]
    }

    # SETUP / TEAR DOWN:
    @classmethod
    def setUpClass(cls):
        logger.addHandler(stream_handler)
        cls.startContainer()

    @classmethod
    def tearDownClass(cls):
        logger.removeHandler(stream_handler)

    @classmethod
    def is_reg_available(cls) -> bool:
        sm_reg_swagger_url = f'{UnitTests.sm_reg_base_url}/swagger-ui/index.html'
        print(sm_reg_swagger_url)

        try:
            r = requests.get(sm_reg_swagger_url)
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
        UnitTests.sm_reg_exposed_port = CONTAINER.get_exposed_port(SM_REG_PORT)

        url = f'http://localhost:{UnitTests.sm_reg_exposed_port}'
        UnitTests.sm_reg_base_url = url
        UnitTests.shell_repo_client = SmRegistryClient(url=url)

        logger.info(f'SM Registry port exposed at: {UnitTests.sm_reg_exposed_port}')
        logger.info(f'SM Registry base url: {UnitTests.sm_reg_base_url}')

        while not wait_for(condition=UnitTests.is_reg_available):
            time.sleep(1)

    def test_01_get_submodel_descriptors_expect_200_none(self):
        status_code, content = UnitTests.shell_repo_client.get_descriptors()

        self.assertEqual(
            200,
            status_code
        )

        self.assertEqual(
            0,
            len(content['result'])
        )

    def test_02_create_submodel_descriptor_expect_201(self):
        status_code, content = UnitTests.shell_repo_client.create_descriptor(UnitTests.test_submodel_descriptor)

        self.assertEqual(
            201,
            status_code
        )

    def test_03_get_submodel_descriptors_expect_200_one(self):
        status_code, content = UnitTests.shell_repo_client.get_descriptors()

        self.assertEqual(
            200,
            status_code
        )

        self.assertEqual(
            1,
            len(content['result'])
        )

    def test_04_get_submodel_descriptor_expect_200(self):
        status_code, content = UnitTests.shell_repo_client.get_descriptor(UnitTests.test_submodel_descriptor['id'])

        self.assertEqual(
            200,
            status_code
        )

    def test_05_create_submodel_descriptor_again_expect_409(self):
        status_code, content = UnitTests.shell_repo_client.create_descriptor(UnitTests.test_submodel_descriptor)

        self.assertEqual(
            409,
            status_code
        )

    def test_06_get_submodel_descriptors_again_expect_200_one(self):
        status_code, content = UnitTests.shell_repo_client.get_descriptors()

        self.assertEqual(
            200,
            status_code
        )

        self.assertEqual(
            1,
            len(content['result'])
        )

    def test_07_delete_submodel_descriptor_expect_204(self):
        status_code, content = UnitTests.shell_repo_client.delete_descriptor(UnitTests.test_submodel_descriptor['id'])

        self.assertEqual(
            204,
            status_code
        )

    def test_08_get_submodel_descriptors_expect_200_none(self):
        status_code, content = UnitTests.shell_repo_client.get_descriptors()

        self.assertEqual(
            200,
            status_code
        )

        self.assertEqual(
            0,
            len(content['result'])
        )
