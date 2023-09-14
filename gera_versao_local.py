import os 
import inspect
import asyncio
import datetime
import util.regex as regex

from util.logger import *
from dotenv import load_dotenv
from processamentos.projeto import *

load_dotenv()

diretorio_projeto = os.getenv("DIRETORIO_PROJETO")
diretorio_sig = os.getenv("DIRETORIO_ROOT_SIG")
diretorio_funcoes = os.getenv("DIRETORIO_ROOT_FUNCOES")
arquivo_sig = os.getenv("ARQUIVO_SIG_WAR")
arquivo_funcoes = os.getenv("ARQUIVO_FUNCOES_WAR")
caminho_properties = os.getenv("CAMINHO_PROPERTIES_TEMPLATE")
caminho_properties_sig = os.getenv("CAMINHO_PROPERTIES_SIG_WAR")
caminho_properties_funcoes = os.getenv("CAMINHO_PROPERTIES_FUNCOES_WAR")
caminho_disponibilizar_versoes_auto = os.getenv("CAMINHO_DISPONIBILIZAR_VERSOES_AUTO_RAR")

async def gerar_versao_sig_local():
    
    try:
        
        logger.info(f'**Iniciando processos para build...**')

        processo_config_ambiente = await projeto.configurar_ambiente(diretorio_projeto, diretorio_sig) # pyright: ignore
            
        if processo_config_ambiente == True: 

            logger.info(f"Ambiente configurado!")

            versao = []
            versao = await versionamento_sig()

            logger.info(f"Versão atual: {versao[0]}") # pyright: ignore
            logger.info(f"Versão que sera gerada: {versao[1]}") # pyright: ignore
            logger.info(f"Cache atual: {versao[2]}") # pyright: ignore
            logger.info(f"Cache da versão que sera gerada: {versao[3]}") # pyright: ignore     
            logger.info(f"Iniciando Clean do repositorio...")
            logger.info(f"Apagando as versões geradas anteriormente...")
            
            processando_clean = asyncio.create_task(gradle_clean())
            
            await status_processamento_local(processando_clean, 20)

            processo_clean = await processando_clean
            
        if processo_clean.returncode == 0: # pyright: ignore
            
            logger.info(f"Processo 'gradle clean' executado com êxito!")
            logger.info(f"Iniciando empacotamento da aplicação...")
            logger.info(f"Gerando build do projeto sig.")

            processando_war = asyncio.create_task(gradle_war())

            await status_processamento_local(processando_war, 180)
            
            resultado_gradle_war, processo_war = await processando_war # pyright: ignore

            formata_resultado_gradle_war = await regex.regex_saida_war(str(resultado_gradle_war)) # pyright: ignore

        if processo_war.returncode == 0: # pyright: ignore

            logger.info(f"Processo de build executado com êxito!")
            logger.info(f"Saida gradle war(Processo que gera o pacote .war")
            print({formata_resultado_gradle_war}) # pyright: ignore
            logger.info(F"------------------------------------------------------------")
            logger.info(f"Iniciando adionar properties.")

            caminho_war = arquivo_sig  + "/sig.war" # pyright: ignore

            processando_adionar_properties = asyncio.create_task(adicionar_properties(caminho_war, caminho_properties_sig, caminho_properties)) # pyright: ignore

            processo_properties = await processando_adionar_properties

        if processo_properties: # pyright: ignore

            logger.info(f"Processo que adiciona o arquivo .properties finalizado!")
            logger.info(f"Processo que adiciona o arquivo .properties foi realizado!")

            logger.info(f"Processo de compactação Iniciado...")

            data_atual = datetime.now()  # pyright: ignore
            data_formatada = data_atual.strftime("%d-%m-%Y") # pyright: ignore
            nome_sig = str(f"SIG-{versao[1]}-{data_formatada}") # pyright: ignore

            processando_compactar_versao = asyncio.create_task(projeto.compactar_arquivo(arquivo_sig, nome_sig)) # pyright: ignore

            await status_processamento_local(processando_compactar_versao, 60)

            processo_compactacao = await processando_compactar_versao

            if processo_compactacao:

                logger.info(f"Processo de compactação finalizado!")
                logger.info(f"Processo de compactação finalizado!")

                processando_upload_arquivo = asyncio.create_task(projeto.disponibilizar_arquivo(arquivo_sig, caminho_disponibilizar_versoes_auto, "sig")) # pyright: ignore

                processo_upload = await processando_upload_arquivo # pyright: ignore

                if processo_upload:

                    logger.info(f"Processo de upload finalizado!")
                    logger.info(f"Arquivo: [**{nome_sig}.rar**](http://localhost:8220/sig/)")
                    logger.info(f"Processo de upload foi realizado!")
                    
                    return True

                else:

                    logger.info(f"ERROR - upload não foi realizado!")
                    logger.info(f"Processo de upload não foi realizado!")

                    return False

            else:

                logger.info(f"ERROR - adicionar arquivo .properties não foi realizado!")
                logger.info(f"Processo adicionar arquivo .properties não foi realizado!")

                return False
                
    except Exception as exception:
        
        logger.error(f'{exception}') 