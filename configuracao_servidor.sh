#!/bin/bash

echo "Configurando ambiente para execução do bot..."

npm install -g pm2
npm install -g grunt-cli 

cd /repo/sig

if [ "$PWD" == "/repo/sig" ]; then
    git config --global --add safe.directory /repo/sig
else
    echo "O script não está na pasta correta para execução."
fi

cd /repo/prodatinha

if [ -e dependencias.txt ]; then
  pip install -r dependencias.txt
else
  echo "O arquivo dependencias.txt não existe."
fi








