FROM ubuntu:latest

WORKDIR /app

COPY dependencias.txt .

RUN apt-get update && apt-get install -y tzdata && apt-get install -y python3 \
    && apt-get install -y python3-pip && apt-get install -y git \
    && apt-get install -y nodejs && apt-get install -y npm \
    && apt-get install -y gradle

RUN  wget -O- https://apt.corretto.aws/corretto.key | sudo apt-key add - 
RUN sudo add-apt-repository 'deb https://apt.corretto.aws stable main'

RUN apt-get install -y java-1.8.0-amazon-corretto-jdk

RUN pip install -r dependencias.txt
RUN npm install -g grunt-cli 
RUN npm install -g pm2

RUN  git config --global --add safe.directory /repo/sig

ENV TZ=America/Sao_Paulo
ENV LANG pt_BR.utf8

COPY . .

CMD [ "pm2 start", "ecosystem.config.js" ]
