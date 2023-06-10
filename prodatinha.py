import subprocess
import platform
import random
import json
import sys
import os

import discord
from discord.ext import commands, tasks
from discord.ext.commands import Bot, Context

from projeto import atualizar_projeto
from traduzir import traduzir_texto
from logger import setup_logger
from regex import regex

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

# Setup loggers
logger = setup_logger("discord_bot", "discord.log")
logerror = setup_logger("discord_bot_error", "discord.log")

bot.logger = logger
bot.logerror = logerror
bot.config = config

# Diretório do projeto Java
diretorio_projeto = "C:/prodata/sig"
diretorio_sig = "C:/prodata/sig/sig"

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
    
        os.chdir(diretorio_projeto)
        
        diretorio_atual = os.getcwd()
        arquivos = os.listdir(diretorio_projeto)

        listabranch = (subprocess.run("git branch", capture_output=True, text=True)).stdout.strip()

        await contexto.send(f"Diretorio: {diretorio_atual}")
        await contexto.send(f"Branch atual >>> \n{listabranch}")
        bot.logger.info(f"Branch atual: {listabranch.split()}")
    
    except Exception as exception:

        bot.logerror.error(f"ERROR - {exception}")

@bot.command(name='gerar-versao-sig')
async def gerar_versao_sig(contexto):
    bot.logger.info('Iniciando processo de build.')

    # Chamar a função para atualizar o projeto
    await atualizar_projeto(bot, diretorio_projeto, diretorio_sig)

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

            resposta = "iniciando sistemas...\n"
            await message.channel.send(resposta)

            bot.logger.info(f"Comando recebido: {comando}")  # Adiciona um print para exibir o comando recebido
            
            try:
            
                if comando == 'mudar-branch':
                    
                    await message.channel.send('Checkout iniciado...')
                    
                    branch = partes[1]
                    processo = await checkout(branch)
                    resultado = await regex(bot, processo)

                    bot.logger.info(f"Args: {resultado.args}")
                    bot.logger.info(f"Returncode: {resultado.returncode}")
                    bot.logger.info(f"Stderr: {resultado.stderr}")
                    
                    await message.channel.send(f'Mudando para a branch --> {branch}')

                    if resultado.returncode == 0:
            
                        bot.logger.info(f"Branch alterada - {resultado.stderr}")
            
                        await message.channel.send(f"Processamento sendo executado --> {resultado.args}")
                        await message.channel.send(f"Branch Alterada --> {resultado.stderr}\n\n")
                        await message.channel.send("\nSucesso na alteração da branch!")

                    elif resultado.returncode == 1:
                    
                        bot.logerror.error(f"{resultado.stderr}")
                        await message.channel.send(f"Falha ao alterar a branch - {resultado.stderr}")
                 
                elif comando == 'gerar-versao-sig':
                    
                    if os.chdir == diretorio_projeto:

                        atualizar_projeto = subprocess

            except Exception as exception:

                bot.logerror.error(f"ERROR - {exception}")
       
    # Permite que o bot continue processando outros comandos
    await bot.process_commands(message)
    
async def checkout(branch):
    
    try:

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
        bot.logerror.error(f"ERROR - {exeption}")
        return("Erro ao alterar branch")

bot.run(config["token"])
