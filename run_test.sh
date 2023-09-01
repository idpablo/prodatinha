#Script para execução de testes unitarios do arquivo test.py de forma individual 
#Estrutura:
# python3 -m unittest arquivo.class.function
 
cd testes/

#python3 -m unittest test.TestProjetoProcess.test_copiar_funcoes 

python3 -m unittest test.TestProjetoProcess.test_versionamento_sig
