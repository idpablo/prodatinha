#!/usr/bin/python

import inspect
import json
import sys
import os

def load_config(bot):

    funcao_atual = inspect.currentframe().f_code.co_name

    try:

        if not os.path.isfile(f"{os.path.realpath(os.path.dirname(__file__))}/config.json"):
            sys.exit("'config.json' não encontrado, adicione e tente novamente.")
        else:
            with open(f"{os.path.realpath(os.path.dirname(__file__))}/config.json") as file:
                config = json.load(file)

                return config
    
    except Exception as exception:

        bot.logger.error(f"{funcao_atual} - {exception}")
