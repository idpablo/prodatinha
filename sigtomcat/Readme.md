# Deploy das aplicações Prodata com o tomcat no Docker:
 
# Com o Docker instalado caminhe ate o diretorio aonde o arquivo Dockerfile se encontra.
# Verifique se dentro do diretorio contem os asquivos Dockerfile do sig e sigpwebfuncoes(caso haja necessiade use essa documentação como base para as demais aplicações).
# O banco de dados deve estar devidade configurado, caso queria apontar para outro banco(exerno por exemplo) edite o arquivo ".properties" dentro dos seguintes diretorios no .war:

# Nota: User o Winrar(Apenas windows) para navegar dentro do arquivo ".war" 

# sigpwebfuncoes

sigpwebfuncoes.war\WEB-INF\classes\servico\comun\SigpConexao.properties

# sig 

# Por padrão as aplicações se conectão sem a necessidade de alteração nas credenciais:

# ip: localhost
# port: 5432 
# database: sch
# user: postgres
# password: prodata

# Comando para dar build na imagem Docker inicial 

docker build -t sigpwebfuncoes .

# Executando container com a imagem criada:

docker run -it --rm -p 8080:8080 --name sigpwebfuncoes sigpwebfuncoes

# Acesse a pagina referente ao Sig Funcoes e o execute:

http://localhost:8080/sigpwebfuncoes/

# Apos a finalização do funcoes o container referente a ele pode ser excluido.

docker image rm -f sigpwebfuncoes

----------------------------------------------------------------------------------------

# Caminhe até o diretorio aonde se encontra o "sig.war" e o Dockerfile referente ao sig

docker build -t sig .

# Executando container com a imagem criada:

docker run -it --rm -p 8082:8080 --name sig sig

# apos o deploy da aplicação ela ficara disponivel no host:

http://localhost:8080/sig/

# apos o deploy da aplicação ela ficara disponivel no host:

http://172.16.30.8:8080/sigpwebfuncoesBetaAngra/funcoes_setup.jsp

#Criar Container padr

CREATE DATABASE sch WITH OWNER = postgres TEMPLATE = template0 ENCODING = 'LATIN1' LC_COLLATE = 'C' LC_CTYPE = 'C' TABLESPACE = pg_default CONNECTION LIMIT = -1 IS_TEMPLATE = False;