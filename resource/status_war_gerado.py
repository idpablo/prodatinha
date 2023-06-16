#!/usr/bin/pythons

import docker

async def montar_container():
    try:
    
        # Conectando ao daemon do Docker
        client = docker.from_env()

        # Criando um novo contêiner
        container = client.containers.create('ubuntu:latest', command='echo Hello, Docker!')

        # Iniciando o contêiner
        container.start()

        # Aguardando a execução do contêiner
        container.wait()

        # Obtendo o log de saída do contêiner
        logs = container.logs().decode('utf-8')
        print(logs)

        # Removendo o contêiner
        container.remove()

    except Exception as exception:
        print(exception)
