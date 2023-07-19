FROM ubuntu:latest

WORKDIR /app

COPY dependencias.txt .

RUN apt-get update && apt-get install -y tzdata && apt-get install -y python3 \
    && apt-get install -y python3-pip && apt-get install -y git \
    && apt-get install -y nodejs && apt-get install -y npm \
    && apt-get install -y gradle

RUN pip install -r dependencias.txt
RUN npm install -g grunt-cli -opcoes -C /repo/sig/sig/WebContent 

RUN  git config --global --add safe.directory /repo/sig

ENV TZ=America/Sao_Paulo
ENV LANG pt_BR.utf8

COPY . .

CMD [ "python3", "prodatinha.py" ]
