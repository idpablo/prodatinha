import re
import asyncio
import subprocess

from bs4 import BeautifulSoup

import util.logger as logger
logger = logger.setup_logger('deploy.py')

async def executar_curl(contexto, url):  
   
    try:

        linha_log_body_funcoes = []
        linha_log_erros_funcoes = []

        logger.info(f'Chamando url pelo curl -> {url}')

        while True:
            
            processo = await asyncio.create_subprocess_shell(f'curl {url}', stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, )

            stdout, stderr = await processo.communicate()

            saida = stdout.decode('iso-8859-1')

            if processo.returncode == 0:

                resultado_curl = saida.splitlines()

                idx = 0
                linha_log_info_encontrada = False 
                linha_log_erros_encontrada = False 
                dentro_do_body = False
               
                for linha in resultado_curl:

                    linha_sem_tag_html = re.sub(r'<[^>]*>', '', linha)

                    if linha_sem_tag_html != '':

                        if '<body>' in linha:
                            dentro_do_body = True
                            continue
                        elif '</body>' in linha:
                            dentro_do_body = False

                        if 'INFO' or '******' in linha:
                            linha_log_info_encontrada = True 

                        if 'LOG ERROS' in linha:
                            linha_log_erros_encontrada = True 

                        if dentro_do_body:
    
                            linha_log_body_funcoes.append(linha_sem_tag_html)
                            logger.info(f'{idx}: {linha_sem_tag_html}')
                            await contexto.send(f'Informações sobre a base onde o funções está sendo executado:\n     └>{linha_sem_tag_html}')
                        
                        # if linha_log_info_encontrada:
                            
                        #     logger.info(f'{idx}: {linha_sem_tag_html}')

                        if linha_log_erros_encontrada:
                                    
                            linha_log_erros_funcoes.append(linha_sem_tag_html)
                            logger.info(f'Linha com erro funcoes - {idx}: {linha_sem_tag_html}')

                    idx += 1

            logger.info(f'Execução SigFunções finalizado!')
            return linha_log_erros_funcoes
            
    except subprocess.CalledProcessError as e:
        
        logger.info(f'Erro ao executar o comando curl: {e}')
        return False
    
    except Exception as e:
        
        logger.error(f'Erro inesperado: {e}')
        return False 


