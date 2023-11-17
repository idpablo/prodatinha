FROM ubuntu:latest

RUN apt-get update && apt-get install -y tzdata && apt-get install -y python3 \
    && apt-get install -y python3-pip && apt-get install -y git \
    && apt-get install -y nodejs && apt-get install -y npm \
    && apt-get install -y gradle && apt-get install -y wget

RUN wget -O- https://apt.corretto.aws/corretto.key | apt-key add - 

RUN echo "deb https://apt.corretto.aws stable main" >> /etc/apt/sources.list

RUN apt-get update

RUN apt-get install -y java-1.8.0-amazon-corretto-jdk

ENV TZ=America/Sao_Paulo
ENV LANG pt_BR.utf8
