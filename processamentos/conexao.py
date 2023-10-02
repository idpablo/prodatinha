import os 
import sys
import json
import inspect

import util.logger as logger
logger = logger.setup_logger('conexao.py')


def gerar_arquivo_properties(config):

    funcao_atual = inspect.currentframe().f_code.co_name  

    try:

        with open(r'/repo/prodatinha/conexao/SigpConexao.properties', 'w') as arquivo:
            arquivo.write(f"driverClassName=org.postgresql.Driver\n")
            arquivo.write(f"{config['url']}\n\n")
            arquivo.write(f"username={config['username']}\n")
            arquivo.write(f"password={config['password']}\n\n")
            arquivo.write(f"!--usuario de relatorios\n")
            arquivo.write(f"usernameReport={config['usernameReport']}\n")
            arquivo.write(f"passwordReport={config['passwordReport']}\n\n")
            arquivo.write("schema=SCH\n")
            arquivo.write("maxActive=40\n")
            arquivo.write("maxIdle=15\n")
            arquivo.write("validationQuery=select 1\n")
            arquivo.write("testOnBorrow=true\n")
            arquivo.write("testWhileIdle=true\n\n")
            arquivo.write("removeAbandoned=false\n\n")
            arquivo.write("defaultAutoCommit=true\n")
            arquivo.write("defaultReadOnly=false\n")
            arquivo.write("defaultTransactionIsolation=READ_COMMITTED\n")
            arquivo.write("isAscii=false\n\n")
            arquivo.write("utilizarSocketComProxyReverso=false\n")
            arquivo.write("utilizarChat=false\n")
            arquivo.write("portaChat=9092\n")
            arquivo.write("utilizarSocket=false\n")
            arquivo.write("portaSocket=9094\n")
            arquivo.write("portaRmiLoginCertificadoDigital=49999\n")
            arquivo.write("portaRmiRelatorioCertificadoDigitao=60001\n\n")
            arquivo.write("isHikari=false\n")
    
    except Exception as exception:

        logger.error(f"{funcao_atual} - {exception}") 

def ler_arquivo_conexao_json():

    conexao_json = '../config/conexao.json'

    funcao_atual = inspect.currentframe().f_code.co_name  

    try:

        if not os.path.isfile(conexao_json):

            sys.exit("'conexao.json' não encontrado, adicione e tente novamente.")
            
        else:
            
            with open(conexao_json) as file:
                
                logger.info(f"{funcao_atual} - Leitura do arquivo conexao.json realidaza!")   

                dados_conexao_json = json.load(file)

                return dados_conexao_json
    
    except Exception as exception:

        logger.error(f"{funcao_atual} - {exception}")  

async def definir_configuracoes_arquivo_properties(nome_servidor_desejado, nome_base_desejada):

    funcao_atual = inspect.currentframe().f_code.co_name  

    logger.info(f'Servidor: {nome_servidor_desejado}')
    logger.info(f'Base: {nome_base_desejada}')

    try:

        conexao_json = r'/repo/prodatinha/config/conexao.json'
        servidor_encontrados = None
        configuracoes_encontradas = None
        todas_urls_encontradas = []

        with open(conexao_json) as file:
                
            logger.info(f"{funcao_atual} - Leitura do arquivo conexao.json realidaza!")   

            dados_conexao_json = json.load(file)

        index = 0

        for servidor in dados_conexao_json:
            if servidor['name'] == nome_servidor_desejado:
                
                logger.info(f'Montando arquivo de conexão para o servidor: {servidor["name"]}')
                
                for bancos in servidor['bancos']:

                    if bancos['name_base'] == nome_base_desejada:

                        logger.info(f'Base encontrada: {bancos["name_base"]}')
                        logger.info(f'Url base encontrada: {bancos["url"]}')

                        configuracoes_encontradas = {
                            'url': bancos['url'],
                            'username': servidor['username'],
                            'password': servidor['password'],
                            'usernameReport': servidor['usernameReport'],
                            'passwordReport': servidor['passwordReport'],
                        }
            index =+ 1

        gerar_arquivo_properties(configuracoes_encontradas)

    except Exception as exception:
        
        logger.error(f"{funcao_atual} - {exception}")  


