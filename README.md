# prodatinha
    Bot criado para automatizar o build da aplicação SIG - Prodata, e mais...
    Todas as instruções para a manutenção e 

# Dependencias
**DENTRO DO DIRETORIO DO BOT** 
    Python3
    NodeJS 
    Execute: 'pip install -r dependencias.txt' <- Instala todas as dependencias necessarias.
    Execute: 'npm install pm2' <- Adiciona o gerenciador de processos avançado.

# Execução
    Execute: 'pm2 start ecosystem.config.js' <- adiona e inicia o processo do bot ao gerenciador.
    Execute: 'pm2 reload prodatinha' <- recarrega o script.
    Execute: 'pm2 stop prodatinha' <- para o processo.
    Execute: 'pm2 log prodatinha' <- observa os logs gerados pelo processo.


