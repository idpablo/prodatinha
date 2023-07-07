#!/usr/bin/python3

import os
import json
import asyncio

from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaFileUpload

import util.logger as logger

logger = logger.setup_logger("upload.py", "discord.log")
diretorio_credenciais = 'C:/prodata/python/prodatinha/config/prodatinha-6da2bc4e0f96.json'

async def upload_arquivo(nome_arquivo, arquivo_sig):

    try:
        credenciais = service_account.Credentials.from_service_account_file(
            diretorio_credenciais,
            scopes=['https://www.googleapis.com/auth/drive']
        )

        servico_drive = build('drive', 'v3', credentials=credenciais)

        metadados_arquivo = {
            'name': nome_arquivo, 
        }
        
        media = MediaFileUpload(arquivo_sig, resumable=True)
        
        while True:
            
            processo_upload = asyncio.create_task(servico_drive.files().create(
                body=metadados_arquivo,
                media_body=media,
                fields='id', 
            ).execute())

            resultado_upload = await processo_upload.communicate()

            return resultado_upload
            
        # Obtendo o ID do arquivo enviado
        id_arquivo = resultado_upload['id']

        link_arquivo = servico_drive.files().get(fileId=id_arquivo, fields='webViewLink').execute()

        link_arquivo = link_arquivo['webViewLink']

        logger.info(f'Upload concluído. ID do arquivo: {link_arquivo}')

        return link_arquivo

    except Exception as exception:
        logger.error(f"{exception}")