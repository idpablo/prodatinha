import os
import inspect
import asyncio
import requests
import subprocess

import util.logger as logger
logger = logger.setup_logger('container.py')

from bs4 import BeautifulSoup

def executar_curl(url):
    try:
        
        arquivo_saida = './saida.txt'
        linhas_de_erro = []
        arquivos_txt = []

        resultado = subprocess.run(['curl', '-s', url], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, encoding='iso-8859-1')
        saida = resultado.stdout
        status = resultado.returncode

        linhas = saida.splitlines()

        if status == 0:

            # for linha in saida:
            #     linha_sem_tags = BeautifulSoup(linha, 'html.parser')
                
            #     if 'ERRO' in linha_sem_tags:
            #         linhas_de_erro.append(linha)

            # linhas_encontradas = linhas_de_erro

            for linha in linhas:


                if 'ERRO' in linha:
                    linhas_de_erro.append(linha) 
                    logger.info(linha)
            
            return True

        return False
    
    except subprocess.CalledProcessError as e:
        
        logger.info(f"Erro ao executar o comando curl: {e}")
        return False
    
    except Exception as e:
        
        logger.error(f"Erro inesperado: {e}")
        return False 

def capturar_linhas_de_erro(diretorio_arquivo):

    funcao_atual = inspect.currentframe().f_code.co_name
    
    try:

        nome_arquivo = 'resposta.txt'

        linhas_de_erro = []
        arquivos_txt = []

        os.chdir(diretorio_arquivo)
        diretorio_atual = os.getcwd()

        logger.info(f"Diretorio atual: {diretorio_atual}")

        lista_arquivos = os.listdir(diretorio_arquivo)
        
        for arquivo in lista_arquivos:
            if arquivo.endswith(".txt"):
                arquivos_txt.append(arquivo)

        if os.path.isfile(nome_arquivo):

            logger.info(f'Arquivo {nome_arquivo} encontrado.')
        
            with open(nome_arquivo, 'r', encoding='iso-8859-1') as arquivo_texto:
                for linha in arquivo_texto:
                    linha_sem_tags = BeautifulSoup(linha, 'html.parser').get_text()
                    
                    if 'erro' in linha_sem_tags.lower():
                        linhas_de_erro.append(linha)

            linhas_encontradas = linhas_de_erro

            for linha in linhas_encontradas:
                logger.info(linha.strip()) 
            
            return True
        
        return False
    
    except Exception as exeption:

        logger.error(f"{funcao_atual} - Erro ao separar linhas erro - {exeption}")
    
        return False

