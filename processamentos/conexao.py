import os 
import sys
import json
import inspect

# from util.logger import logger
# logger = logger.setup_logger('conexao.py')


def gerar_arquivo_properties(config):

    with open(f"Teste_SigpConexao.properties", 'w') as arquivo:
        arquivo.write(f"driverClassName=org.postgresql.Driver\n")
        arquivo.write(f"url=jdbc:postgresql://{config['url']}\n")
        arquivo.write(f"username={config['username']}\n")
        arquivo.write(f"password={config['password']}\n")
        arquivo.write(f"usernameReport={config['usernameReport']}\n")
        arquivo.write(f"passwordReport={config['passwordReport']}\n")
        arquivo.write("schema=SCH\n")
        arquivo.write("maxActive=40\n")
        arquivo.write("maxIdle=15\n")
        arquivo.write("validationQuery=select 1\n")
        arquivo.write("testOnBorrow=true\n")
        arquivo.write("testWhileIdle=true\n")
        arquivo.write("removeAbandoned=false\n")
        arquivo.write("defaultAutoCommit=true\n")
        arquivo.write("defaultReadOnly=false\n")
        arquivo.write("defaultTransactionIsolation=READ_COMMITTED\n")
        arquivo.write("isAscii=false\n")
        arquivo.write("utilizarSocketComProxyReverso=false\n")
        arquivo.write("utilizarChat=false\n")
        arquivo.write("portaChat=9092\n")
        arquivo.write("utilizarSocket=false\n")
        arquivo.write("portaSocket=9094\n")
        arquivo.write("portaRmiLoginCertificadoDigital=49999\n")
        arquivo.write("portaRmiRelatorioCertificadoDigitao=60001\n")
        arquivo.write("isHikari=false\n")

def ler_arquivo_conexao_json():

    conexao_json = '../config/conexao.json'

    funcao_atual = inspect.currentframe().f_code.co_name  

    try:

        if not os.path.isfile(conexao_json):

            sys.exit("'conexao.json' não encontrado, adicione e tente novamente.")
            
        else:
            
            with open(conexao_json) as file:
                
                print(f"{funcao_atual} - Leitura do arquivo conexao.json realidaza!")   

                dados_conexao_json = json.load(file)

                return dados_conexao_json
    
    except Exception as exception:

        print(f"{funcao_atual} - {exception}")  

def definir_configuracoes_arquivo_properties(nome_servidor_desejado, nome_base_desejada):

    funcao_atual = inspect.currentframe().f_code.co_name  

    try:

        configuracoes_encontradas = None

        dados_conexao = ler_arquivo_conexao_json()
        
        for servidor_data in dados_conexao:
            if servidor_data['name'] == nome_servidor_desejado:
                for banco_data in servidor_data['bancos']:
                    if banco_data['name_base'] == nome_base_desejada:
                        configuracoes_encontradas = {
                            'url': banco_data['url'],
                            'username': servidor_data['username'],
                            'password': servidor_data['password'],
                            'usernameReport': servidor_data['usernameReport'],
                            'passwordReport': servidor_data['passwordReport']
                        }
                        break
                if configuracoes_encontradas:
                    break
        
        if configuracoes_encontradas:

            gerar_arquivo_properties(configuracoes_encontradas)
            print(f"Arquivo SigpConexao.properties da base {nome_servidor_desejado}_{nome_base_desejada} gerado com sucesso.")

            return True

        else:

            print(f"Configurações para o servidor {nome_servidor_desejado} e a base {nome_base_desejada} não foram encontradas.")

            return False

    except Exception as exception:
        
        print(f"{funcao_atual} - {exception}")  