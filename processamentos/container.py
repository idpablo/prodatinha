import docker # pyright: ignore
import inspect
import threading
import time 

import util.logger as logger
logger = logger.setup_logger('container.py')

container_semaforo = threading.Semaphore()

def docker_buscar_container(container_nome: str):
    
    funcao_atual = inspect.currentframe().f_code.co_name # pyright: ignore

    try:

        client = docker.from_env() # pyright: ignore
        container = client.containers.get(container_nome) # pyright: ignore
        return True
    
    except docker.errors.NotFound as e: # pyright: ignore

        logger.info(f"{funcao_atual} - O container '{container_nome}' não existe. - {e}")
    
        return False

def docker_parar_container(container_nome: str):

    funcao_atual = inspect.currentframe().f_code.co_name # pyright: ignore

    try:
        client = docker.from_env() # pyright: ignore
        container = client.containers.get(container_nome) # pyright: ignore

        if container.status == "running": # pyright: ignore
            
            logger.info(f"O container '{container_nome}' esta em excução.")
            logger.info(f"O container '{container_nome}' sera parado.") 
            container.stop() # pyright: ignore
            
            while docker_buscar_container(container_nome):
                logger.info(f"Aguardando o container '{container_nome}' finalizar a execução...")
                time.sleep(1) 

        if docker_buscar_container(container_nome) is not True:
            
            logger.info(f"O container '{container_nome}' foi removido.") 
            
            return True
        
        return False

    except docker.errors as e: # pyright: ignore
    
        logger.info(f"{funcao_atual} - O container '{container_nome}' não existe. - {e}")

        return False

async def docker_criar_container(dockerfile_dir: str, container_nome: str):

    funcao_atual = inspect.currentframe().f_code.co_name # pyright: ignore

    try:

        resultado_buscar_contairner = docker_buscar_container(container_nome)

        if resultado_buscar_contairner:
        
            logger.info(f"O container '{container_nome}' já existe.")
            resultado_parar_container = docker_parar_container(container_nome) # pyright: ignore
            
        client = docker.from_env() # pyright: ignore

        # Construa a imagem a partir do Dockerfile
        image, build_logs = client.images.build(path=dockerfile_dir, tag=container_nome) # pyright: ignore

        # Exiba os logs de construção
        for log_line in build_logs: # pyright: ignore
            logger.info(log_line) # pyright: ignore
        
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

        # Crie um contêiner usando a imagem criada
        container = client.containers.run(**container_config) # pyright: ignore

        # Exiba o ID do contêiner criado
        logger.info(f"ID do contêiner criado: {container.id}") # pyright: ignore

        return True

    except Exception as exception:
    
        logger.error(f"{funcao_atual} - {exception}")

        return False

def capturar_logs_com_erro_pelo_nome(container_name: str):
    try:
        client = docker.from_env()  # Crie um cliente Docker # pyright: ignore
        container = client.containers.get(container_name)  # Obtenha o objeto do container pelo nome # pyright: ignore
        logs = container.logs(stream=True, follow=True)  # Capture os logs e decode para texto # pyright: ignore
        linhas_de_erro = []

        # Analise as linhas dos logs
        for linha in logs.split('\n'): # pyright: ignore
            if 'erro' in linha.lower() or 'exception' in linha.lower(): # pyright: ignore
                linhas_de_erro.append(linha) # pyright: ignore

        for linha in linhas_de_erro: # pyright: ignore
            logger.info(f"LOG FUNCOES - {linha}")
        
        return True
    
    except docker.errors.NotFound as e: # pyright: ignore

        logger.error(f"Container não encontrado: {str(e)}") # pyright: ignore
        return False
    
    except Exception as e:
    
        logger.error(f"Erro ao monitorar logs: {str(e)}")
        return False

def monitorar_logs_em_tempo_real(container_name: str):
    try:
        client = docker.from_env()  # Crie um cliente Docker # pyright: ignore
        container = client.containers.get(container_name)  # Obtenha o objeto do container pelo nome # pyright: ignore

        # Inicie a captura de logs em tempo real
        for log in container.logs(stream=True, follow=True): # pyright: ignore
            log = log.decode('utf-8')  # Decodifique o log para texto # pyright: ignore
            # Faça o que desejar com o log (por exemplo, imprima na tela) 
            logger.info(log, end='') # pyright: ignore

        return True

    except docker.errors.NotFound as e: # pyright: ignore
    
        logger.error(f"Container não encontrado: {e}") 
        return False
    
    except Exception as e:
    
        logger.error(f"Erro ao monitorar logs: {str(e)}")
        return False


