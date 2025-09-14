# mugiwara-store-backend/Dockerfile

# 1. Define a imagem base. Usaremos a imagem oficial do Python 3.9.
FROM python:3.9-slim

# 2. Define o diretório de trabalho dentro do container.
# Todos os comandos seguintes serão executados a partir daqui.
WORKDIR /app

# 3. Copia o arquivo de dependências para o container.
COPY requirements.txt .

# 4. Instala as dependências do Python.
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copia todo o resto do código do backend para o diretório de trabalho no container.
COPY . .

# 6. Expõe a porta 5000, que é a porta padrão do Flask.
EXPOSE 5000

# 7. Define o comando para rodar a aplicação quando o container iniciar.
# Usar host='0.0.0.0' torna a aplicação acessível de fora do container.
CMD ["flask", "run", "--host=0.0.0.0"]