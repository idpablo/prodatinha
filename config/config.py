#!/usr/bin/python3

import inspect
import json
import sys
import os

import util.logger as logger

logger = logger.setup_logger("config.py")

class config():

    def load_config():  # pyright: ignore

        funcao_atual = inspect.currentframe().f_code.co_name  # pyright: ignore

        try:

            if not os.path.isfile(f"{os.path.realpath(os.path.dirname(__file__))}/config.json"):
                sys.exit("'config.json' não encontrado, adicione e tente novamente.")
            else:
                with open(f"{os.path.realpath(os.path.dirname(__file__))}/config.json") as file:
                    
                    logger.info(f"{funcao_atual} - Leitura do arquivo config.json realidaza!")   # pyright: ignore

                    config = json.load(file)

                    return config
        
        except Exception as exception:

            logger.error(f"{funcao_atual} - {exception}")  # pyright: ignore

    def load_config_gpt():  # pyright: ignore

        try:

            if not os.path.isfile(f"{os.path.realpath(os.path.dirname(__file__))}/chatgpt.json"):
                sys.exit("'chatgpt.json' não encontrado, adicione e tente novamente.")
            else:
                with open(f"{os.path.realpath(os.path.dirname(__file__))}/chatgpt.json") as file:
                    config_gpt = json.load(file)

                    return config_gpt
        
        except Exception as exception:
            
            logger.error(f"{exception}")  # pyright: ignore