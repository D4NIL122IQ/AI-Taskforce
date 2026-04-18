FROM python:3.11-slim

WORKDIR /app

# Dépendances système (PostgreSQL client + build tools)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Installer les dépendances Python en premier (cache layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code source
COPY . .

# Créer les dossiers persistants
RUN mkdir -p uploads chroma_db

EXPOSE 8000

CMD ["uvicorn", "backend.main.main:app", "--host", "0.0.0.0", "--port", "8000"]
