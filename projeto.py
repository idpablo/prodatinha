import os
import subprocess

from traduzir import traduzir_texto

async def atualizar_projeto(bot, diretorio_projeto, diretorio_sig):
    # Verifica se o diretório do projeto existe
    if not os.path.isdir(diretorio_projeto):
        bot.logger.info(f"Diretório inválido: {diretorio_projeto}")
        return

    # Navega até o diretório do projeto
    os.chdir(diretorio_projeto)

    # Verifica o diretório atual para confirmar se é o diretório correto
    diretorio_atual = os.getcwd().replace("\\", "/")
    bot.logger.info(f"Diretório atual: {diretorio_atual}")

    if diretorio_atual != diretorio_projeto:
        bot.logger.info(f"Diretório incorreto. Esperado: {diretorio_projeto}")
        return

    try:
        # Executa o comando 'git pull' usando a biblioteca subprocess
        resultado_pull = subprocess.run(['git', 'pull'], capture_output=True, text=True)
        
        if resultado_pull.returncode == 0:
            # Exibe e armazena a saída do comando git pull
            output_pull = await traduzir_texto(resultado_pull.stdout.strip(), destino='pt')
            bot.logger.info(output_pull)
        else:
            bot.logger.info(f"Erro ao executar git pull: {resultado_pull.stderr.strip()}")

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

        bot.logger.info(os.listdir(diretorio_atual_sig))
        
        # Executa o comando 'gradle clean war' usando a biblioteca subprocess
        resultado_build = subprocess.run(['gradle', 'clean', 'war'], capture_output=True, text=True)
        bot.logger.info(resultado_build)

       

        #if resultado_build.returncode == 0:
            # Exibe e armazena a saída do comando gradle clean war
            #output_build = resultado_build.stdout.strip()
            #bot.logger.info(output_build)
        #else:
            #bot.logger.info(f"Erro ao executar gradle clean war: {resultado_build.stderr.strip()}")

    except Exception as exception:
        bot.logger.info(f"Erro durante a atualização do projeto: {exception}")
