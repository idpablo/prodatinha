#!/usr/bin/python3

import os
import re
import sys
import json
import asyncio
import inspect
import subprocess

from datetime import datetime
import util.traduzir as traduzir

async def checkout(bot, branch, diretorio_projeto):
    
    try:

        funcao_atual = inspect.currentframe().f_code.co_name

        os.chdir(diretorio_projeto)
        diretorio_atual = os.getcwd()

        bot.logger.info(f'Mudando para a branch --> {branch}')
        bot.logger.info(f"Diretorio: {diretorio_atual}")

        mudar_branch = subprocess.run(["bash", "-c", f"git checkout {branch}"], capture_output=True)
        mudar_branch = str(mudar_branch)

        if mudar_branch.find("Your branch is up to date with"):
            bot.logger.info("Branch Alterada com sucesso!")

        return(mudar_branch)
    
    except Exception as exeption:
        
        bot.logger.error(f"{funcao_atual} - {exeption}")
        return("Erro ao alterar branch")

async def versionamento_sig(bot):

    funcao_atual = inspect.currentframe().f_code.co_name
    diretorio_json = "/repo/sig/sig/WebContent/version.json"

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

                bot.logger.info(f"Versão Atual: {versaosig}")

                cache_atual = version["cache"]
                cache = int(version["cache"])
                cache_novo = cache + 1

                bot.logger.info(f"Cache Atual: {cache_novo}")
            
            version['versaosig'] = versaosig
            version['cache'] = cache_novo

            with open(diretorio_json, 'w') as arquivo:
                json.dump(version, arquivo, indent=4)
            
            return versao_atual, versaosig, cache_atual, cache_novo
    
    except Exception as exception:

        bot.logger.error(f"{funcao_atual} - {exception}")

async def versionamento_funcoes(bot):

    funcao_atual = inspect.currentframe().f_code.co_name
    caminho_arquivo = r"/repo/sig/sigpwebfuncoes/src/servico/setup/VersaoSigpWebFuncoes.java"

    try:
    
        nova_versao = "2023.07.08"
        nova_data = "08/07/2023 - 11:00"

        with open(caminho_arquivo, 'r') as arquivo:
            conteudo = arquivo.read()

        conteudo = re.sub(r'public static String VERSAO = "[^"]+";', f'public static String VERSAO = "{nova_versao}";', conteudo)
        conteudo = re.sub(r'public static String DATA = "[^"]+";', f'public static String DATA = "{nova_data}";', conteudo)

        with open(caminho_arquivo, 'w') as arquivo:
            arquivo.write(conteudo)

    except Exception as exception:

        bot.logger.error(f"{funcao_atual} - {exception}")


async def configurar_ambiente(bot, diretorio_projeto, diretorio_sig):

    funcao_atual = inspect.currentframe().f_code.co_names

    try:

        if not os.path.isdir(diretorio_projeto):
            bot.logger.info(f"Diretório inválido: {diretorio_projeto}")
            return

        os.chdir(diretorio_projeto)

        diretorio_atual = os.getcwd()
        bot.logger.info(f"Diretório atual: {diretorio_atual}")

        if diretorio_atual != diretorio_projeto:
            bot.logger.info(f"Diretório incorreto. Esperado: {diretorio_projeto}")
            return

        resultado_pull = subprocess.run(["bash", "-c", 'git pull'], capture_output=True, text=True)
        
        if resultado_pull.returncode == 0:
            bot.logger.info(f"Resultado git pull: {resultado_pull.stdout.strip()}")
        else:
            
            bot.logger.error(f"Erro ao executar git pull: {resultado_pull.stderr.strip()}")

        if not os.path.isdir(diretorio_sig):
            bot.logger.info(f"Diretório inválido: {diretorio_sig}")
            return

        os.chdir(diretorio_sig)

        diretorio_atual_sig = os.getcwd()
        bot.logger.info(f"Diretório atual (sig): {diretorio_atual_sig}")

        if diretorio_atual_sig != diretorio_sig:
            bot.logger.info(f"Diretório incorreto. Esperado: {diretorio_sig}")
            return
        
        return True;

    except Exception as exception:
        bot.logger.error(f"{funcao_atual} - { exception}")

async def gradle_clean(bot):
    try:
        funcao_atual = inspect.currentframe().f_code.co_name

        bot.logger.info("Iniciando clean do projeto")

        while True:

            processo = await asyncio.create_subprocess_shell('gradle clean', stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
            stdout, stderr = await processo.communicate() 

            if processo.returncode == 0:
                bot.logger.info(f"Sucesso ao executar gradle clean")
                return processo
            else:
                bot.logger.error(f"Erro ao executar o gradle clean.")

    except Exception as exception:
        bot.logger.error(f"{funcao_atual} - {exception}")
        await asyncio.sleep(5)

async def gradle_war(bot):
    
    funcao_atual = inspect.currentframe().f_code.co_name

    try:
        
        bot.logger.info("Iniciando build do projeto")

        while True:

            processo = await asyncio.create_subprocess_shell('gradle war', stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
            stdout, stderr = await processo.communicate()

            if processo.returncode == 0:
                bot.logger.info(f"Sucesso ao executar gradle war")
                return stdout.decode(), processo
            else:
                bot.logger.error(f"Erro ao executar o gradle war: {stderr.decode()}")

    except Exception as exception:

        bot.logger.error(f"{funcao_atual} - {exception}")
        await asyncio.sleep(5)

async def compactar_arquivo(bot, caminho_arquivo, nome_arquivo):

    funcao_atual = inspect.currentframe().f_code.co_name

    try:

        bot.logger.info(f"{funcao_atual} - caminho recebido: {caminho_arquivo}")
        bot.logger.info(f"{funcao_atual} - nome arquivo recebido: {nome_arquivo}")

        os.chdir(caminho_arquivo)
        diretorio_atual = os.getcwd()

        bot.logger.info(f"{funcao_atual} - diretorio atual: {diretorio_atual}")

        if os.path.exists("sig"):

            os.rename("sig", "sig.war")
        
        elif os.path.exists("sig.war"):

            while True:

                processo = await asyncio.create_subprocess_shell(f"rar a {nome_arquivo}.rar sig.war ", stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
                await processo.communicate()

                if processo.returncode == 0:
                    
                    bot.logger.info("Processo de compactação finalizado!")

                    return True

        else:

            bot.logger.error("'sig.war' não encontrado, adicione e tente novamente.")
            return False


    except Exception as exception:
         
         bot.logger.error(f"{funcao_atual} - {exception}")

async def disponibilizar_arquivo(bot, caminho_arquivo, tipo):

    funcao_atual = inspect.currentframe().f_code.co_name

    try:

        bot.logger.info(f"{funcao_atual} - caminho recebido: {caminho_arquivo}")

        arquivos_rar = []
        lista_arquivos = os.listdir(caminho_arquivo)
        
        for arquivo in lista_arquivos:
            if arquivo.endswith(".rar"):
                arquivos_rar.append(arquivo)
        
        if arquivos_rar:
        
            bot.logger.info(f"Arquivo que sera disponibilizado: {arquivos_rar}")
            
            os.chdir(caminho_arquivo)
            diretorio_atual = os.getcwd()

            bot.logger.info(f"{funcao_atual} - diretorio atual: {diretorio_atual}")

            while True:

                processo = await asyncio.create_subprocess_shell(f"mv {arquivos_rar[0]} /repo/disponibilizar-arquivos/arquivos_build/{tipo}", stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
                await processo.communicate()
                
                if processo.returncode == 0:
                    
                    bot.logger.info("Arquivo movido com exitô!")

                    return True

        else:

            bot.logger.error("'Arquivo .rar' não encontrado, adicione e tente novamente.")

    except Exception as exception:
         
         bot.logger.error(f"{funcao_atual} - {exception}")