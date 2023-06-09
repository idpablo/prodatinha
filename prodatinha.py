import subprocess
import platform
import random
import json
import sys
import os
import re

import discord
from discord.ext import commands, tasks
from discord.ext.commands import Bot, Context

if not os.path.isfile(f"{os.path.realpath(os.path.dirname(__file__))}/config.json"):
    sys.exit("'config.json' not found! Please add it and try again.")
else:
    with open(f"{os.path.realpath(os.path.dirname(__file__))}/config.json") as file:
        config = json.load(file)

intents = discord.Intents.all()

bot = Bot(
    command_prefix=commands.when_mentioned_or(config["prefix"]),
    intents=intents,
    help_command=None,
)

from logger import setup_logger

# Setup loggers
logger = setup_logger("discord_bot", "discord.log")
logerror = setup_logger("discord_bot_error", "discord.log")

bot.logger = logger
bot.logerror = logerror
bot.config = config

bot.config = config

# Diretório do projeto Java
diretorio_projeto = "C:/prodata/sig/"

@bot.event
async def on_ready():
    bot.logger.info(f"\nConectado com {bot.user.name}!")
    bot.logger.info(f"Versão API discord.py: {discord.__version__}")
    bot.logger.info(f"Versão Python: {platform.python_version()}")
    bot.logger.info(f"Rodando na plataforma: {platform.system()} {platform.release()} ({os.name})")
    bot.logger.info("-------------------")
    status_task.start()

    if config["sync_commands_globally"]:
        bot.logger.info("Sincronizado com comandos globais...\n")
        await bot.tree.sync()

@tasks.loop(minutes=1.0)
async def status_task() -> None:
    """
    Definindo status do bot.
    """
    statuses = ["Os outros bots.", "Paciência!", "Com humanos!"]
    await bot.change_presence(activity=discord.Game(random.choice(statuses)))

@bot.command(name='branch')
async def branch(contexto):

    try:

        await contexto.send('Consultando branch atual. \n')
    
        os.chdir(diretorio_projeto)
        
        diretorio_atual = os.getcwd()
        arquivos = os.listdir(diretorio_projeto)
        linhas = diretorio_atual.__str__()

        await contexto.send(f"Diretorio Atual: {linhas}")

        #for arquivo in arquivos:
            #await contexto.send(arquivo)

        branch = subprocess.run("git branch", capture_output=True, text=True)

        resultado = branch.stdout.strip()
        bot.logerror.error(f"TESTE")

        await contexto.send(resultado)
    
    except Exception as exception:
        bot.logerror.error(f"ERROR - {exception}")

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
    # Verifica se a mensagem foi enviada por um usuário (exclui mensagens do próprio bot)
    if message.author != bot.user:

        # Acessa o conteúdo da mensagem
        conteudo = message.content

        bot.logger.info(f"Conteudo: {conteudo}")

        if conteudo.startswith(config["prefix"]):

            partes = conteudo.split(' ') 
            comando = partes[0][len(config["prefix"]):]

            # Verificando comunicação com os canais
            resposta = "iniciando processamento!\n"
            await message.channel.send(resposta)

            bot.logger.info(f"Comando recebido: {comando}")  # Adiciona um print para exibir o comando recebido
            
            try:
            
                if comando == 'comando1':
                    await message.channel.send('Executando o comando1!')
                elif comando == 'comando2':
                    await message.channel.send('Executando o comando2!')
                elif comando == 'mudar-branch':
                    
                    await message.channel.send('Processo de checkout iniciado:')
                    
                    branch = partes[1]
                    processo = await checkout(branch)
                    resultado = await regex(processo)

                    bot.logger.info(f"Args: {resultado.args}")
                    bot.logger.info(f"Returncode: {resultado.returncode}")
                    bot.logger.info(f"Stderr: {resultado.stderr}")

                    if resultado.returncode == 0:
                        bot.logger.info("Sucesso na alteração da branch!")

                        message = discord.Message(content='!branch')
                        ctx = await bot.get_context(message)

                        await bot.invoke("ctx")

            except Exception as exception:

                bot.logerror.error(f"ERROR - {exception}")

    # Permite que o bot continue processando outros comandos
    await bot.process_commands(message)
    
async def checkout(branch):
    
    try:

        bot.logger.info(f'Mudando para a branch: {branch}')

        os.chdir(diretorio_projeto)
        
        diretorio_atual = os.getcwd()
        arquivos = os.listdir(diretorio_projeto)
        #diretorio_atual = subprocess.run("dir", capture_output=True, universal_newlines=True, shell=True)
        #linhas = diretorio_atual.__str__()

        bot.logger.info(f"Diretorio Atual: {diretorio_atual}")

        mudar_branch = subprocess.run(f"git checkout {branch}", capture_output=True)
        mudar_branch = str(mudar_branch)

        #jsonbranch = json.dumps(mudar_branch)

        if mudar_branch.find("Your branch is up to date with"):
            bot.logger.info("Branch Alterada com sucesso!")

        #print(mudar_branch)
        #print(jsonbranch)

        #for arquivo in arquivos:
            #await contexto.send(arquivo)

        return(mudar_branch)
    
    except Exception as exeption:
        bot.logerror.error(f"ERROR - {exeption}")
        return("Erro ao alterar branch")

class ResultadoRegex:
    def __init__(self, args, returncode, stdout, stderr):
        self.args = args
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
    
async def regex(texto):

    try:
        args_match = re.search(r"args='(.*?)'", texto)
        args = args_match.group(1) if args_match else ""

        returncode_match = re.search(r"returncode=(\d+)", texto)
        returncode = int(returncode_match.group(1)) if returncode_match else 0

        stdout_match = re.search(r"stdout=b\"(.*?)\"", texto)
        stdout = stdout_match.group(1) if stdout_match else ""

        stderr_match = re.search(r"stderr=b\"(.*?)\"", texto)
        stderr = stderr_match.group(1) if stderr_match else ""

        return ResultadoRegex(args, returncode, stdout, stderr)

    except Exception as exception:
        bot.logerror.error(f'ERROR - {exception}')
        return None

bot.run(config["token"])
