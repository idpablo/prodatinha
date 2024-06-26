import os
import re
import sys
import json
import zipfile
import asyncio
import inspect
import subprocess

from util import logger

from datetime import datetime

sys.setrecursionlimit(16385)

logger = logger.setup_logger("projeto.py")


async def git_checkout(branch, diretorio_projeto):
    
    try:

        funcao_atual = inspect.currentframe().f_code.co_name

        os.chdir(diretorio_projeto)
        diretorio_atual = os.getcwd()

        logger.info(f'Mudando para a branch --> {branch}')
        logger.info(f"Diretorio: {diretorio_atual}")

        processo_git_stash = subprocess.run(["bash", "-c", f"git stash"], capture_output=True)

        if processo_git_stash.returncode == 0:

            logger.info(f"Stash: {processo_git_stash.stdout}")

        processo_git_checkout = subprocess.run(["bash", "-c", f"git checkout {branch}"], capture_output=True)

        if processo_git_checkout.returncode == 0:
            
            logger.info(f"Branch: {processo_git_checkout.stdout}")

            return processo_git_checkout
    
    except Exception as exeption:
        
        logger.error(f"{funcao_atual} - {exeption}")
        return("Erro ao alterar branch")

#Deve ser implementado
async def git_criar_branch(diretorio_projeto, nova_branch):
    
    funcao_atual = inspect.currentframe().f_code.co_name

    try:
        logger.info("Criando nova branch pra gerar o build da aplicação")

        os.chdir(diretorio_projeto)
        diretorio_atual = os.getcwd()

        logger.info(f"Diretorio: {diretorio_atual}")
        logger.info(f'Nome da branch --> {nova_branch}')

        processo_git_checkout = subprocess.run(["bash", "-c", f"git checkout -b {nova_branch}"], capture_output=True)

        if processo_git_checkout.returncode == 0:

            logger.info(f'Branch criada: {processo_git_checkout.stdout}')
        
        if processo_git_checkout.returncode == 0:

            logger.info(f'Branch criada: {processo_git_checkout.stdout}')
        
    except Exception as exception:

        logger.error(f"{funcao_atual} - {exception}")

#Deve ser implementado
async def git_commit(diretorio_projeto):
    
    funcao_atual = inspect.currentframe().f_code.co_name

    try:
        
        logger.info("Iniciando processo de commit")
    
    except Exception as exception:

        logger.error(f"{funcao_atual} - {exception}")

async def versionamento_sig():

    funcao_atual = inspect.currentframe().f_code.co_name
    diretorio_json = "/opt/docker/repo/sig/sig/WebContent/version.json"

    try:

        if not os.path.isfile(diretorio_json):
            sys.exit("'version.json' não encontrado, adicione e tente novamente.")
        else:
            with open(diretorio_json) as file:
                
                version = json.load(file)

                versao_atual = version["versaosig"]

                versao = version["versaosig"].split('.')
                versao_concat = int(versao[2]) + 1
                versao_concat = str(versao_concat)
                versaosig = versao[0] +"." + versao[1] + "." + versao_concat

                logger.info(f"Versão Atual: {versaosig}")

                cache_atual = version["cache"]
                cache = int(version["cache"])
                cache_novo = cache + 1

                logger.info(f"Cache Atual: {cache_novo}")
            
            version['versaosig'] = versaosig
            version['cache'] = cache_novo

            with open(diretorio_json, 'w') as arquivo:
                json.dump(version, arquivo, indent=4)
            
            return versao_atual, versaosig, cache_atual, cache_novo
    
    except Exception as exception:

        logger.error(f"{funcao_atual} - {exception}")

async def versao_atual_funcoes():

    funcao_atual = inspect.currentframe().f_code.co_name
    caminho_versao_sigpwebfuncoes = r"/opt/docker/repo/sig/sigpwebfuncoes/src/servico/setup/VersaoSigpWebFuncoes.java"

    try:

        with open(caminho_versao_sigpwebfuncoes, 'r', encoding='cp1252') as f:
            conteudo = f.read()

            padrao_versao = r'VERSAO\s*=\s*"(.*)"'
            padrao_data = r'DATA\s*=\s*"(.*)"'

            versao = re.search(padrao_versao, conteudo)
            data = re.search(padrao_data, conteudo)

            if versao and data:
                versao = versao.group(1)
                data = data.group(1)

                logger.info(f"Versão atual: {versao}")
                logger.info(f"Data atual: {data}")

                return versao, data
            else:
                return None, None
        
    except Exception as exception:

        logger.error(f"{funcao_atual} - {exception}")

async def versionamento_funcoes():

    funcao_atual = inspect.currentframe().f_code.co_name
    caminho_versao_sigpwebfuncoes = r"/opt/docker/repo/sig/sigpwebfuncoes/src/servico/setup/VersaoSigpWebFuncoes.java"

    try:

        nova_data = datetime.now().strftime("%d/%m/%Y - %H:%M:%S")
        nova_data_nome = datetime.now().strftime("%d-%m-%Y")

        with open(caminho_versao_sigpwebfuncoes, 'r', encoding='cp1252') as f:
            conteudo = f.read()

        conteudo = re.sub(r'DATA\s*=\s*".*"', f'DATA="{nova_data}"', conteudo)

        with open(caminho_versao_sigpwebfuncoes, 'w', encoding='cp1252') as f:
            f.write(conteudo)

        logger.info(f"Data atualizada: {nova_data}")

        if nova_data:
                return nova_data_nome
        else:
            return None, None
        
    except Exception as exception:

        logger.error(f"{funcao_atual} - {exception}")

async def configurar_ambiente(diretorio_projeto, diretorio_sig):

    funcao_atual = inspect.currentframe().f_code.co_names

    try:

        if not os.path.isdir(diretorio_projeto):
            logger.info(f"Diretório inválido: {diretorio_projeto}")
            return

        os.chdir(diretorio_projeto)

        diretorio_atual = os.getcwd()
        logger.info(f"Diretório atual: {diretorio_atual}")

        if diretorio_atual != diretorio_projeto:
            logger.info(f"Diretório incorreto. Esperado: {diretorio_projeto}")
            return

        resultado_pull = subprocess.run(["bash", "-c", 'git pull'], capture_output=True, text=True)
        
        if resultado_pull.returncode == 0:
            logger.info(f"Resultado git pull: {resultado_pull.stdout.strip()}")
        else:
            
            logger.error(f"{funcao_atual} - Erro ao executar git pull: {resultado_pull.stderr.strip()}")

        if not os.path.isdir(diretorio_sig):
            logger.info(f"Diretório inválido: {diretorio_sig}")
            return

        os.chdir(diretorio_sig)

        diretorio_atual_sig = os.getcwd()
        logger.info(f"Diretório atual (sig): {diretorio_atual_sig}")

        if diretorio_atual_sig != diretorio_sig:
            logger.info(f"Diretório incorreto. Esperado: {diretorio_sig}")
            return
        
        return True;

    except Exception as exception:
        logger.error(f"{funcao_atual} - { exception}")

async def gradle_clean():
    try:
        funcao_atual = inspect.currentframe().f_code.co_name

        logger.info(f"Iniciando clean do projeto")

        while True:

            processo = await asyncio.create_subprocess_shell('gradle clean', stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
            await processo.communicate() 

            if processo.returncode == 0:
                logger.info(f"Sucesso ao executar gradle clean")
                return processo
            else:
                logger.error(f"{funcao_atual} - Erro ao executar o gradle clean.")

    except Exception as exception:
        logger.error(f"{funcao_atual} - {exception}")
        await asyncio.sleep(5)

async def gradle_war():
    
    funcao_atual = inspect.currentframe().f_code.co_name

    try:
        
        logger.info(f"Iniciando build do projeto")

        while True:


            processo = await asyncio.create_subprocess_shell('gradle war', stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
            stdout, stderr = await processo.communicate()

            if processo.returncode == 0:

                logger.info(f"Sucesso ao executar gradle war")
                return stdout.decode(), processo
            
            else:
                
                logger.error(f"Erro ao executar o gradle war: {stderr.decode()}")

    except Exception as exception:

        logger.error(f"{funcao_atual} - {exception}")
        await asyncio.sleep(5)

async def adicionar_properties(caminho_war, caminho_no_war, caminho_properties):
    
    arquivo_war = os.path.abspath(caminho_war)
    arquivo_properties = os.path.abspath(caminho_properties)

    try:
        with zipfile.ZipFile(arquivo_war, 'a') as war_zip:
            war_zip.write(arquivo_properties, arcname=caminho_no_war)

        logger.info("Arquivo adicionado ao pacote .war com sucesso!")

        return True
    
    except Exception as e:
        logger.error(f"Ocorreu um erro ao adicionar o arquivo: {e}")

async def copiar_war(caminho_war, destino):
    
    arquivo_war = os.path.abspath(caminho_war)
    arquivo_destino = os.path.abspath(destino)

    try:
        os.chdir(caminho_war)
        diretorio_atual = os.getcwd()
        logger.info(f"Diretorio atual: {diretorio_atual}")

        if os.path.exists("sig.war") or os.path.exists("sigpwebfuncoes.war"):

            logger.info(f"Arquivos encontrados")

            while True:
                
                logger.info(f"Diretorio destino: {diretorio_atual}")
                processo = await asyncio.create_subprocess_shell(f'cp *.war {destino}', stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
                
                resultado_processo = await processo.communicate()

                if processo.returncode == 0:
                    
                    logger.info(f"Sucesso ao copiar arquivo")
                    return True
                
                else:
                    logger.info(f"Ocorreu um erro ao copiar o war")
                    return False
        
        else:
            
            logger.info(f"Arquivo war não encontrado")
    
    except Exception as e:

        logger.error(f"Ocorreu um erro ao adicionar o arquivo: {e}")

async def compactar_arquivo(caminho_diretorio, nome_arquivo):

    funcao_atual = inspect.currentframe().f_code.co_name

    try:

        logger.info(f"Caminho recebido: {caminho_diretorio}")
        logger.info(f"Nome arquivo recebido: {nome_arquivo}")

        os.chdir(caminho_diretorio)
        diretorio_atual = os.getcwd()

        logger.info(f"Diretorio atual: {diretorio_atual}")

        if os.path.exists("sig") or os.path.exists("sig.war"):

            if os.path.exists("sig"):
                
                os.rename("sig", "sig.war")

            logger.info(f"{funcao_atual} - arquivo sig encontrado. Renomenando...")
            logger.info(f"Renomenando arquivo...")

            caminho_arquivo = caminho_diretorio + "/sig.war"

            while True:

                processo = await asyncio.create_subprocess_shell(f'rar a {nome_arquivo}.rar sig.war', stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
                await processo.communicate()

                if processo.returncode == 0:
                    
                    logger.info("Processo de compactação finalizado!")

                    return True

                else:
                
                    logger.error(f"{funcao_atual} - Erro ao executar compactação: {processo}")

        elif os.path.exists("sigpwebfuncoes.war"):

            logger.info(f"{funcao_atual} - arquivo sigpwebfuncoes.war encontrado")

            caminho_arquivo = caminho_diretorio + "/sigpwebfuncoes.war"

            logger.info(f"Arquivo sigpwebfuncoes.war encontrado")

            diretorio_atual = os.getcwd()

            logger.info(f"Diretorio atual: {diretorio_atual}")

            while True:

                processo = await asyncio.create_subprocess_shell(f'rar a "{nome_arquivo}.rar" sigpwebfuncoes.war', stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
                await processo.communicate()

                logger.info(f"Arquivo {caminho_arquivo} compactado com sucesso para {nome_arquivo}.rar")

                if processo.returncode == 0:
                    
                    logger.info("Processo de compactação finalizado!")

                    return True
                
                else:
                
                    logger.error(f"{funcao_atual} - Erro ao executar compactação: {processo}")
                
        elif os.path.exists("sig.war"):

            logger.info(f"{funcao_atual} - arquivo sig.war encontrado")
            
        else:

            logger.error("Arquivo não encontrado, adicione e tente novamente.")
            return False

    except Exception as exception:
        
        logger.error(f"{funcao_atual} - {exception}")

async def disponibilizar_arquivo(caminho_arquivo, tipo):

    funcao_atual = inspect.currentframe().f_code.co_name

    try:

        logger.info(f"Caminho recebido: {caminho_arquivo}")

        arquivos_rar = []
        lista_arquivos = os.listdir(caminho_arquivo)
        
        for arquivo in lista_arquivos:
            if arquivo.endswith(".rar"):
                arquivos_rar.append(arquivo)
        
        if arquivos_rar:
        
            logger.info(f"Arquivo que sera disponibilizado: {arquivos_rar}")
            
            os.chdir(caminho_arquivo)
            diretorio_atual = os.getcwd()

            logger.info(f"Diretorio atual: {diretorio_atual}")

            while True:

                processo = await asyncio.create_subprocess_shell(f"mv {arquivos_rar[0]} /repo/disponibilizar_arquivos/arquivos_build/{tipo}", stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
                await processo.communicate()
                
                if processo.returncode == 0:
                    
                    logger.info("Arquivo movido com exitô!")

                    return True

        else:

            logger.error("'Arquivo .rar' não encontrado, adicione e tente novamente.")

    except Exception as exception:
        
        logger.error(f"{funcao_atual} - {exception}")
