import re

class ResultadoRegex:
    def __init__(self, args, returncode, stdout, stderr):
        self.args = args
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr

async def regex(bot, texto):

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
        
        bot.logerror.error(f'ERROR - {exception}')
        return None