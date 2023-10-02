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
import processamentos.deploy as deploy
import processamentos.projeto as projeto
import processamentos.conexao as conexao
import processamentos.container as container

from unidecode import unidecode
from datetime import datetime
from dotenv import load_dotenv
from discord.ext import commands 
from discord.ext.commands import Bot  
from discord.errors import GatewayNotFound
from config import config

# Setup loggers
logger = logger.setup_logger('prodatinha.bot')

# Setup bot
bot = Bot
config = config.config.load_config() 
bot.config = config  

# Load variaveis .env
load_dotenv()

intents = discord.Intents.all()

bot = Bot(
    command_prefix=commands.when_mentioned_or(config['prefix']), 
    intents=intents,
    help_command=None,
)

# Diretório do projeto Java
diretorio_projeto = os.getenv('DIRETORIO_PROJETO')
diretorio_sig = os.getenv('DIRETORIO_ROOT_SIG')
diretorio_root_funcoes = os.getenv('DIRETORIO_ROOT_FUNCOES')
diretorio_sig_war = os.getenv('DIRETORIO_SIG_WAR')
diretorio_funcoes_war = os.getenv('DIRETORIO_FUNCOES_WAR')
arquivo_sig_war = os.getenv('ARQUIVO_SIG_WAR')
arquivo_funcoes_war = os.getenv('ARQUIVO_FUNCOES_WAR')
caminho_properties_padrao = os.getenv('CAMINHO_PROPERTIES_TEMPLATE')
caminho_properties_gerado = os.getenv('CAMINHO_PROPERTIES_TEMPLATE_GERADA')
caminho_properties_sig = os.getenv('CAMINHO_PROPERTIES_SIG_WAR')
caminho_properties_funcoes = os.getenv('CAMINHO_PROPERTIES_FUNCOES_WAR')
caminho_criar_container_sig = os.getenv('CAMINHO_CRIAR_CONTAINER_SIG')
caminho_criar_container_funcoes = os.getenv('CAMINHO_CRIAR_CONTAINER_FUNCOES')
caminho_disponibilizar_versoes_padrao = os.getenv('CAMINHO_DISPONIBILIZAR_PADRAO_RAR')

@bot.event
async def on_ready():
   
    logger.info(f'Conectado com {bot.user.name}!') 
    logger.info(f'Versão API discord.py: {discord.__version__}')
    logger.info(f'Versão Python: {platform.python_version()}')
    logger.info(f'Rodando na plataforma: {platform.system()} {platform.release()} ({os.name})')
    logger.info('-------------------')

    if config['sync_commands_globally']: 
        logger.info('Sincronizado com comandos globais...')
        await bot.tree.sync()

    await status_bot()

@bot.event
async def on_disconnect():

    try:

        logger.info('Bot desconectado. Reconectando...')
        await bot.login(bot.token) 
        await bot.connect()

    except Exception as exception:

        logger.error(f'{exception}')

@bot.event
async def on_command_error(contexto, error): 
    
    processo_atual = inspect.currentframe().f_code.co_name 

    try:    
        if isinstance(error, commands.CommandNotFound): 

            comando = contexto.message.content

            if '!executar-setup' in comando:
                logger.info(f'Comando: {comando}');
                return
            
            elif '!mudar-branch' in comando:
                logger.info(f'Comando: {comando}')
                return
            else:

                logger.info(f'Comando não encontrado.') 

        else:
            raise error
    
    except Exception as exception:
        
          logger.error(f'{processo_atual} - {exception}')

@bot.command(name='branch')
async def branch(contexto): 

    processo_atual = inspect.currentframe().f_code.co_name 

    try:

        os.chdir(diretorio_projeto) 
        
        diretorio_atual = os.getcwd()
        arquivos = os.listdir(diretorio_projeto) 

        await contexto.send(f'Diretorio: {diretorio_atual}') 
    
        listabranch = (subprocess.run(['bash', '-c', 'git branch'], capture_output=True, text=True)).stdout.strip()
        
        await contexto.send(f'Branch atual:\n\n  {listabranch}\n------------------------------------------------------------') 
        
        logger.info(f'{processo_atual} - Branch atual: {listabranch.split()}')
    
    except Exception as exception:

        logger.error(f'{processo_atual} - {exception}')

@bot.command(name='gerar-versao-sig')
async def gerar_versao_sig(contexto): 

    await status_bot('Build SIG iniciado!','do_not_disturb')
 
    processo_atual = inspect.currentframe().f_code.co_name 
    nome_usuario = contexto.author.name 

    await contexto.send('Deseja gerar uma nova versão da aplicação SIG? \n     └> Por favor, digite "sim" para iniciar o processo.') 

    def check(m): 
        return m.channel == contexto.channel and m.author == contexto.author and m.content.lower() == 'sim' 
    
    try:

        processo_check = await bot.wait_for('message', check=check, timeout=60)
        resposta = processo_check.content.lower()

        if resposta != 'sim':
              await contexto.send(f'**Resposta inesperada...**') 
           
        
        await contexto.send(f'**Iniciando processos para build...**') 
        await contexto.send(f'Requerente: **{nome_usuario}**') 

        processo_config_ambiente = await projeto.configurar_ambiente(diretorio_projeto, diretorio_sig) 
            
        if processo_config_ambiente == True: 

            await contexto.send(f'Ambiente configurado!') 
            
            versao = await projeto.versionamento_sig()

            await contexto.send(f'Versão atual: {versao[0]}\n     └> Versão que sera gerada: {versao[1]}') 

            await contexto.send(f'Cache atual: {versao[2]}\n     └> Cache da versão que sera gerada: {versao[3]}') 
    
            await contexto.send(f'Iniciando Clean do repositorio...\n     └> Apagando as versões geradas anteriormente...') 
            
            processando_clean = asyncio.create_task(projeto.gradle_clean())
            
            await status_processamento(contexto, processo_atual, processando_clean, 20) 

            processo_clean = await processando_clean
            
        if processo_clean.returncode == 0: 
            
            await contexto.send(f'Processo "gradle clean" executado com êxito!\nIniciando empacotamento da aplicação...\n     └> Gerando build do projeto sig.') 

            processando_war = asyncio.create_task(projeto.gradle_war())

            await status_processamento(contexto, processo_atual, processando_war, 180) 
            
            resultado_gradle_war, processo_war = await processando_war 

            formata_resultado_gradle_war = await regex.regex_saida_war(str(resultado_gradle_war)) 

        if processo_war.returncode == 0: 

            await status_bot('Build SIG Finalizado!')
            await contexto.send(f'Processo de build executado com êxito! \nSaida gradle war(Processo que gera o pacote .war): \n------------------------------------------------------------') 
            await contexto.send(f'{formata_resultado_gradle_war}') 
            await contexto.send(F'------------------------------------------------------------') 
            await contexto.send(f'\nIniciando adionar properties. \n\n') 

            processando_adionar_properties = asyncio.create_task(projeto.adicionar_properties(arquivo_sig_war, caminho_properties_sig, caminho_properties_padrao)) 

            processo_properties = await processando_adionar_properties

        if processo_properties: 

            await contexto.send(f'Processo que adiciona o arquivo .properties finalizado!') 
            logger.info(f'Processo que adiciona o arquivo .properties foi realizado!')

            await contexto.send(f'Processo de compactação Iniciado...') 

            data_atual = datetime.now()
            data_formatada = data_atual.strftime('%d-%m-%Y')
            nome_sig = str(f'SIG-{versao[1]}-{data_formatada}') 

            processando_compactar_versao = asyncio.create_task(projeto.compactar_arquivo(diretorio_sig_war, nome_sig)) 

            await status_processamento(contexto, processo_atual, processando_compactar_versao, 60) 

            processo_compactacao = await processando_compactar_versao 

            if processo_compactacao:

                await contexto.send(f'Processo de compactação finalizado!') 
                logger.info(f'Processo de compactação finalizado!')

                processando_upload_arquivo = asyncio.create_task(projeto.disponibilizar_arquivo(diretorio_sig_war, caminho_disponibilizar_versoes_padrao, 'sig')) 

                processo_upload = await processando_upload_arquivo

                if processo_upload:

                    await contexto.send(f"Processo que disponibiliza arquivo finalizado!") 
                    await contexto.send(f'Arquivo:\n     └> [**{nome_sig}.rar**](http://localhost:8220/sig/)\n') 
                    logger.info(f'Processo de upload foi realizado!')

                    await status_bot('Arquivo disponibilizado!', 'online')
                else:

                    await contexto.send(f'ERROR - upload não foi realizado!') 
                    logger.info(f'Processo de upload não foi realizado!')

            else:

                await contexto.send(f'ERROR - adionar arquivo .properties não foi realizado!') 
                logger.info(f'Processo adionar arquivo .properties não foi realizado!')
    
    except asyncio.TimeoutError as exception:
        
        await contexto.send(f'Tempo esgotado.') 
        logger.info(f'Tempo esgotado.')
                
    except Exception as exception:
        
        logger.error(f'{processo_atual} - {exception}') 

@bot.command(name='gerar-versao-funcoes')
async def gerar_versao_funcoes(contexto): 

    await status_bot(status='Build Funções iniciada!', estado='do_not_disturb')
 
    processo_atual = inspect.currentframe().f_code.co_name 
    nome_usuario = contexto.author.name 

    await contexto.send('Deseja alterar a versão do funções? \n     └> Por favor, digite "sim" para iniciar o processo.') 

    def check(m): 
        return m.channel == contexto.channel and m.author == contexto.author and m.content.lower() == 'sim' 

    try:
       
        processo_check = await bot.wait_for('message', check=check, timeout=60) 
        resposta = processo_check.content.lower()

        if resposta != 'sim':
              await contexto.send(f'**Resposta inesperada...**') 

        await contexto.send('Iniciando o processo...') 
        
        await contexto.send(f'**Iniciando processos para build...**') 
        await contexto.send(f'Requerente: **{nome_usuario}**') 

        ambiente = await projeto.configurar_ambiente(diretorio_projeto, diretorio_root_funcoes) 
            
        if ambiente: 
        
            await contexto.send(f"Ambiente configurado!") 

            versao_atual, data_atual = await projeto.versao_atual_funcoes() 
            versao_atualizada, data_atualizada = await projeto.versionamento_funcoes()

            await contexto.send(f"Versão atual: {versao_atual}\n\t\t\t└>  Versão que sera gerada: {versao_atualizada}") 

            await contexto.send(f"Data atual: {data_atual}\n\t\t\t└>  Data da versão que sera gerada: {data_atualizada}") 

            await contexto.send(f"Iniciando Clean do repositorio...\n\t\t\t└>  Apagando as versões geradas anteriormente...") 
            
            processando_clean = asyncio.create_task(projeto.gradle_clean())
            
            await status_processamento(contexto, 'de limpeza no repositorío do funções', processando_clean, 3) 

            processo_clean = await processando_clean
            
        if processo_clean.returncode == 0: 
            
            await contexto.send(f"Processo 'gradle clean' executado com êxito!\nIniciando empacotamento da aplicação...\n\t\t\t└>  Gerando build do funções.") 

            processando_war = asyncio.create_task(projeto.gradle_war())

            await status_processamento(contexto, 'gerando war', processando_war, 10) 
            
            resultado_war, processo_war = await processando_war 

        if processo_war.returncode == 0: 

            await status_bot("Build FUNCOES Finalizado!")

            await contexto.send(f"Processo de build executado com êxito!") 
            await contexto.send(f"Adicionando arquivo .properties!") 

            processando_adionar_properties = asyncio.create_task(projeto.adicionar_properties(arquivo_funcoes_war, caminho_properties_funcoes, caminho_properties_padrao)) 

            processo_properties = await processando_adionar_properties

        if processo_properties: 

            await contexto.send(f"Processo que adiciona o arquivo .properties finalizado!") 
            logger.info(f"Processo que adiciona o arquivo .properties foi realizado!")

            await contexto.send("Processando arquivos para criar o container docker de teste do funções!") 

            processo_copiar_war = await projeto.copiar_war(diretorio_funcoes_war, caminho_criar_container_funcoes) 

            if processo_copiar_war:

                await contexto.send("Arquivo funções para criação do container copiado com êxito!") 

                processando_criar_container = asyncio.create_task(container.docker_criar_container(caminho_criar_container_funcoes, 'sigpwebfuncoes')) 
            
            else:

                await contexto.send("Arquivo funções para criação do container não foi copiado") 

            await contexto.send(f"Processo de compactação Iniciado...") 
            
            nova_data_nome = datetime.now().strftime("%d-%m-%Y")
            nome_funcoes = f'Funcao-v.{versao_atual}-{nova_data_nome}' 
            nome_funcoes = str(nome_funcoes)

            processando_compactar_versao = asyncio.create_task(projeto.compactar_arquivo(diretorio_funcoes_war, nome_funcoes)) 

            await status_processamento(contexto, 'compactando versão gerada', processando_compactar_versao, 3) 

            processo_compactacao = await processando_compactar_versao 

            if processo_compactacao:
                
                await contexto.send(f"Processo de compactação finalizado!") 

                await contexto.send(f"Disponibilizando arquivo...") 

                processando_upload_arquivo = asyncio.create_task(projeto.disponibilizar_arquivo(diretorio_funcoes_war, caminho_disponibilizar_versoes_padrao,"sigpwebfuncoes")) 

                processo_upload = await processando_upload_arquivo

                if processo_upload:

                    await contexto.send(f"Processo que disponibiliza arquivo finalizado!") 
                    await contexto.send(f"Arquivo:\n\t\t\t└> [**{nome_funcoes}.rar**](http://localhost:8220/sigpwebfuncoes/)\n") 
                    logger.info(f"Processo de upload realizado!") 

                    await status_bot(status="Arquivo disponibilizado!", estado='online')

                    processando_deploy_funcoes = asyncio.create_task(deploy.executar_curl('http://localhost:8080/sigpwebfuncoes/funcoes_setup.jsp')) 

                    await status_processamento(contexto, 'funções setup', processando_deploy_funcoes, 90) 

                    processo_deploy_funcoes = await processando_deploy_funcoes

                    if processo_deploy_funcoes:

                        await contexto.send(f'Execução  funções setup finalizado!')

                        for linha in processo_deploy_funcoes:

                            await contexto.send(f'{linha}')
                    
                    logger.info(f'Processo {processo_atual} foi concluido.')

                    return True

                else:

                    await contexto.send(f'ERROR - houve falha ao disponibilizar arquivo!') 
                    logger.info(f'falha no processo disponibilizar arquivo!')

                    return False

            else:

                await contexto.send(f'Processo de compactação não foi realizado!') 

                return False        

        else:

            await contexto.send(f'ERROR - adionar arquivo .properties não foi realizado!') 
            logger.info(f'Processo adionar arquivo .properties não foi realizado!')

    except asyncio.TimeoutError as exception:
        
        await contexto.send(f'Tempo esgotado.') 
        logger.info(f'Tempo esgotado.')

    except Exception as exception:
        
        logger.error(f'{processo_atual} - {exception}') 

@bot.command(name='comandos')
async def comandos(contexto): 
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
                └> Muda para a branch selecionada! (Exemplo: **!mudar-branch master**)
        
           **!gerar-versao-sig**
                └>  Gera versão da aplicação sig!
               
           **!gerar-versao-funcoes**
                └> Gera versão da aplicação funções
           
           **!executar-setup "nome_da_branch" "nome_do_servidor" "nome_da_base"**
                └>  Gera uma nova versão do funções a partir da branch indicada, 
                       Executa setup no servidor e base indicados!
                       (Exemplo: **!executar-setup master 28 sch_shelena)**
    """ 

    await contexto.send(texto) 

@bot.command(name='status')
async def status_task(contexto): 

    processo_atual = inspect.currentframe().f_code.co_name 

    try:

        dados = await apm.monitorar_recursos() 

        if dados is not None:

            uso_ram_mb = '{:.2f}'.format(dados[-1].uso_ram_mb) 
            
            await contexto.send(f"""\nStatus do bot e processamentos: \n    └> USO RAM: {uso_ram_mb} MB \n    └> USO CPU: {dados[-1].uso_cpu}% """) 
    
    except Exception as exception:
        
        logger.error(f"{processo_atual} - {exception}")

@bot.command(name='sobre')
async def sobre(contexto): 
    await contexto.send('Bot feito com a intenção de automatizar o build da aplicação SIG,\nCriação: 02/06/2023, \nCriado e mantido por: Pablo Soares!') 

@bot.event
async def on_message(message): 
    
    processo_atual = inspect.currentframe().f_code.co_name 

    if message.author != bot.user: 

        nome_usuario = message.author.name 
        conteudo = message.content 

        logger.info(f'Conteudo: {conteudo}')

        if conteudo.startswith(config['prefix']): 

            partes = conteudo.split(' ') 
            comando = partes[0][len(config['prefix']):] 

            resposta = f"""
            Bot online...\n\t└>  Processando comando: {comando}\n\t\t\tRequerente: **{nome_usuario}**\n------------------------------------------------------------
            """
            await message.channel.send(resposta) 

            logger.info(f'Comando recebido: {comando}')
            
            try:
            
                if comando == 'mudar-branch':

                    configuracoes = {
                        'branch' : partes[1],  
                    } 

                    branch = configuracoes['branch']
                    
                    await message.channel.send('\nCheckout iniciado...')  
                    await message.channel.send(f'Mudando para a branch:\n\t└> {branch}') 
                    
                    processando_checkout = asyncio.create_task(projeto.git_checkout(branch, diretorio_projeto))
                    processo_checkout = await processando_checkout
                    
                    if processo_checkout.returncode == 0:

                        await message.channel.send(f'Branch Alterada:\n\t└> **{branch}**\n\n') 
                        await message.channel.send(f'Sucesso na alteração da branch!\n\t└> **{processo_checkout.stdout}**') 

                    else: 
                    
                        logger.error(f'{processo_checkout.stderr}') 
                        await message.channel.send(f'Falha ao alterar a branch - {processo_checkout.stderr}') 
                
                elif comando == 'executar-setup':

                    configuracoes = {
                        'branch' : partes[1],
                        'servidor' :  partes[2],
                        'base' : partes[3]    
                    } 

                    branch = configuracoes['branch']
                    servidor = configuracoes['servidor']
                    base = configuracoes['base']

                    processo_checkout = await projeto.git_checkout(branch, diretorio_projeto)

                    if processo_checkout.returncode == 0: 

                            await message.channel.send(f'Branch Alterada:\n\t└> **{branch}**') 
                            await message.channel.send(f'Sucesso na alteração da branch!\n\t└> **{processo_checkout.stdout}**') 
                    
                    ambiente = await projeto.configurar_ambiente(diretorio_projeto, diretorio_root_funcoes) 

                    await message.channel.send(f'\nIniciando execução do setup na base indicada...\n\t└>  Branch: {branch}\n\t\t\tServidor: {servidor}\n\t\t\tBase: {base}')
            
                    if ambiente:

                        await message.channel.send(f"Ambiente configurado!") 

                        versao_atual, data_atual = await projeto.versao_atual_funcoes() 
                        versao_atualizada, data_atualizada = await projeto.versionamento_funcoes()

                        await message.channel.send(f"Versão atual: {versao_atual}\n\t\t\t└>  Versão que sera gerada: {versao_atualizada}") 
                        await message.channel.send(f"Data atual: {data_atual}\n\t\t\t└>  Data da versão que sera gerada: {data_atualizada}")  
                        await message.channel.send(f"Iniciando Clean do repositorio...\n\t└> Apagando as versões geradas anteriormente...") 
            
                        processando_clean = asyncio.create_task(projeto.gradle_clean())
                        
                        await status_processamento(contexto = None, processo_atual = 'de limpeza no repositorío do funções', procesamento = processando_clean, tempo = 3) 

                        processo_clean = await processando_clean
                        
                        if processo_clean.returncode == 0: 
                            
                            await message.channel.send(f"Processo 'gradle clean' executado com êxito!\nIniciando empacotamento da aplicação...\n     └> Gerando build do funções.") 

                            processando_war = asyncio.create_task(projeto.gradle_war())

                            await status_processamento(contexto = None, processo_atual = 'gerando war', procesamento = processando_clean, tempo = 10) 

                            resultado_war, processo_war = await processando_war 

                        if processo_war.returncode == 0: 

                            await conexao.definir_configuracoes_arquivo_properties(servidor, base)

                            await status_bot("Build FUNCOES Finalizado!")

                            await message.channel.send(f"Processo de build executado com êxito!") 
                            await message.channel.send(f"Adicionando arquivo .properties!") 

                            processando_adionar_properties = asyncio.create_task(projeto.adicionar_properties(arquivo_funcoes_war, caminho_properties_funcoes, caminho_properties_gerado)) 

                            processo_properties = await processando_adionar_properties

                        if processo_properties:

                            porta = 8081 
                            container_name = f'sigpwebfuncoes_{servidor}_{base}_{nome_usuario}'

                            await message.channel.send(f"Processo que adiciona o arquivo .properties finalizado!") 
                            logger.info(f"Processo que adiciona o arquivo .properties foi realizado!")

                            await message.channel.send("Processando arquivos para criar o container docker de teste do funções!") 

                            processo_copiar_war = await projeto.copiar_war(diretorio_funcoes_war, caminho_criar_container_funcoes) 

                            if processo_copiar_war:

                                await message.channel.send("Arquivo funções para criação do container copiado com êxito!") 

                                processando_criar_container = asyncio.create_task(container.docker_criar_container(caminho_criar_container_funcoes, container_name, porta))

                                await asyncio.sleep(60)

                            if processando_criar_container:

                                processando_deploy_funcoes = asyncio.create_task(deploy.executar_curl(f'http://localhost:{porta}/sigpwebfuncoes/funcoes_setup.jsp')) 

                                await status_processamento(message.channel, processo_atual = 'funções setup', procesamento = processando_clean, tempo = 30) 

                                processo_deploy_funcoes = await processando_deploy_funcoes

                                if processo_deploy_funcoes:

                                    await message.channel.send(f'Execução  funções setup finalizado!')

                                    for linha in processo_deploy_funcoes:

                                        await message.channel.send(f'{linha}')

                    elif processo_checkout.returncode == 1: 
                    
                        logger.error(f'{processo_checkout.stderr}') 
                        await message.channel.send(f'Falha ao alterar a branch - {processo_checkout.stderr}')

                    else:
                        
                        pass

            except Exception as exception:

                logger.error(f'{processo_atual} - {exception}') 
        
    await bot.process_commands(message) 

async def status_processamento(contexto=None, processo_atual=None, procesamento=None, tempo=None): 
    
    while not procesamento.done(): 
            processo_atual_sem_acentos = unidecode(processo_atual)
            logger.info(f'Executando o processo {processo_atual_sem_acentos}...') 
            
            if contexto is not None : await contexto.send(f'Executando o processo {processo_atual}...') 
            
            await asyncio.sleep(tempo) 

async def status_bot(status=None, estado=None) -> None: 

    processo_atual = inspect.currentframe().f_code.co_name 

    try:
        statuses = ['com outros bots.', 'Paciência!', 'com humanos!']
        
        if status is None: 
            await bot.change_presence(activity=discord.Game(random.choice(statuses))) 
            logger.info(f'Status de presença do bot modificado aletoariamente.')
            return
        
        if status is not None: await bot.change_presence(activity=discord.Game(str(status))) 
        if estado is not None: await bot.change_presence(status=estado) 
    
    except Exception as exception:

        logger.error(f'{processo_atual} - {exception}')
    
try:

    bot.run(config['token']) 

except GatewayNotFound as exeption:

    logger.warnning(f'{exeption}') 
