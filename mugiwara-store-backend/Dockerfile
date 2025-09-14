# 1. Define a imagem base.
FROM python:3.9-slim

# 2. Define o diretório de trabalho.
WORKDIR /app

# 3. Copia e instala as dependências.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copia todo o resto do código do backend.
COPY . .

# 5. Expõe a porta 5000.
EXPOSE 5000

# 6. Define o comando para rodar a aplicação.
CMD ["python", "-u", "app.py"]