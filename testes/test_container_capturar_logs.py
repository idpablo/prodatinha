import unittest
from unittest.mock import MagicMock
from processamentos.container import * 
from processamentos.deploy import * 

class TestCriarExecutarFuncoes(unittest.TestCase):
    def setUp(self):
        # Crie um objeto Docker Mock para simular a interação com o Docker
        self.docker_mock = MagicMock()
        self.client_mock = MagicMock()
        self.container_mock = MagicMock()
    
    async def test_criar_container_funcoes(self):
        resultado = await docker_criar_container('/opt/docker/repo/prodatinha/sigtomcat/sigpwebfuncoes/', 'sigpwebfuncoes')
        self.assertTrue(resultado)

    def test_executar_funcoes(self):
        resultado = executar_funcoes('http://localhost:8080/sigpwebfuncoes/funcoes_setup.jsp')
        self.assertTrue(resultado)

    def test_capturar_logs_com_erro(self):
        # Configura o mock para retornar logs de teste
        logs_de_teste = "Isso é um erro\nOutro erro\nIsso não é um erro"
        self.container_mock.logs.return_value.decode.return_value = logs_de_teste

        # Configura a interação com o Docker
        self.docker_mock.from_env.return_value = self.client_mock
        self.client_mock.containers.get.return_value = self.container_mock

        # Chama a função que você deseja testar
        logs_com_erro = capturar_logs_com_erro_pelo_nome('sigpwebfuncoes')

        # Verifica se a função retorna as linhas de erro esperadas
        self.assertEqual(logs_com_erro, "Isso é um erro\nOutro erro")

if __name__ == '__main__':
    unittest.main()
