#!/usr/bin/python3

import subprocess
import platform
import asyncio
import inspect
import discord
import random
import os

from datetime import datetime
from dotenv import load_dotenv
from discord.ext import commands, tasks
from discord.ext.commands import Bot
from discord.errors import GatewayNotFound

import resource.projeto as projeto
import config.config as config
import util.logger as logger
import util.regex as regex

# Setup loggers
logger = logger.setup_logger("discord_bot", "discord.log")

# Setup bot
bot = Bot
config = config.load_config()
bot.config = config

# Load variaveis .env
load_dotenv()

intents = discord.Intents.all()

bot = Bot(
    command_prefix=commands.when_mentioned_or(config["prefix"]),
    intents=intents,
    help_command=None,
)

# Diretório do projeto Java
diretorio_projeto = os.getenv("DIRETORIO_PROJETO")
diretorio_sig = os.getenv("DIRETORIO_SIG")
diretorio_funcoes = os.getenv("DIRETORIO_FUNCOES")
arquivo_sig = os.getenv("ARQUIVO_SIG")
arquivo_funcoes = os.getenv("ARQUIVO_FUNCOES")
caminho_properties = os.getenv("CAMINHO_PROPERTIES")
caminho_properties_sig = os.getenv("CAMINHO_PROPERTIES_SIG")
caminho_properties_funcoes = os.getenv("CAMINHO_PROPERTIES_FUNCOES")

@bot.event
async def on_ready():
   
    logger.info(f"Conectado com {bot.user.name}!")
    logger.info(f"Versão API discord.py: {discord.__version__}")
    logger.info(f"Versão Python: {platform.python_version()}")
    logger.info(f"Rodando na plataforma: {platform.system()} {platform.release()} ({os.name})")
    logger.info("-------------------")

    if config["sync_commands_globally"]:
        logger.info("Sincronizado com comandos globais...")
        await bot.tree.sync()

        statuses = ["com outros bots.", "Paciência!", "com humanos!"]

        await bot.change_presence(activity=discord.Game(random.choice(statuses)))

@bot.event
async def on_disconnect():

    try:

        logger.info("Bot desconectado. Reconectando...")
        await bot.login(bot.token)
        await bot.connect()

    except Exception as exception:

        logger.error(f"{exception}")

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
        
        await contexto.send(f"Branch atual:\n     └> {listabranch}")
        
        logger.info(f"{funcao_atual} - Branch atual: {listabranch.split()}")
    
    except Exception as exception:

        logger.error(f"{funcao_atual} - {exception}")

@bot.command(name='gerar-versao-sig')
async def gerar_versao_sig(contexto):

    await bot.change_presence(activity=discord.Game('Build da aplicação Sig iniciada!'))
 
    funcao_atual = inspect.currentframe().f_code.co_name
    nome_usuario = contexto.author.name
    
    try:
        
        await contexto.send(f'**Iniciando processos para build...**')
        await contexto.send(f'Requerente: **{nome_usuario}**')

        ambiente = await projeto.configurar_ambiente(diretorio_projeto, diretorio_sig)
            
        if ambiente == True: 
           
            await contexto.send(f"Ambiente configurado!")
            
            versao = await projeto.versionamento_sig()

            await contexto.send(f"Versão atual: {versao[0]}\n     └> Versão que sera gerada: {versao[1]}")

            await contexto.send(f"Cache atual: {versao[2]}\n     └> Cache da versão que sera gerada: {versao[3]}")      
    
            await contexto.send(f"Iniciando Clean do repositorio...\n     └> Apagando as versões geradas anteriormente...")
            
            processando_clean = asyncio.create_task(projeto.gradle_clean())
            
            await status_processamento(contexto, processando_clean, 20)

            resultado_clean = await processando_clean
            
            if resultado_clean.returncode == 0:
                
                await contexto.send(f"Processo 'gradle clean' executado com êxito!\nIniciando empacotamento da aplicação...\n     └> Gerando build do projeto sig.")

                processando_war = asyncio.create_task(projeto.gradle_war())

                await status_processamento(contexto, processando_war, 120)
                
                resultado_gradle_war, processo_war = await processando_war

                formata_resultado_gradle_war = await regex.regex_saida_war(str(resultado_gradle_war))

                if processo_war.returncode == 0:

                    await bot.change_presence(activity=discord.Game('Build da aplicação finalizado!'))

                    await contexto.send(f"Processo de build executado com êxito! \nSaida gradle war(Processo que gera o pacote .war): \n     └> {formata_resultado_gradle_war}")

                    await contexto.send(f"\nIniciando adionar properties. \n\n")

                    caminho_war = arquivo_sig  + "/sig.war"

                    processando_adionar_properties = asyncio.create_task(projeto.adicionar_properties(caminho_war, caminho_properties_sig, caminho_properties))

                    processo_properties = await processando_adionar_properties

                    if processo_properties:

                        await contexto.send(f"Processo que adiciona o arquivo .properties finalizado!")
                        logger.info(f"Processo que adiciona o arquivo .properties foi realizado!")

                        await contexto.send(f" \nProcesso de compactação Iniciado...")

                        data_atual = datetime.now()
                        data_formatada = data_atual.strftime("%d-%m-%Y")
                        nome_sig = str(f"SIG-{versao[1]}-{data_formatada}")

                        processando_compactar_versao = asyncio.create_task(projeto.compactar_arquivo(arquivo_sig, nome_sig))

                        await status_processamento(contexto, processando_compactar_versao, 3)

                        processo_compactacao = await processando_compactar_versao

                        if processo_compactacao:

                            await contexto.send(f"Processo de compactação finalizado!")
                            logger.info(f"Processo de compactação finalizado!")

                            processando_upload_arquivo = asyncio.create_task(projeto.disponibilizar_arquivo(arquivo_sig, "sig"))

                            processo_upload = await processando_upload_arquivo

                            if processo_upload:

                                await bot.change_presence(activity=discord.Game('Arquivo disponibilizados com exitô.'))

                                await contexto.send(f"Processo de upload finalizado!")
                                await contexto.send(f"Link: [Download Sig](http://localhost:9200/sig/)\n")
                                logger.info(f"Processo de upload foi realizado com sucesso!")

                            else:

                                await contexto.send(f"ERROR - upload não foi realizado!")
                                logger.info(f"Processo de upload não foi realizado!")

                    else:

                        await contexto.send(f"ERROR - adionar arquivo .properties não foi realizado!")
                        logger.info(f"Processo adionar arquivo .properties não foi realizado!")
                
    except Exception as exception:
        
        logger.error(f'{funcao_atual} - {exception}') 

@bot.command(name='gerar-versao-funcoes')
async def gerar_versao_funcoes(contexto):

    await bot.change_presence(activity=discord.Game('Build da aplicação Funções iniciada!'))
 
    funcao_atual = inspect.currentframe().f_code.co_name
    nome_usuario = contexto.author.name

    await contexto.send('Deseja alterar a versão do funções? \n     └> Por favor, digite "sim" para iniciar o processo.')

    def check(m):
        return m.channel == contexto.channel and m.author == contexto.author and m.content.lower() == 'sim'

    try:
       
        resposta = await bot.wait_for('message', check=check, timeout=60) 

        await contexto.send('Iniciando o processo...')
        
        await contexto.send(f'**Iniciando processos para build...**')
        await contexto.send(f'Requerente: **{nome_usuario}**')

        ambiente = await projeto.configurar_ambiente(diretorio_projeto, diretorio_funcoes)
            
        if ambiente: 
           
            await contexto.send(f"Ambiente configurado!") 

            versao_atual, data_atual = await projeto.versao_atual_funcoes()
            data_atualizada = await projeto.versionamento_funcoes()

            await contexto.send(f"Versão atual: {versao_atual}\n     └> Versão que sera gerada: {versao_atual}")

            await contexto.send(f"Data atual: {data_atual}\n     └> Data atual da versão que sera gerada: {data_atualizada}") 

            await contexto.send(f"Iniciando Clean do repositorio...\n     └> Apagando as versões geradas anteriormente...")
            
            processando_clean = asyncio.create_task(projeto.gradle_clean())
            
            await status_processamento(contexto, processando_clean, 3)

            resultado_clean = await processando_clean
            
            if resultado_clean.returncode == 0:
                
                await contexto.send(f"Processo 'gradle clean' executado com êxito!\nIniciando empacotamento da aplicação...\n     └> Gerando build do projeto funções.")

                processando_war = asyncio.create_task(projeto.gradle_war())

                await status_processamento(contexto, processando_war, 10)
                
                resultado_gradle_war, processo_war = await processando_war

                formata_resultado_gradle_war = await regex.regex_saida_war(str(resultado_gradle_war))

                if processo_war.returncode == 0:

                    await contexto.send(f"Processo de build executado com êxito! \nSaida gradle war(Processo que gera o pacote .war): \n     └> {formata_resultado_gradle_war}")

                    await contexto.send(f"Adicionando arquivo .properties! \n\n")

                    caminho_war = arquivo_funcoes  + "/sigpwebfuncoes.war"

                    processando_adionar_properties = asyncio.create_task(projeto.adicionar_properties(caminho_war, caminho_properties_funcoes, caminho_properties))

                    processo_properties = await processando_adionar_properties

                    if processo_properties:

                        await contexto.send(f"Processo que adiciona o arquivo .properties finalizado!")
                        logger.info(f"Processo que adiciona o arquivo .properties foi realizado!")

                        await contexto.send(f" \nProcesso de compactação Iniciado...")

                        nome_funcoes = f"Funcao-v.{versao_atual}-{data_atualizada}"
                        nome_funcoes = str(nome_funcoes)

                        processando_compactar_versao = asyncio.create_task(projeto.compactar_arquivo(arquivo_funcoes, nome_funcoes))

                        await status_processamento(contexto, processando_compactar_versao, 3)

                        processo_compactacao = await processando_compactar_versao

                        if processo_compactacao:
                            
                            await contexto.send(f"Processo de compactação finalizado!")

                            await contexto.send(f"Iniciando upload. \n\n")

                            processando_upload_arquivo = asyncio.create_task(projeto.disponibilizar_arquivo(arquivo_funcoes, "sigpwebfuncoes"))

                            processo_upload = await processando_upload_arquivo

                            if processo_upload:

                                await contexto.send(f"Processo de upload finalizado!")
                                await contexto.send(f"Link: [Download Funções](http://localhost:9200/sigpwebfuncoes/)\n")
                                logger.info(f"Processo de upload realizado!") 
                            else:

                                await contexto.send(f"ERROR - upload não foi realizado!")
                                logger.info(f"Processo de upload não foi realizado!")

                        else:

                            await contexto.send(f"Processo de compactação não foi realizado!")

                    else:

                        await contexto.send(f"ERROR - adionar arquivo .properties não foi realizado!")
                        logger.info(f"Processo adionar arquivo .properties não foi realizado!")

    except Exception as exception:
        
        logger.error(f'{funcao_atual} - {exception}') 

@bot.command(name='comandos')
async def comandos(contexto):
    await contexto.send(
    f"""
    Menu de comandos:
    
    **1 - !branch**
             |
            └> Verifica branch atual!
    
    **2 - !mudar-branch nome_da_branch**
             |
            └> Muda para a branch selecionada! (Exemplo: !mudar-branch master)
    
    **3 - !gerar-versao-sig**
             |
            └>  Gera versão da aplicação sig!
    
    **4 - !gerar-versao-funcoes**
             |
            └> Gera versão da aplicação funções
    """)

@bot.command(name='sobre')
async def sobre(contexto):
    await contexto.send('Bot feito com a intenção de automatizar o build da aplicação SIG,\nCriação: 02/06/2023, \nCriado e mantido por: Pablo Soares!')

@bot.event
async def on_message(message):
    
    funcao_atual = inspect.currentframe().f_code.co_name

    from util.traduzir import traduzir_texto

    if message.author != bot.user:

        conteudo = message.content

        logger.info(f"Conteudo: {conteudo}")

        if conteudo.startswith(config["prefix"]):

            partes = conteudo.split(' ') 
            comando = partes[0][len(config["prefix"]):]

            resposta = "iniciando sistemas...\n"
            await message.channel.send(resposta)

            logger.info(f"Comando recebido: {comando}")
            
            try:
            
                if comando == 'mudar-branch':

                    branch = partes[1]
                    
                    await message.channel.send('\nCheckout iniciado...')
                    await message.channel.send(f'Mudando para a branch:\n     └> {branch}')
                    
                    processo_checkout = await projeto.checkout(branch, diretorio_projeto)
                    resultado_checkout = await regex.regex_git_checkout(processo_checkout)
                    
                    if resultado_checkout.returncode == 0:

                        logger.info(f"{funcao_atual} - Stderr: {resultado_checkout.stderr}")

                        await message.channel.send(f"Branch Alterada:\n     └> {resultado_checkout.stderr}\n\n")
                        await message.channel.send("Sucesso na alteração da branch!")

                    elif resultado_checkout.returncode == 1:
                    
                        logger.error(f"{resultado_checkout.stderr}")
                        await message.channel.send(f"Falha ao alterar a branch - {resultado_checkout.stderr}")
                
            except Exception as exception:

                logger.error(f"{funcao_atual} - {exception}")
       
    await bot.process_commands(message)

async def status_processamento(contexto, procesamento, tempo):
    
    while not procesamento.done():
            logger.info("Processando...")
            await contexto.send("Executando o processo...")
            await asyncio.sleep(tempo)
    
try:

    bot.run(config["token"])

except GatewayNotFound as exeption:

    logger.warnning(f"{exeption}")