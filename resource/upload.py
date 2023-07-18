#!/usr/bin/python3

import os
import inspect
import asyncio

import util.logger as logger

logger = logger.setup_logger("upload.py", "discord.log")

async def fazer_upload_arquivo(diretorio_arquivo, nome):

    funcao_atual = inspect.currentframe().f_code.co_name

    try:

        os.chdir(diretorio_arquivo, nome)

        if not os.path.isfile(f"{os.path.realpath(os.path.dirname(__file__))}/{nome}"):
             logger.info("'config.json' não encontrado, adicione e tente novamente.")
        else:
            
            processo = await asyncio.create_subprocess_shell('"curl -u "pablosoares:Devflag#8591" -T "/repo/sig/sig/build/libs/SIG-v2.5.199-22-06-2023.rar" "https://owncloud.prodataweb.inf.br/owncloud/index.php/apps/files?dir=/Versoes_Anteriores"', stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
            stdout, stderr = await processo.communicate()

    except Exception as exception:
       
        logger.error(f"{funcao_atual} - {exception}")