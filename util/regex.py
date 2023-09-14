import inspect
import re

import util.logger as logger

logger = logger.setup_logger("regex.py", 'log/discord.log')

arquivo_atual = inspect.currentframe().f_code.co_filename # pyright: ignore


class ResultadoRegex:
    def __init__(self, args: str, returncode: int, stdout: str, stderr: str, task: None = None): 
        self.args = args
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
        if task is not None:
            task = task.replace('\\n', ' ')
            self.task = re.sub(r'\bUP-TO-DATE\b', '', task)
        else:
            self.task = None

async def regex_git_checkout(texto: str):
    try:
        logger.info(f"Regex iniciado")
        logger.info(f"{arquivo_atual} - Texto: {texto}")

        args_match = re.search(r"args='(.*?)'", texto)
        args = args_match.group(1) if args_match else ""

        returncode_match = re.search(r"returncode=(\d+)", texto)
        returncode = int(returncode_match.group(1)) if returncode_match else 0

        stdout_match = re.search(r"stdout=b\"(.*?)\"", texto)
        stdout = stdout_match.group(1) if stdout_match else ""

        stderr_match = re.search(r"stderr=b\"(.*?)\"", texto)
        stderr = stderr_match.group(1).replace("\\n", "") if stderr_match else ""

        return ResultadoRegex(args, returncode, stdout, stderr)

    except Exception as exception:

        logger.error(f'{arquivo_atual} - {exception}')
        return None

async def regex_saida_war(array: str):
    try:

        padrao = r"(Execution Time.*[\s\S]*?up-to-date)"  
        resultado = re.findall(padrao, array, re.DOTALL)
        resultado = '\n'.join(resultado)
        return resultado

    except Exception as exception:
        logger.error(f'{arquivo_atual} - {exception}')
        return None