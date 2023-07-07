#!/usr/bin/python3

import subprocess
import platform
import inspect
import discord
import random
import os

from discord.ext import commands, tasks
from discord.ext.commands import Bot
from discord.errors import GatewayNotFound

import resource.projeto as projeto
import config.config as config
import resource.upload as upload
import resource.apm as apm
import util.logger as logger
import util.regex as regex

# Setup loggers
logger = logger.setup_logger("discord_bot", "discord.log")

bot = Bot
config = config.load_config(bot)

bot.logger = logger
bot.config = config

intents = discord.Intents.all()

bot = Bot(
    command_prefix=commands.when_mentioned_or(config["prefix"]),
    intents=intents,
    help_command=None,
)

# Diretório do projeto Java
diretorio_projeto = "/repo/prodata/sig"
diretorio_sig = "/repo/prodata/sig/sig"
arquivo_sig = "/repo/prodata/sig/sig/build/libs/sig.war"
diretorio_json = "/repo/prodata/sig/sig/WebContent/version.json"

@bot.event
async def on_ready():
    
    bot.logger.info(f"Conectado com {bot.user.name}!")
    bot.logger.info(f"Versão API discord.py: {discord.__version__}")
    bot.logger.info(f"Versão Python: {platform.python_version()}")
    bot.logger.info(f"Rodando na plataforma: {platform.system()} {platform.release()} ({os.name})")
    bot.logger.info("-------------------")
    status_task.start()

    if config["sync_commands_globally"]:
        bot.logger.info("Sincronizado com comandos globais...\n")
        await bot.tree.sync()

@bot.event
async def on_disconnect():

    try:

        print("Bot desconectado. Reconectando...")
        await bot.login(bot.token)
        await bot.connect()

    except Exception as exception:

        logger.error(f"{exception}")

@tasks.loop(minutes=5.0)
async def status_task() -> None:
    """
    Definindo status do bot.
    """
    try:
        funcao_atual = inspect.currentframe().f_code.co_name

        dados = apm.monitorar_recursos(bot)

        if dados is not None:
            bot.logger.info(f'{funcao_atual} - Status do bot e processamentos:')
            bot.logger.info(f"USO RAM: {dados[-1].uso_ram_mb} MB")
            bot.logger.info(f"USO CPU: {dados[-1].uso_cpu}%")
            bot.logger.info("Processos em execução:")
            
            for proc in dados[-1].processos:
                bot.logger.info(f"PID: {proc['pid']}, Nome: {proc['nome']}, Uso de CPU: {proc['uso_cpu']}%")
                
        statuses = ["com outros bots.", "Paciência!", "com humanos!"]
        
        await bot.change_presence(activity=discord.Game(random.choice(statuses)))
    
    except Exception as exception:
        
        bot.logger.error(f"{funcao_atual} - {exception}")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Comando não encontrado.")
    else:
        raise error

@bot.command(name='branch')
async def branch(contexto):

    funcao_atual = inspect.currentframe().f_code.co_name

    try:
    
        os.chdir(diretorio_projeto)
        
        diretorio_atual = os.getcwd()
        arquivos = os.listdir(diretorio_projeto)

        listabranch = (subprocess.run("git branch", capture_output=True, text=True)).stdout.strip()

        await contexto.send(f"Diretorio: {diretorio_atual}")
        await contexto.send(f"Branch atual >>> \n{listabranch}")
        bot.logger.info(f"{funcao_atual} - Branch atual: {listabranch.split()}")
    
    except Exception as exception:

        bot.logerror.error(f"{funcao_atual} - {exception}")

@bot.command(name='gerar-versao-sig')
async def gerar_versao_sig(contexto):

    await bot.change_presence(activity=discord.Game('Versão sendo gerada!'))
 
    funcao_atual = inspect.currentframe().f_code.co_name
    nome_usuario = contexto.author.name
    
    try:
        
        await contexto.send(f'Iniciando processos para build.')
        await contexto.send(f'Requerente: {nome_usuario}.')

        ambiente = await projeto.configurar_ambiente(bot, diretorio_projeto, diretorio_sig)
            
        if ambiente == True: 
           
            await contexto.send(f"Ambiente configurado >>> \n Load versão atual:")
            
            versao = projeto.versionamento(bot, diretorio_json)

            await contexto.send(f"Versão atual: \n\n{versao}")
            
            
            resultado_gradle_clean, processo_clean = await projeto.gradle_clean(bot)
            await contexto.send(f"Retorno gradle clean(remove versões geradas anteriormente): \n {resultado_gradle_clean}")

            if processo_clean.returncode == 0:
                
                await contexto.send(f"\n\nProcesso 'gradle clean' executado com exito >>> ")
                await contexto.send(f"Iniciando empacotamento da aplicação >>> ")

                resultado_gradle_war, processo_war = await projeto.gradle_war(bot)

                if processo_war.returncode == 0:
                    
                    await contexto.send(f"\nProcesso de build executado com exito >>> ")

                    fomatado_resultado_gradle_war = await regex.regex_saida_war(bot, str(resultado_gradle_war))
                    
                    await contexto.send(f"\nSaida gradle war(gerando package .war): \n\n")
                    await contexto.send(f"{fomatado_resultado_gradle_war}")
                    #for linha in fomatado_resultado_gradle_war:
                        #await contexto.send(f"{linha}")

    except Exception as exception:
        
        bot.logerror.error(f'{funcao_atual} - {exception}') 

@bot.command(name='upload')
async def upload_war(contexto):

    # Verificar se o arquivo existe
    if not os.path.isfile(arquivo_sig):
        await contexto.send("Arquivo sig.war não encontrado.")
        return
    
    task = await upload.upload_arquivo('sig', arquivo_sig)

    await contexto.send(f"Upload concluído. Link \n\n{task}")

    # Aguardar a conclusão do upload e enviar a mensagem de retorno
    #if task.exception() is not None:
        #await contexto.send("Ocorreu um erro durante o upload do arquivo.")
    #else:
        #await contexto.send("Upload concluído.")

    #if link_arquivo:
        #await contexto.send(f"Upload concluído. Aqui está o link do arquivo: {link_arquivo}")
    #else:
        #await contexto.send("Ocorreu um erro durante o upload do arquivo.")

@bot.command(name='ajuda')
async def ajuda(contexto):
    await contexto.send('Menu de Ajuda, \n\n1 - Comandos')

@bot.command(name='mudar-branch')
async def mudar_branch(contexto):
    print('')

@bot.command(name='sobre')
async def sobre(contexto):
    await contexto.send('Bot feito com a intenção de automatizar o build da aplicação SIG,\nCriação: 02/06/2023, \nCriado e mantido por: Pablo Soares!')

@bot.event
async def on_message(message):
    
    funcao_atual = inspect.currentframe().f_code.co_name

    from util.traduzir import traduzir_texto

    # Verifica se a mensagem foi enviada por um usuário (exclui mensagens do próprio bot)
    if message.author != bot.user:

        # Acessa o conteúdo da mensagem
        conteudo = message.content

        bot.logger.info(f"Conteudo: {conteudo}")

        if conteudo.startswith(config["prefix"]):

            partes = conteudo.split(' ') 
            comando = partes[0][len(config["prefix"]):]

            resposta = "iniciando sistemas...\n"
            await message.channel.send(resposta)

            bot.logger.info(f"Comando recebido: {comando}")  # Adiciona um print para exibir o comando recebido
            
            try:
            
                if comando == 'mudar-branch':

                    branch = partes[1]
                    
                    await message.channel.send('\nCheckout iniciado...')
                    await message.channel.send(f'Mudando para a branch --> {branch}')
                    
                    processo_checkout = await checkout(branch)
                    resultado_checkout = await regex.regex_git_checkout(bot, processo_checkout)
                    
                    if resultado_checkout.returncode == 0:

                        bot.logger.info(f"{funcao_atual} - Args: {resultado_checkout.args}")
                        bot.logger.info(f"{funcao_atual} - Returncode: {resultado_checkout.returncode}")
                        bot.logger.info(f"{funcao_atual} - Stderr: {resultado_checkout.stderr}")

                        traducao = resultado_checkout.stderr
                        traducao = await traduzir_texto(traducao.strip(), destino='pt')
                        await message.channel.send(f"Processamento sendo executado --> {resultado_checkout.args}")
                        await message.channel.send(f"Branch Alterada --> {traducao}\n\n")
                        await message.channel.send("\nSucesso na alteração da branch!")

                    elif resultado_checkout.returncode == 1:
                    
                        bot.logerror.error(f"{resultado_checkout.stderr}")
                        await message.channel.send(f"Falha ao alterar a branch - {resultado_checkout.stderr}")
                
            except Exception as exception:

                bot.logger.error(f"{funcao_atual} - {exception}")
       
    # Permite que o bot continue processando outros comandos
    await bot.process_commands(message)
    
async def checkout(branch):
    
    try:

        funcao_atual = inspect.currentframe().f_code.co_name

        os.chdir(diretorio_projeto)
        diretorio_atual = os.getcwd()

        bot.logger.info(f'Mudando para a branch --> {branch}')
        bot.logger.info(f"Diretorio: {diretorio_atual}")

        mudar_branch = subprocess.run(f"git checkout {branch}", capture_output=True)
        mudar_branch = str(mudar_branch)

        if mudar_branch.find("Your branch is up to date with"):
            bot.logger.info("Branch Alterada com sucesso!")

        return(mudar_branch)
    
    except Exception as exeption:
        bot.logger.error(f"{funcao_atual} - {exeption}")
        return("Erro ao alterar branch")
    
try:
    bot.run(config["token"])
except GatewayNotFound as exeption:
    bot.logger.warnning(f"{exeption}")
