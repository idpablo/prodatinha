import inspect
import json
import sys
import os

def load_config(bot):

    funcao_atual = inspect.currentframe().f_code.co_name

    try:

        if not os.path.isfile(f"{os.path.realpath(os.path.dirname(__file__))}/config.json"):
            sys.exit("'config.json' not found! Please add it and try again.")
        else:
            with open(f"{os.path.realpath(os.path.dirname(__file__))}/config.json") as file:
                config = json.load(file)

                return config
    
    except Exception as exception:

        bot.logerror.error(f"{funcao_atual} - {exception}")
