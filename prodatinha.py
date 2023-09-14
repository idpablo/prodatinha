import subprocess
import platform
import asyncio
import inspect
import discord
import random
import os

import util.apm as apm
import util.regex as regex
import util.logger as logger
import processamentos.projeto as projeto

from datetime import datetime
from dotenv import load_dotenv
from discord.ext import commands 
from discord.ext.commands import Bot  # pyright: ignore
from discord.errors import GatewayNotFound
from config import config

# Setup loggers
logger = logger.setup_logger("prodatinha.bot")

# Setup bot
bot = Bot
config = config.config.load_config() 
bot.config = config  # pyright: ignore

# Load variaveis .env
load_dotenv()

intents = discord.Intents.all()

bot = Bot(
    command_prefix=commands.when_mentioned_or(config["prefix"]), # pyright: ignore
    intents=intents,
    help_command=None,
)

# Diretório do projeto Java
diretorio_projeto = os.getenv("DIRETORIO_PROJETO")
diretorio_sig = os.getenv("DIRETORIO_ROOT_SIG")
diretorio_funcoes = os.getenv("DIRETORIO_ROOT_FUNCOES")
arquivo_sig = os.getenv("ARQUIVO_SIG_WAR")
arquivo_funcoes = os.getenv("ARQUIVO_FUNCOES_WAR")
caminho_properties = os.getenv("CAMINHO_PROPERTIES_TEMPLATE")
caminho_properties_sig = os.getenv("CAMINHO_PROPERTIES_SIG_WAR")
caminho_properties_funcoes = os.getenv("CAMINHO_PROPERTIES_FUNCOES_WAR")
caminho_disponibilizar_versoes_padrao = os.getenv("CAMINHO_DISPONIBILIZAR_PADRAO_RAR")

@bot.event
async def on_ready():
   
    logger.info(f"Conectado com {bot.user.name}!") # pyright: ignore
    logger.info(f"Versão API discord.py: {discord.__version__}")
    logger.info(f"Versão Python: {platform.python_version()}")
    logger.info(f"Rodando na plataforma: {platform.system()} {platform.release()} ({os.name})")
    logger.info("-------------------")

    if config["sync_commands_globally"]: # pyright: ignore
        logger.info("Sincronizado com comandos globais...")
        await bot.tree.sync()

    await status_bot()

@bot.event
async def on_disconnect():

    try:

        logger.info("Bot desconectado. Reconectando...")
        await bot.login(bot.token) # pyright: ignore
        await bot.connect()

    except Exception as exception:

        logger.error(f"{exception}")

@bot.event
async def on_command_error(contexto, error): # pyright: ignore
    
    funcao_atual = inspect.currentframe().f_code.co_name # pyright: ignore

    try:    
        if isinstance(error, commands.CommandNotFound): # pyright: ignore

            await contexto.send(f"Comando não encontrado.") # pyright: ignore
        else:
            raise error
    
    except Exception as exception:
        
          logger.error(f"{funcao_atual} - {exception}")

@bot.command(name='branch')
async def branch(contexto): # pyright: ignore

    funcao_atual = inspect.currentframe().f_code.co_name # pyright: ignore

    try:

        os.chdir(diretorio_projeto) # pyright: ignore
        
        diretorio_atual = os.getcwd()
        arquivos = os.listdir(diretorio_projeto) # pyright: ignore

        await contexto.send(f"Diretorio: {diretorio_atual}") # pyright: ignore
    
        listabranch = (subprocess.run(["bash", "-c", "git branch"], capture_output=True, text=True)).stdout.strip()
        
        await contexto.send(f"Branch atual:\n\n  {listabranch}\n------------------------------------------------------------") # pyright: ignore
        
        logger.info(f"{funcao_atual} - Branch atual: {listabranch.split()}")
    
    except Exception as exception:

        logger.error(f"{funcao_atual} - {exception}")

@bot.command(name='gerar-versao-sig')
async def gerar_versao_sig(contexto): # pyright: ignore

    await status_bot("Build SIG iniciado!","do_not_disturb")
 
    funcao_atual = inspect.currentframe().f_code.co_name # pyright: ignore
    nome_usuario = contexto.author.name # pyright: ignore

    await contexto.send('Deseja gerar uma nova versão da aplicação SIG? \n     └> Por favor, digite "sim" para iniciar o processo.') # pyright: ignore

    def check(m): # pyright: ignore
        return m.channel == contexto.channel and m.author == contexto.author and m.content.lower() == 'sim' # pyright: ignore
    
    try:

        await bot.wait_for('message', check=check, timeout=60)  # pyright: ignore
           
        
        await contexto.send(f'**Iniciando processos para build...**') # pyright: ignore
        await contexto.send(f'Requerente: **{nome_usuario}**') # pyright: ignore

        processo_config_ambiente = await projeto.configurar_ambiente(diretorio_projeto, diretorio_sig) # pyright: ignore
            
        if processo_config_ambiente == True: 

            await contexto.send(f"Ambiente configurado!") # pyright: ignore
            
            versao = await projeto.versionamento_sig()

            await contexto.send(f"Versão atual: {versao[0]}\n     └> Versão que sera gerada: {versao[1]}") # pyright: ignore

            await contexto.send(f"Cache atual: {versao[2]}\n     └> Cache da versão que sera gerada: {versao[3]}") # pyright: ignore
    
            await contexto.send(f"Iniciando Clean do repositorio...\n     └> Apagando as versões geradas anteriormente...") # pyright: ignore
            
            processando_clean = asyncio.create_task(projeto.gradle_clean())
            
            await status_processamento(contexto, processando_clean, 20) # pyright: ignore

            processo_clean = await processando_clean
            
        if processo_clean.returncode == 0: # pyright: ignore
            
            await contexto.send(f"Processo 'gradle clean' executado com êxito!\nIniciando empacotamento da aplicação...\n     └> Gerando build do projeto sig.") # pyright: ignore

            processando_war = asyncio.create_task(projeto.gradle_war())

            await status_processamento(contexto, processando_war, 180) # pyright: ignore
            
            resultado_gradle_war, processo_war = await processando_war # pyright: ignore

            formata_resultado_gradle_war = await regex.regex_saida_war(str(resultado_gradle_war)) # pyright: ignore

        if processo_war.returncode == 0: # pyright: ignore

            await status_bot("Build SIG Finalizado!")
            await contexto.send(f"Processo de build executado com êxito! \nSaida gradle war(Processo que gera o pacote .war): \n------------------------------------------------------------") # pyright: ignore
            await contexto.send(f"{formata_resultado_gradle_war}") # pyright: ignore
            await contexto.send(F"------------------------------------------------------------") # pyright: ignore
            await contexto.send(f"\nIniciando adionar properties. \n\n") # pyright: ignore

            caminho_war = arquivo_sig  + "/sig.war" # pyright: ignore

            processando_adionar_properties = asyncio.create_task(projeto.adicionar_properties(caminho_war, caminho_properties_sig, caminho_properties)) # pyright: ignore

            processo_properties = await processando_adionar_properties

        if processo_properties: # pyright: ignore

            await contexto.send(f"Processo que adiciona o arquivo .properties finalizado!") # pyright: ignore
            logger.info(f"Processo que adiciona o arquivo .properties foi realizado!")

            await contexto.send(f" \nProcesso de compactação Iniciado...") # pyright: ignore

            data_atual = datetime.now()
            data_formatada = data_atual.strftime("%d-%m-%Y")
            nome_sig = str(f"SIG-{versao[1]}-{data_formatada}") # pyright: ignore

            processando_compactar_versao = asyncio.create_task(projeto.compactar_arquivo(arquivo_sig, nome_sig)) # pyright: ignore

            await status_processamento(contexto, processando_compactar_versao, 60) # pyright: ignore

            processo_compactacao = await processando_compactar_versao # pyright: ignore

            if processo_compactacao:

                await contexto.send(f"Processo de compactação finalizado!") # pyright: ignore
                logger.info(f"Processo de compactação finalizado!")

                processando_upload_arquivo = asyncio.create_task(projeto.disponibilizar_arquivo(arquivo_sig, caminho_disponibilizar_versoes_padrao, "sig")) # pyright: ignore

                processo_upload = await processando_upload_arquivo

                if processo_upload:

                    await contexto.send(f"Processo de upload finalizado!") # pyright: ignore
                    await contexto.send(f"Arquivo:\n     └> [**{nome_sig}.rar**](http://localhost:8220/sig/)\n") # pyright: ignore
                    logger.info(f"Processo de upload foi realizado!")

                    await status_bot("Arquivo disponibilizado!", 'online')
                else:

                    await contexto.send(f"ERROR - upload não foi realizado!") # pyright: ignore
                    logger.info(f"Processo de upload não foi realizado!")

            else:

                await contexto.send(f"ERROR - adionar arquivo .properties não foi realizado!") # pyright: ignore
                logger.info(f"Processo adionar arquivo .properties não foi realizado!")
                
    except Exception as exception:
        
        logger.error(f'{funcao_atual} - {exception}') 

@bot.command(name='gerar-versao-funcoes')
async def gerar_versao_funcoes(contexto): # pyright: ignore

    await status_bot(status="Build Funções iniciada!", estado='do_not_disturb')
 
    funcao_atual = inspect.currentframe().f_code.co_name # pyright: ignore
    nome_usuario = contexto.author.name # pyright: ignore

    await contexto.send('Deseja alterar a versão do funções? \n     └> Por favor, digite "sim" para iniciar o processo.') # pyright: ignore

    def check(m): # pyright: ignore
        return m.channel == contexto.channel and m.author == contexto.author and m.content.lower() == 'sim' # pyright: ignore

    try:
       
        await bot.wait_for('message', check=check, timeout=60) # pyright: ignore

        await contexto.send('Iniciando o processo...') # pyright: ignore
        
        await contexto.send(f'**Iniciando processos para build...**') # pyright: ignore
        await contexto.send(f'Requerente: **{nome_usuario}**') # pyright: ignore

        ambiente = await projeto.configurar_ambiente(diretorio_projeto, diretorio_funcoes) # pyright: ignore
            
        if ambiente: 
           
            await contexto.send(f"Ambiente configurado!") # pyright: ignore

            versao_atual, data_atual = await projeto.versao_atual_funcoes() # pyright: ignore
            data_atualizada = await projeto.versionamento_funcoes()

            await contexto.send(f"Versão atual: {versao_atual}\n     └> Versão que sera gerada: {versao_atual}") # pyright: ignore

            await contexto.send(f"Data atual: {data_atual}\n     └> Data da versão que sera gerada: {data_atualizada}") # pyright: ignore

            await contexto.send(f"Iniciando Clean do repositorio...\n     └> Apagando as versões geradas anteriormente...") # pyright: ignore
            
            processando_clean = asyncio.create_task(projeto.gradle_clean())
            
            await status_processamento(contexto, processando_clean, 3) # pyright: ignore

            processo_clean = await processando_clean
            
        if processo_clean.returncode == 0: # pyright: ignore
            
            await contexto.send(f"Processo 'gradle clean' executado com êxito!\nIniciando empacotamento da aplicação...\n     └> Gerando build do funções.") # pyright: ignore

            processando_war = asyncio.create_task(projeto.gradle_war())

            await status_processamento(contexto, processando_war, 10) # pyright: ignore
            
            resultado_war, processo_war = await processando_war # pyright: ignore

        if processo_war.returncode == 0: # pyright: ignore

            await status_bot("Build FUNCOES Finalizado!")

            await contexto.send(f"Processo de build executado com êxito! \nSaida gradle war(Processo que gera o pacote .war):") # pyright: ignore
            await contexto.send(f"Adicionando arquivo .properties! \n\n") # pyright: ignore

            caminho_war = arquivo_funcoes  + "/sigpwebfuncoes.war" # pyright: ignore

            processando_adionar_properties = asyncio.create_task(projeto.adicionar_properties(caminho_war, caminho_properties_funcoes, caminho_properties)) # pyright: ignore

            processo_properties = await processando_adionar_properties

        if processo_properties: # pyright: ignore

            await contexto.send(f"Processo que adiciona o arquivo .properties finalizado!") # pyright: ignore
            logger.info(f"Processo que adiciona o arquivo .properties foi realizado!")

            await contexto.send(f" \nProcesso de compactação Iniciado...") # pyright: ignore

            nome_funcoes = f"Funcao-v.{versao_atual}-{data_atualizada}" # pyright: ignore
            nome_funcoes = str(nome_funcoes)

            processando_compactar_versao = asyncio.create_task(projeto.compactar_arquivo(arquivo_funcoes, nome_funcoes)) # pyright: ignore

            await status_processamento(contexto, processando_compactar_versao, 3) # pyright: ignore

            processo_compactacao = await processando_compactar_versao # pyright: ignore

            if processo_compactacao:
                
                await contexto.send(f"Processo de compactação finalizado!") # pyright: ignore

                await contexto.send(f"Iniciando upload. \n\n") # pyright: ignore

                processando_upload_arquivo = asyncio.create_task(projeto.disponibilizar_arquivo(arquivo_funcoes, caminho_disponibilizar_versoes_padrao,"sigpwebfuncoes")) # pyright: ignore

                processo_upload = await processando_upload_arquivo

                if processo_upload:

                    await contexto.send(f"Processo de upload finalizado!") # pyright: ignore
                    await contexto.send(f"Arquivo:\n     └> [**{nome_funcoes}.rar**](http://localhost:8220/sigpwebfuncoes/)\n") # pyright: ignore
                    logger.info(f"Processo de upload realizado!") 

                    await status_bot(status="Arquivo disponibilizado!", estado='online')

                else:

                    await contexto.send(f"ERROR - upload não foi realizado!") # pyright: ignore
                    logger.info(f"Processo de upload não foi realizado!")

            else:

                        await contexto.send(f"Processo de compactação não foi realizado!") # pyright: ignore

        else:

            await contexto.send(f"ERROR - adionar arquivo .properties não foi realizado!") # pyright: ignore
            logger.info(f"Processo adionar arquivo .properties não foi realizado!")

    except Exception as exception:
        
        logger.error(f'{funcao_atual} - {exception}') 

@bot.command(name='comandos')
async def comandos(contexto): # pyright: ignore
    texto = f"""Menu de comandos:           

 **!comandos**
     |                       
    └> **!status**
                └> Verifica status de processamento e memoria RAM usadas!
 
           **!sobre**
                └> Informações basicas sobre o bot!
        
           **!branch**
                └> Verifica branch atual!
        
           **!mudar-branch nome_da_branch**
                └> Muda para a branch selecionada! (Exemplo: !mudar-branch master)
        
           **!gerar-versao-sig**
                └>  Gera versão da aplicação sig!
        
           **!gerar-versao-funcoes**
                └> Gera versão da aplicação funções""" 

    await contexto.send(texto) # pyright: ignore

@bot.command(name='status')
async def status_task(contexto): # pyright: ignore

    funcao_atual = inspect.currentframe().f_code.co_name # pyright: ignore

    try:

        dados = await apm.monitorar_recursos() # pyright: ignore

        if dados is not None:

            uso_ram_mb = "{:.2f}".format(dados[-1].uso_ram_mb) # pyright: ignore
            
            await contexto.send(f"""\nStatus do bot e processamentos: \n    └> USO RAM: {uso_ram_mb} MB \n    └> USO CPU: {dados[-1].uso_cpu}% """) # pyright: ignore
    
    except Exception as exception:
        
        logger.error(f"{funcao_atual} - {exception}")

@bot.command(name='sobre')
async def sobre(contexto): # pyright: ignore
    await contexto.send('Bot feito com a intenção de automatizar o build da aplicação SIG,\nCriação: 02/06/2023, \nCriado e mantido por: Pablo Soares!') # pyright: ignore

@bot.command(name='mudar-branch')

@bot.event
async def on_message(message): # pyright: ignore
    
    funcao_atual = inspect.currentframe().f_code.co_name # pyright: ignore

    if message.author != bot.user: # pyright: ignore

        conteudo = message.content # pyright: ignore

        logger.info(f"Conteudo: {conteudo}")

        if conteudo.startswith(config["prefix"]): # pyright: ignore

            partes = conteudo.split(' ') # pyright: ignore
            comando = partes[0][len(config["prefix"]):] # pyright: ignore

            resposta = f"""
            Bot online... \n    └> Processando comando: {comando} \n------------------------------------------------------------
            """
            await message.channel.send(resposta) # pyright: ignore

            logger.info(f"Comando recebido: {comando}")
            
            try:
            
                if comando == 'mudar-branch':

                    branch = partes[1] # pyright: ignore
                    
                    await message.channel.send('\nCheckout iniciado...') # pyright: ignore 
                    await message.channel.send(f'Mudando para a branch:\n     └> {branch}') # pyright: ignore
                    
                    processo_checkout = await projeto.git_checkout(branch, diretorio_projeto) # pyright: ignore
                    
                    if processo_checkout.returncode == 0: # pyright: ignore

                        await message.channel.send(f"Branch Alterada:\n     └> **{branch}**\n\n") # pyright: ignore
                        await message.channel.send(f"Sucesso na alteração da branch!\n     └> **{processo_checkout.stdout}**") # pyright: ignore

                    elif processo_checkout.returncode == 1: # pyright: ignore
                    
                        logger.error(f"{processo_checkout.stderr}") # pyright: ignore
                        await message.channel.send(f"Falha ao alterar a branch - {processo_checkout.stderr}") # pyright: ignore

            except Exception as exception:

                logger.error(f"{funcao_atual} - {exception}")
        
    await bot.process_commands(message) # pyright: ignore

async def status_processamento(contexto, procesamento, tempo): # pyright: ignore
    
    while not procesamento.done(): # pyright: ignore
            logger.info("Processando...")
            await contexto.send("Executando o processo...") # pyright: ignore
            await asyncio.sleep(tempo) # pyright: ignore

async def status_bot(status=None, estado=None) -> None: # pyright: ignore

    funcao_atual = inspect.currentframe().f_code.co_name # pyright: ignore

    try:
        statuses = ["com outros bots.", "Paciência!", "com humanos!"]
        
        if status is None: 
            await bot.change_presence(activity=discord.Game(random.choice(statuses))) 
            logger.info(f"Status de presença do bot modificado aletoariamente.")
            return
        
        if status is not None: await bot.change_presence(activity=discord.Game(str(status))) # pyright: ignore
        if estado is not None: await bot.change_presence(status=estado) # pyright: ignore
    
    except Exception as exception:

        logger.error(f"{funcao_atual} - {exception}")
    
try:

    bot.run(config["token"]) # pyright: ignore

except GatewayNotFound as exeption:

    logger.warnning(f"{exeption}") # pyright: ignore
