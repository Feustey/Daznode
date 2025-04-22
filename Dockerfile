FROM python:3.10-slim

WORKDIR /app

# Installer des dépendances système
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libffi-dev \
    g++ \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copier les fichiers de requirements
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code de l'application
COPY . .

# Créer les répertoires nécessaires
RUN mkdir -p /data/cache

# Exposer le port
EXPOSE 8000

# Variable d'environnement pour désactiver le buffer de sortie Python
ENV PYTHONUNBUFFERED=1

# Définir la variable d'environnement pour le chemin des données
ENV DATA_DIR=/data

# Commande par défaut
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"] 