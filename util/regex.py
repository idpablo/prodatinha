#!/usr/bin/python3

import inspect
import re

arquivo_atual = inspect.currentframe().f_code.co_filename

class ResultadoRegex:
    def __init__(self, args, returncode, stdout, stderr, task=None):
        self.args = args
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
        if task is not None:
            task = task.replace('\\n', ' ')
            self.task = re.sub(r'\bUP-TO-DATE\b', '', task)
        else:
            self.task = None

#funcao regex_build analisa e capitura a saida do comando gradle clean, não a uso efetivo atualmente
async def regex_build(bot, texto):
    try:
        bot.logger.info(f"Regex iniciado")
        bot.logger.info(f"{arquivo_atual} - Texto: {texto}")
        
        args_match = re.search(r"args=(\[.*?\])", texto)
        args = eval(args_match.group(1)) if args_match else []

        returncode_match = re.search(r"returncode=(\d+)", texto)
        returncode = int(returncode_match.group(1)) if returncode_match else 0

        stdout_match = re.search(r"stdout='(.*?)'", texto)
        stdout = stdout_match.group(1) if stdout_match else ""

        stderr_match = re.search(r"stderr='(.*?)'", texto)
        stderr = stderr_match.group(1) if stderr_match else ""

        task_match = re.search(r"Task :.*?BUILD SUCCESSFUL", texto)
        task = task_match.group(0).strip() if task_match else None

        return ResultadoRegex(args, returncode, stdout, stderr, task)

    except Exception as exception:
        
        bot.logger.error(f'{arquivo_atual} - {exception}')
        return None

async def regex_git_checkout(bot, texto):
    try:
        args_match = re.search(r"args='(.*?)'", texto)
        args = args_match.group(1) if args_match else ""

        returncode_match = re.search(r"returncode=(\d+)", texto)
        returncode = int(returncode_match.group(1)) if returncode_match else 0

        stdout_match = re.search(r"stdout=b\"(.*?)\"", texto)
        stdout = stdout_match.group(1) if stdout_match else ""

        stderr_match = re.search(r"stderr=b\"(.*?)\"", texto)
        stderr = stderr_match.group(1) if stderr_match else ""

        return ResultadoRegex(args, returncode, stdout, stderr)

    except Exception as exception:

        bot.logger.error(f'{arquivo_atual} - {exception}')
        return None

async def regex_saida_war(bot, array):
    try:

        padrao = r"(Execution Time.*[\s\S]*?up-to-date)"  
        resultado = re.findall(padrao, array, re.DOTALL)
        resultado = '\n'.join(resultado)
        return resultado

    except Exception as exception:
        bot.logger.error(f'{arquivo_atual} - {exception}')
        return None