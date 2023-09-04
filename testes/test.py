import unittest
from unittest.mock import MagicMock

from processamentos.projeto import *
from processamentos.container import *
from processamentos.deploy import *

class TestProjetoProcess(unittest.IsolatedAsyncioTestCase):

    async def test_configurar_ambiente(self):
        resultado = await configurar_ambiente('/opt/docker/repo/sig', '/opt/docker/repo/sig/sig')
        self.assertTrue(resultado)
    
    async def test_versionamento_sig(self):
        resultado = await versionamento_sig()
        self.assertTrue(resultado)
    
    async def test_criar_branch(self):
        resultado = await git_criar_branch('/opt/docker/repo/sig', 'teste-versao-auto')
        self.assertTrue(resultado)
    
    async def test_commitar_branch(self):
        resultado = await git_commit('/opt/docker/repo/sig', '2.5.216', '2023.08.10')
        self.assertTrue(resultado)

    async def test_copiar_funcoes(self):
        resultado = await copiar_war('/opt/docker/repo/sig', '/opt/docker/repo/prodatinha/sigtomcat/sigpwebfuncoes/')
        self.assertTrue(resultado)

class TestContainerProcess(unittest.IsolatedAsyncioTestCase):

    async def test_criar_container_funcoes(self):
        resultado = await docker_criar_container('/opt/docker/repo/prodatinha/sigtomcat/sigpwebfuncoes/', 'sigpwebfuncoes')
        self.assertTrue(resultado)

class TestExecutarFuncoes(unittest.TestCase):
    def setUp(self):
        # Crie um objeto Docker Mock para simular a interação com o Docker
        self.docker_mock = MagicMock()
        self.client_mock = MagicMock()
        self.container_mock = MagicMock()
    
    def test_executar_funcoes_capturar_saida(self):
        resultado = executar_curl('http://localhost:8080/sigpwebfuncoes/funcoes_setup.jsp')
        self.assertTrue(resultado)

    def test_capturar_logs_com_erro(self):
        # Configura o mock para retornar logs de teste
        logs_de_teste = "Isso é um erro\nOutro erro\nIsso não é um erro"
        self.container_mock.logs.return_value.decode.return_value = logs_de_teste

        # Configura a interação com o Docker
        self.docker_mock.from_env.return_value = self.client_mock
        self.client_mock.containers.get.return_value = self.container_mock

        while True:
            logs_com_erro = capturar_logs_com_erro_pelo_nome('sigpwebfuncoes')
            self.assertFalse(logs_com_erro)
        
if __name__ == '__main__':
    unittest.main()