import docker
import inspect

import util.logger as logger
logger = logger.setup_logger('container.py')


async def criar_container(dockerfile_dir, tipo):

    funcao_atual = inspect.currentframe().f_code.co_name

    try:

        # Crie um cliente Docker
        client = docker.from_env()

        # Construa a imagem a partir do Dockerfile
        image, build_logs = client.images.build(path=dockerfile_dir, tag=tipo)

        # Exiba os logs de construção
        for log_line in build_logs:
            logger.info(log_line)
        
        # Configurações do contêiner
        container_config = {
            'image': tipo,
            'ports': {5601:8080},
            'name': 'sigpwebfuncoes',
            'remove': True,
            'tty': True,
            'detach': True,
            'network_mode': 'bridge'
        }

        # Crie um contêiner usando a imagem criada
        container = client.containers.run(**container_config)

        # Exiba o ID do contêiner criado
        logger.info("ID do contêiner criado:", container.id)

        return True
    
    except Exception as exception:
    
        logger.error(f"{funcao_atual} - {exception}")

        return False



