#!/usr/bin/python

import os
import sys
import json
import asyncio
import inspect
import subprocess

from util.traduzir import traduzir_texto

async def reconectar_bot(bot):
    
    bot.logger.info("Reconectando o bot...")
    await bot.login(bot.token)
    await bot.connect()

async def versionamento(bot, diretorio_json):
    
    funcao_atual = inspect.currentframe().f_code.co_name

    try:

        if not os.path.isfile(diretorio_json):
            sys.exit("'version.json' não encontrado, adicione e tente novamente.")
        else:
            with open(diretorio_json) as file:
                version = json.load(file)

                return version
    
    except Exception as exception:

        bot.logger.error(f"{funcao_atual} - {exception}")

async def configurar_ambiente(bot, diretorio_projeto, diretorio_sig):

    try:
        funcao_atual = inspect.currentframe().f_code.co_names

        # Verifica se o diretório do projeto existe
        if not os.path.isdir(diretorio_projeto):
            bot.logger.info(f"Diretório inválido: {diretorio_projeto}")
            return

        # Navega até o diretório do projetos
        os.chdir(diretorio_projeto)

        # Verifica o diretório atual é o diretório correto
        diretorio_atual = os.getcwd().replace("\\", "/")
        bot.logger.info(f"Diretório atual: {diretorio_atual}")

        if diretorio_atual != diretorio_projeto:
            bot.logger.info(f"Diretório incorreto. Esperado: {diretorio_projeto}")
            return

        # Executa o comando 'git pull' usando a biblioteca subprocess
        resultado_pull = subprocess.run(['git', 'pull'], capture_output=True, text=True)
        
        if resultado_pull.returncode == 0:
            # Exibe a saída stdout do comando git pull
            bot.logger.info(f"Resultado git pull: {resultado_pull.stdout.strip()}")
        else:
            
            bot.logerror.error(f"Erro ao executar git pull: {resultado_pull.stderr.strip()}")

        # Verifica se o diretório sig existe
        if not os.path.isdir(diretorio_sig):
            bot.logger.info(f"Diretório inválido: {diretorio_sig}")
            return

        # Navega até o diretório sig
        os.chdir(diretorio_sig)

        # Verifica o diretório atual para confirmar se é o diretório correto
        diretorio_atual_sig = os.getcwd().replace("\\", "/")
        bot.logger.info(f"Diretório atual (sig): {diretorio_atual_sig}")

        if diretorio_atual_sig != diretorio_sig:
            bot.logger.info(f"Diretório incorreto. Esperado: {diretorio_sig}")
            return
        
        return True;

    except Exception as exception:
        bot.logerror.error(f"funcao_atual - { exception}")

async def gradle_clean(bot):
    try:
        funcao_atual = inspect.currentframe().f_code.co_name

        saida_build = "Iniciando clean do projeto"
        bot.logger.info(saida_build)

        while True:

            processo = await asyncio.create_subprocess_shell('gradle clean', stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
            stdout, stderr = await processo.communicate()

                # Loop para exibir mensagens de progresso enquanto o processo estiver em andamento
            while processo.returncode is None:
                bot.logger.info("Executando o processo...")
                await asyncio.sleep(10)  # Exibe uma mensagem a cada 10 segundos

            if processo.returncode == 0:
                bot.logger.info(f"Saida do gradle clean: {stdout.decode()}")
                return stdout.decode(), processo
            else:
                bot.logger.error(f"Erro ao executar o gradle clean: {stderr.decode()}")

    except Exception as exception:
        bot.logerror.error(f"{funcao_atual} - {exception}")
        await asyncio.sleep(5)

async def gradle_war(bot):
    try:
        funcao_atual = inspect.currentframe().f_code.co_name

        saida_build = "Iniciando build do projeto"
        bot.logger.info(saida_build)

        while True:

            processo = await asyncio.create_subprocess_shell('gradle war', stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
            stdout, stderr = await processo.communicate()

                # Loop para exibir mensagens de progresso enquanto o processo estiver em andamento
            while processo.returncode is None:
                bot.logger.info("Executando o processo...")
                await asyncio.sleep(10)  # Exibe uma mensagem a cada 10 segundos

            if processo.returncode == 0:
                saida_build = stdout.decode()
                return stdout.decode(), processo
            else:
                bot.logger.error(f"Erro ao executar o gradle war: {stderr.decode()}")

    except Exception as exception:
        bot.logerror.error(f"{funcao_atual} - {exception}")
        await asyncio.sleep(5)