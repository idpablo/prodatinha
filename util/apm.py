import psutil

from util import logger

logger = logger.setup_logger("apm.py")

class monitor_recursos:
    def __init__(self, uso_ram_mb: str, uso_cpu: str, processos: str) -> None: # pyright: ignore
        self.uso_ram_mb = uso_ram_mb
        self.uso_cpu = uso_cpu
        self.processos = processos

async def monitorar_recursos() -> None:
    try:
        processo = psutil.Process()
        informacoes = []

        uso_ram = processo.memory_info().rss
        uso_ram_mb = uso_ram / (1024 * 1024)

        uso_cpu = psutil.cpu_percent()

        processos = []
        for proc in psutil.process_iter(["pid", "name", "cpu_percent"]):
            if proc.info["name"].lower().find("python") != -1: # pyright: ignore
                processos.append({ # pyright: ignore
                    "pid": proc.info["pid"], # pyright: ignore
                    "nome": proc.info["name"], # pyright: ignore
                    "uso_cpu": proc.info["cpu_percent"] # pyright: ignore
                })

        informacoes.append(monitor_recursos(uso_ram_mb, uso_cpu, processos)) # pyright: ignore

        return informacoes # pyright: ignore
    
    except Exception as exception:
        logger.error(f"{exception}")
        return None
