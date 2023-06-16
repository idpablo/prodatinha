#!/usr/bin/python

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

from util.logger import setup_logger
logger = setup_logger("upload.py", "discord.log")

async def upload_arquivo(nome_arquivo, caminho_arquvio):

    try:

        # Autenticação e autorização
        gauth = GoogleAuth()
        gauth.LocalWebserverAuth()
        drive = GoogleDrive(gauth)

        # Fazer upload do arquivo
        file_name = 'arquivo.txt'  # Nome do arquivo que será enviado
        file_path = 'caminho/do/arquivo/arquivo.txt'  # Caminho completo do arquivo

        gfile = drive.CreateFile({'title': file_name})
        gfile.SetContentFile(file_path)
        gfile.Upload()

        logger.info(f'Arquivo {file_name} enviado com sucesso!')
    
    except Exception as exception:
        logger.error(f"{exception}")