# prodatinha
 Bot criado para automatizar o build da aplicação SIG - Prodata, e mais...
 
## Sobre

 Bot desenvolvido a partir da api disponibilizada pelo discord:
 [Dashboard API](https://discord.com/developers/applications) / [Documentação API](https://discord.com/developers/docs/intro)
 
## Tecnologias usadas

<div style="display: inline_block"><br>
  <img align="center" alt="Prodatinha-Python" height="30" width="40" src="https://raw.githubusercontent.com/devicons/devicon/master/icons/python/python-original.svg">
</div>

### Dependências globais

Python3 / pm2

### Dependências locais

```bash
pip install -r dependecias.txt
```

### Execução

```bash
pm2 start ecosystem.config.js
```

### Monitorar

```bash
pm2 monit
```

### logs

```bash
pm2 logs prodatinha
```
