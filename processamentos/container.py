import docker 
import inspect
import threading
import time 

import util.logger as logger
logger = logger.setup_logger('container.py')

container_semaforo = threading.Semaphore()

def docker_buscar_container(container_nome: str):
    
    funcao_atual = inspect.currentframe().f_code.co_name 

    try:

        client = docker.from_env() 
        container = client.containers.get(container_nome) 
        return True
    
    except docker.errors.NotFound as e: 

        logger.info(f"{funcao_atual} - O container '{container_nome}' não existe. - {e}")
    
        return False

def docker_parar_container(container_nome: str):

    funcao_atual = inspect.currentframe().f_code.co_name 

    try:
        client = docker.from_env() 
        container = client.containers.get(container_nome) 

        if container.status == "running": 
            
            logger.info(f"O container '{container_nome}' esta em excução.")
            logger.info(f"O container '{container_nome}' sera parado.") 
            container.stop() 
            
            while docker_buscar_container(container_nome):
                logger.info(f"Aguardando o container '{container_nome}' finalizar a execução...")
                time.sleep(1) 

        if docker_buscar_container(container_nome) is not True:
            
            logger.info(f"O container '{container_nome}' foi removido.") 
            
            return True
        
        return False

    except docker.errors as e: 
    
        logger.info(f"{funcao_atual} - O container '{container_nome}' não existe. - {e}")

        return False

async def docker_criar_container(dockerfile_dir: str, container_nome: str):

    funcao_atual = inspect.currentframe().f_code.co_name 

    try:

        resultado_buscar_contairner = docker_buscar_container(container_nome)

        if resultado_buscar_contairner:
        
            logger.info(f"O container '{container_nome}' já existe.")
            resultado_parar_container = docker_parar_container(container_nome) 
            
        client = docker.from_env() 

        # Construa a imagem a partir do Dockerfile
        image, build_logs = client.images.build(path=dockerfile_dir, tag=container_nome) 

        # Exiba os logs de construção
        for log_line in build_logs: 
            logger.info(log_line) 
        
        # Configurações do contêiner
        container_config = {
            'image': container_nome,
            'ports': {8080:8080},
            'name': 'sigpwebfuncoes',
            'remove': True,
            'tty': True,
            'detach': True,
            'network_mode': 'bridge'
        }

        container = client.containers.run(**container_config) 

        logger.info(f"ID do contêiner criado: {container.id}") 

        return True

    except Exception as exception:
    
        logger.error(f"{funcao_atual} - {exception}")

        return False

def capturar_logs_com_erro_pelo_nome(container_name: str):
    try:
        client = docker.from_env() 
        container = client.containers.get(container_name)  
        logs = container.logs(stream=True, follow=True) 
        linhas_de_erro = []

        for linha in logs.split('\n'): 
            if 'erro' in linha.lower() or 'exception' in linha.lower(): 
                linhas_de_erro.append(linha) 

        for linha in linhas_de_erro: 
            logger.info(f"LOG FUNCOES - {linha}")
        
        return True
    
    except docker.errors.NotFound as e: 

        logger.error(f"Container não encontrado: {str(e)}") 
        return False
    
    except Exception as e:
    
        logger.error(f"Erro ao monitorar logs: {str(e)}")
        return False

def monitorar_logs_em_tempo_real(container_name: str):
    try:
        client = docker.from_env()  
        container = client.containers.get(container_name)  

        for log in container.logs(stream=True, follow=True): 
            log = log.decode('utf-8')  
            logger.info(log, end='') 

        return True

    except docker.errors.NotFound as e: 
    
        logger.error(f"Container não encontrado: {e}") 
        return False
    
    except Exception as e:
    
        logger.error(f"Erro ao monitorar logs: {str(e)}")
        return False


