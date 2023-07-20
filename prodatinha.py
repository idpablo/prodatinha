#!/usr/bin/python3

import subprocess
import platform
import asyncio
import inspect
import discord
import random
import os

from datetime import datetime
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
diretorio_projeto = "/repo/sig"
diretorio_sig = "/repo/sig/sig"
diretorio_funcoes = "/repo/sig/sigpwebfuncoes"
arquivo_sig = "/repo/sig/sig/build/libs"
arquivo_funcoes = "/repo/sig/sigpwebfuncoes/build/libs/"
diretorio_json = "/repo/sig/sig/WebContent/version.json"

@bot.event
async def on_ready():
    
    bot.logger.info(f"Conectado com {bot.user.name}!")
    bot.logger.info(f"Versão API discord.py: {discord.__version__}")
    bot.logger.info(f"Versão Python: {platform.python_version()}")
    bot.logger.info(f"Rodando na plataforma: {platform.system()} {platform.release()} ({os.name})")
    bot.logger.info("-------------------")

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
        
        logger.error(f"{funcao_atual} - {exception}")

@bot.event
async def on_command_error(ctx, error):
    
    funcao_atual = inspect.currentframe().f_code.co_name

    try:    
        if isinstance(error, commands.CommandNotFound):
            await ctx.send("Comando não encontrado.")
        else:
            raise error
    
    except Exception as exception:
        
          logger.error(f"{funcao_atual} - {exception}")

@bot.command(name='branch')
async def branch(contexto):

    funcao_atual = inspect.currentframe().f_code.co_name

    try:

        os.chdir(diretorio_projeto)
        
        diretorio_atual = os.getcwd()
        arquivos = os.listdir(diretorio_projeto)

        await contexto.send(f"Diretorio: {diretorio_atual}")
    
        listabranch = (subprocess.run(["bash", "-c", "git branch"], capture_output=True, text=True)).stdout.strip()
        
        await contexto.send(f"Branch atual >>> \n{listabranch}")
        
        bot.logger.info(f"{funcao_atual} - Branch atual: {listabranch.split()}")
    
    except Exception as exception:

        bot.logger.error(f"{funcao_atual} - {exception}")

@bot.command(name='gerar-versao-sig')
async def gerar_versao_sig(contexto):

    await bot.change_presence(activity=discord.Game('Build da aplicação Sig iniciada!'))
 
    funcao_atual = inspect.currentframe().f_code.co_name
    nome_usuario = contexto.author.name
    
    try:
        
        await contexto.send(f'**Iniciando processos para build...**')
        await contexto.send(f'Requerente: {nome_usuario}.')

        ambiente = await projeto.configurar_ambiente(bot, diretorio_projeto, diretorio_sig)
            
        if ambiente == True: 
           
            await contexto.send(f"Ambiente configurado!")
            
            versao = await projeto.versionamento_sig(bot)

            await contexto.send(f"Versão atual: {versao[0]}\n     └> Versão que sera gerada: {versao[1]}")

            await contexto.send(f"Cache atual: {versao[2]}\n     └> Cache atual da versão que sera gerada: {versao[3]}")      
    
            await contexto.send(f"Iniciando Clean do repositorio...\n     └> Apagando as versões geradas anteriormente...")
            
            processo_clean = await projeto.gradle_clean(bot)
            stdout, stderr = await processo_clean.communicate()

            bot.logger.info(f'{funcao_atual} - stdout:{stdout}')
            bot.logger.info(f'{funcao_atual} - stderr:{stderr}')
            
            while processo_clean.returncode is None:
                bot.logger.info("Procesando...")
                await contexto.send("Executando o processo...")
                await asyncio.sleep(3)
            
            if processo_clean.returncode == 0:
                
                await contexto.send(f"Processo 'gradle clean' executado com êxito! \n\nIniciando empacotamento da aplicação...")

                resultado_gradle_war, processo_war = await projeto.gradle_war(bot)
                fomatado_resultado_gradle_war = await regex.regex_saida_war(bot, str(resultado_gradle_war))

                while processo_clean.returncode is None:
                    bot.logger.info("Procesando...")
                    await contexto.send("Executando o processo...")
                    await asyncio.sleep(3)

                if processo_war.returncode == 0:

                    await contexto.send(f"Processo de build executado com êxito! \nSaida gradle war(Processo que gera o pacote .war): \n     └> {fomatado_resultado_gradle_war}")

                await contexto.send(f" \nProcesso de compactação Iniciado...")

                data_atual = datetime.now()
                data_formatada = data_atual.strftime("%d-%m-%Y")
                nome_sig = f"SIG-{versao[1]}-{data_formatada}"

                compactar_versao = await projeto.compactar_arquivo(bot, arquivo_sig, f"{nome_sig}")

                if compactar_versao:
                    
                    await contexto.send(f"Processo de compactação finalizado!")
                else:

                    await contexto.send(f"Processo de compactação não foi realizado!")

    except Exception as exception:
        
        bot.logger.error(f'{funcao_atual} - {exception}') 

@bot.command(name='gerar-versao-funcoes')
async def gerar_versao_sig(contexto):

    await bot.change_presence(activity=discord.Game('Build da aplicação Funções iniciada!'))

    await projeto.versionamento_funcoes(bot)
 
    funcao_atual = inspect.currentframe().f_code.co_name
    nome_usuario = contexto.author.name
    
    try:
        
        await contexto.send(f'Iniciando processos para build funcoes.')
        await contexto.send(f'Requerente: {nome_usuario}.')

        ambiente = await projeto.configurar_ambiente(bot, diretorio_projeto, diretorio_funcoes)
            
        if ambiente == True: 
           
            await contexto.send(f"Ambiente configurado >>>")
    
            processo_clean = await projeto.gradle_clean(bot)
            
            while processo_clean.returncode is None:
                bot.logger.info("Procesando...")
                await contexto.send("Executando o processo...")
                await asyncio.sleep(3)
            
            if processo_clean.returncode == 0:
                
                await contexto.send(f"\n\nProcesso 'gradle clean' executado com exito >>> ")
                await contexto.send(f"Iniciando empacotamento da aplicação >>> ")

                processo_war = await projeto.gradle_war(bot)

                while processo_war.returncode is None:
                    bot.logger.info("Procesando...")
                    await contexto.send("Executando o processo...")
                    await asyncio.sleep(3) 

                if processo_war.returncode == 0:
                    
                    await contexto.send(f"\nProcesso de build executado com exito >>> ")
                    
                    await contexto.send(f"\nSaida gradle war(gerando package .war): \n\n")
                    # await contexto.send(f"{fomatado_resultado_gradle_war}") 

                    data_atual = datetime.now()
                    data_formatada = data_atual.strftime("%d-%m-%Y")
                    nome_funcoes = f"Funcao-v.{data_formatada}"

                    compactar_versao = await projeto.compactar_arquivo(bot, arquivo_sig, nome_funcoes)

                if compactar_versao:

                    await contexto.send(f"Processo de compactação finalizado!")

    except Exception as exception:
        
        bot.logger.error(f'{funcao_atual} - {exception}') 

@bot.command(name='compactar')
async def compactar(contexto):

    funcao_atual = inspect.currentframe().f_code.co_name

    try:

        versao = "2.5.235"
       
        compactar_versao = await projeto.compactar_arquivo(bot, arquivo_sig, f"SIG-{versao}")

        if compactar_versao:

            await contexto.send(f"Processo de compactação finalizado!")

    except Exception as exception:

        bot.logger.error(f'{funcao_atual} - {exception}')

@bot.command(name='upload')
async def upload_war(contexto):

    funcao_atual = inspect.currentframe().f_code.co_name

    try:
        await contexto.send(f"\nIniciando Upload: \n\n")

        if not os.path.isfile(arquivo_sig):
            await contexto.send("Arquivo sig.war não encontrado.")
            return
        else:

            task = await upload.fazer_upload_arquivo(arquivo_sig, 'sig', 'sig')

            await contexto.send(f"Upload concluído. Link \n\n{task}")

    except Exception as exception:

        bot.logger.error(f'{funcao_atual} - {exception}') 

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

    if message.author != bot.user:

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
                    await message.channel.send(f'Mudando para a branch:\n     └> {branch}')
                    
                    processo_checkout = await projeto.checkout(bot, branch, diretorio_projeto)
                    resultado_checkout = await regex.regex_git_checkout(bot, processo_checkout)
                    
                    if resultado_checkout.returncode == 0:

                        bot.logger.info(f"{funcao_atual} - Stderr: {resultado_checkout.stderr}")

                        await message.channel.send(f"Branch Alterada:\n     └> {resultado_checkout.stderr}\n\n")
                        await message.channel.send("Sucesso na alteração da branch!")

                    elif resultado_checkout.returncode == 1:
                    
                        bot.logger.error(f"{resultado_checkout.stderr}")
                        await message.channel.send(f"Falha ao alterar a branch - {resultado_checkout.stderr}")
                
            except Exception as exception:

                bot.logger.error(f"{funcao_atual} - {exception}")
       
    await bot.process_commands(message)
    
try:

    bot.run(config["token"])

except GatewayNotFound as exeption:

    bot.logger.warnning(f"{exeption}")