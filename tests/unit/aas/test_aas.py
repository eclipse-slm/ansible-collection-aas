import logging
import sys
import time
import unittest

import requests
from basyx.aas.model import AssetAdministrationShell, AssetInformation
from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_for

from plugins.modules.aas import ShellRepoClient

logger = logging.getLogger()
logger.level = logging.INFO
stream_handler = logging.StreamHandler(sys.stdout)

AAS_ENV_PORT = 8081
CONTAINER = (DockerContainer('eclipsebasyx/aas-environment:2.0.0-SNAPSHOT')
             .with_exposed_ports(AAS_ENV_PORT))


class UnitTests(unittest.TestCase):
    aas_env_exposed_port = AAS_ENV_PORT
    aas_env_base_url = f'http://localhost:{str(aas_env_exposed_port)}'

    shell_repo_client = None

    test_shell = AssetAdministrationShell(
        id_='shell_id',
        id_short='shell_id_short',
        asset_information=AssetInformation(
            global_asset_id='asset_global_id'
        )
    )

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
        UnitTests.shell_repo_client = ShellRepoClient(url=url)

        logger.info(f'AAS Env port exposed at: {UnitTests.aas_env_exposed_port}')
        logger.info(f'AAS Env base url: {UnitTests.aas_env_base_url}')

        while not wait_for(condition=UnitTests.is_env_available):
            time.sleep(1)

    def test_01_get_all_shells_expect_200_none(self):
        status_code, content = UnitTests.shell_repo_client.get_shells()

        self.assertEqual(
            200,
            status_code
        )

        self.assertEqual(
            0,
            len(content['result'])
        )

    def test_02_create_shell_expect_201(self):
        status_code, content = UnitTests.shell_repo_client.create_shell(UnitTests.test_shell)

        self.assertEqual(
            201,
            status_code
        )

    def test_03_get_all_shells_expect_200_one(self):
        status_code, content = UnitTests.shell_repo_client.get_shells()

        self.assertEqual(
            200,
            status_code
        )

        self.assertEqual(
            1,
            len(content['result'])
        )

    def test_04_get_one_shell_expect_200(self):
        status_code, content = UnitTests.shell_repo_client.get_shell(UnitTests.test_shell.id)

        self.assertEqual(
            200,
            status_code
        )

    def test_05_create_shell_again_expect_409(self):
        status_code, content = UnitTests.shell_repo_client.create_shell(UnitTests.test_shell)

        self.assertEqual(
            409,
            status_code
        )

    def test_06_delete_shell_expect_204(self):
        status_code, content = UnitTests.shell_repo_client.delete_shell(UnitTests.test_shell.id)

        self.assertEqual(
            204,
            status_code
        )

    def test_07_get_all_shells_expect_200_none(self):
        status_code, content = UnitTests.shell_repo_client.get_shells()

        self.assertEqual(
            200,
            status_code
        )

        self.assertEqual(
            0,
            len(content['result'])
        )
