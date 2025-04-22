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

# Exposer le port
EXPOSE 9100

# Variable d'environnement pour désactiver le buffer de sortie Python
ENV PYTHONUNBUFFERED=1

# Commande par défaut
CMD ["python", "metrics_collector.py"] 