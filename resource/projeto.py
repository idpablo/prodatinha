import os
import asyncio
import inspect
import subprocess

from util.traduzir import traduzir_texto
from config.config import load_config

async def gerar_versao(bot, diretorio_projeto, diretorio_sig):

    config = load_config(bot)

    async def reconectar_bot():
        bot.logger.info("Reconectando o bot...")
        await bot.login(bot.token)
        await bot.connect()

    async def build_gradle():
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
                    await asyncio.sleep(10)  # Exibe uma mensagem a cada 30 segundos

                if processo.returncode == 0:
                    bot.logger.info(f"Saida do build: {stdout.decode()}")
                else:
                    bot.logger.error(f"Erro ao executar o build: {stderr.decode()}")

                return stdout.decode()

        except Exception as exception:
            bot.logerror.error(f"{funcao_atual} - {exception}")
            await asyncio.sleep(5)

    try:
        
        funcao_atual = inspect.currentframe().f_code.co_names

        if not bot.is_ready():
            await reconectar_bot()

        # Verifica se o diretório do projeto existe
        if not os.path.isdir(diretorio_projeto):
            bot.logger.info(f"Diretório inválido: {diretorio_projeto}")
            return

        # Navega até o diretório do projeto
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
        
        # Executa o comando 'gradle clean war' usando a biblioteca subprocess
        resultado_clean = subprocess.run(['gradle', 'clean'], capture_output=True, text=True, shell=True,  check=True)
        
        saida_clean = str(resultado_clean)
        
        if resultado_clean.returncode == 0:

            try:
                saida_build = await build_gradle()
                bot.logger.info(f"Saida: {saida_build}")
                return saida_build
            
            except Exception as exception:
            
                bot.logger.info(f"Erro durante o build do projeto: {exception}")
        else:
            
            bot.logger.info(f"Erro ao executar gradle clean: {saida_clean.stderr.strip()}")

        return(saida_clean, saida_build)
    except Exception as exception:

        bot.logerror.error(f"funcao_atual - { exception}")
        bot.logWarnning.warnning(f"funcao_atual - { exception}")

