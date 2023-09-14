import unittest

from processamentos.projeto import *
from processamentos.container import *
from processamentos.deploy import *
from gera_versao_local import *

diretorio_projeto = '/opt/docker/repo/sig'
diretorio_root_sig = "/opt/docker/repo/sig/sig"
diretorio_root_funcoes = "/opt/docker/repo/sig/sigpwebfuncoes"
arquivo_funcoes_war = "/opt/docker/repo/sig/sigpwebfuncoes/build/libs"

class TestExecutarFuncoes(unittest.IsolatedAsyncioTestCase):
    
    async def test_gerar_funcoes(self):
        
        ambiente = await configurar_ambiente('/opt/docker/repo/sig', diretorio_root_funcoes)

        if ambiente: 

            versao_atual, data_atual = await versao_atual_funcoes()  # pyright: ignore
            data_atualizada = await versionamento_funcoes()

            print(f"Versão atual: {versao_atual}") 
            print(f"Versão que sera gerada: {versao_atual}") 
            print(f"Data atual: {data_atual}")
            print(f"Data da versão que sera gerada: {data_atualizada}") 
            print(f"Iniciando Clean do repositorio...")
            print(f"Apagando as versões geradas anteriormente...")

            processo_clean = await gradle_clean()

            if processo_clean.returncode == 0: # pyright: ignore

                resultado_war, processo_war = await gradle_war() # pyright: ignore

                if processo_war.returncode == 0: # pyright: ignore
                
                    processo_copiar_war = await copiar_war(arquivo_funcoes_war, '/opt/docker/repo/prodatinha/sigtomcat/sigpwebfuncoes/')

                    if processo_copiar_war:
                        
                        criar_container = await docker_criar_container('/opt/docker/repo/prodatinha/sigtomcat/sigpwebfuncoes/', 'sigpwebfuncoes')
                       
                        if criar_container:
                            print("CONTAINER CRIADO")
                            resultado = executar_curl('http://localhost:8080/sigpwebfuncoes/funcoes_setup.jsp') 
                    
                        else:
                    
                            resultado = False
                    else:

                        resultado = False

                else:
                
                    resultado = False

            else:
                
                resultado = False

            self.assertTrue(resultado)

    async def test_criar_container_funcoes(self):
        resultado = await docker_criar_container('/opt/docker/repo/prodatinha/sigtomcat/sigpwebfuncoes/', 'sigpwebfuncoes')
        self.assertTrue(resultado)

    async def test_executar_funcoes(self):
        resultado = await executar_curl('http://localhost:8080/sigpwebfuncoes/funcoes_setup.jsp')  # pyright: ignore
        self.assertTrue(resultado)
    
if __name__ == '__main__':
    unittest.main()