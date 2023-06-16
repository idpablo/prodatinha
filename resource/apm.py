#!/usr/bin/python

import psutil

class monitor_recursos:
    def __init__(self, uso_ram_mb, uso_cpu=None, processos=None):
        self.uso_ram_mb = uso_ram_mb
        self.uso_cpu = uso_cpu
        self.processos = processos

def monitorar_recursos(bot):
    try:
        processo = psutil.Process()
        informacoes = []

        uso_ram = processo.memory_info().rss
        uso_ram_mb = uso_ram / (1024 * 1024)

        uso_cpu = psutil.cpu_percent()

        processos = []
        for proc in psutil.process_iter(["pid", "name", "cpu_percent"]):
            if proc.info["name"].lower().find("python") != -1:
                processos.append({
                    "pid": proc.info["pid"],
                    "nome": proc.info["name"],
                    "uso_cpu": proc.info["cpu_percent"]
                })

        informacoes.append(monitor_recursos(uso_ram_mb, uso_cpu, processos))

        return informacoes
    
    except Exception as exception:
        bot.logerror.error(f"{exception}")
        return None
