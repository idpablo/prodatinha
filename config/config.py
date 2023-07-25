#!/usr/bin/python3

import inspect
import json
import sys
import os

import util.logger as logger

logger = logger.setup_logger("config.py", "discord.log")

def load_config():

    funcao_atual = inspect.currentframe().f_code.co_name

    try:

        if not os.path.isfile(f"{os.path.realpath(os.path.dirname(__file__))}/config.json"):
            sys.exit("'config.json' não encontrado, adicione e tente novamente.")
        else:
            with open(f"{os.path.realpath(os.path.dirname(__file__))}/config.json") as file:
                
                logger.error(f"{funcao_atual} - Leitura do arquivo config.json realidaza!")

                config = json.load(file)

                return config
    
    except Exception as exception:

        logger.error(f"{funcao_atual} - {exception}")

def load_config_gpt():

    try:

        if not os.path.isfile(f"{os.path.realpath(os.path.dirname(__file__))}/chatgpt.json"):
            sys.exit("'chatgpt.json' não encontrado, adicione e tente novamente.")
        else:
            with open(f"{os.path.realpath(os.path.dirname(__file__))}/chatgpt.json") as file:
                config_gpt = json.load(file)

                return config_gpt
    
    except Exception as exception:
        
        bot.logger.error(f"{exception}")