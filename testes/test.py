import unittest

from processamentos.projeto import *
from processamentos.container import *

class TestProjetoProcess(unittest.IsolatedAsyncioTestCase):

    async def test_configurar_ambiente(self):
        resultado = await configurar_ambiente('/opt/docker/repo/sig', '/opt/docker/repo/sig/sig')
        self.assertTrue(resultado)
    
    async def test_versionamento_sig(self):
        resultado = await versionamento_sig()
        self.assertTrue(resultado)

    async def test_copiar_funcoes(self):
        resultado = await copiar_war('/repo/sig/sigpwebfuncoes/build/libs/', '/opt/docker/repo/prodatinha/sigtomcat/sigpwebfuncoes/')
        self.assertTrue(resultado)
    
    async def test_copiar_sig(self):
        resultado = await copiar_war('/repo/sig/sig/build/libs/', '/opt/docker/repo/prodatinha/sigtomcat/sig/')
        self.assertTrue(resultado)

    async def test_criar_container_funcoes(self):
        resultado = await criar_container('/opt/docker/repo/prodatinha/sigtomcat/sigpwebfuncoes/', 'sigpwebfuncoes')
        self.assertTrue(resultado)

if __name__ == '__main__':
    unittest.main()