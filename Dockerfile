# Imagem oficial do Python (versão estável e enxuta)
FROM python:3.13-slim

# Evita que o Python grave arquivos .pyc e bufferize a saída do terminal
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Define o diretório de trabalho dentro do contêiner
WORKDIR /app

# Instala dependências do sistema necessárias
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copia e instala as dependências Python
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código-fonte do projeto
COPY . /app/

# Porta padrão de execução do Django
EXPOSE 8000

# Executa migrações do banco de dados e inicia o servidor Django em 0.0.0.0
CMD ["sh", "-c", "python manage.py migrate && python manage.py popular_banco && python manage.py runserver 0.0.0.0:8000"]
