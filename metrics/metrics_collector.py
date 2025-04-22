import os
import time
import requests
import json
from prometheus_client import start_http_server, Gauge
import telegram

# Configuration
API_URL = "http://host.docker.internal:8000"  # URL de l'API MCP-llama sur la machine hôte
JWT_TOKEN = os.getenv("JWT_TOKEN")  # Token JWT pour l'authentification
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
METRICS_PORT = 9100
CHECK_INTERVAL = 300  # 5 minutes

# Headers pour l'authentification
headers = {
    "Authorization": f"Bearer {JWT_TOKEN}",
    "Content-Type": "application/json"
}

# Métriques Prometheus
node_cpu_usage = Gauge('node_cpu_usage', 'CPU usage of the node')
node_memory_usage = Gauge('node_memory_usage', 'Memory usage of the node')
node_disk_usage = Gauge('node_disk_usage', 'Disk usage of the node')
node_network_in = Gauge('node_network_in', 'Network incoming traffic')
node_network_out = Gauge('node_network_out', 'Network outgoing traffic')
node_uptime = Gauge('node_uptime', 'Node uptime in seconds')

# Client Telegram (optionnel)
bot = None
if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
    try:
        bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
    except Exception as e:
        print(f"Erreur lors de l'initialisation du bot Telegram : {e}")

def get_node_metrics():
    try:
        if not JWT_TOKEN:
            raise ValueError("Le token JWT n'est pas configuré")
            
        response = requests.get(f"{API_URL}/nodes/feustey/metrics", headers=headers)
        if response.status_code == 401:
            print("Erreur d'authentification : Token JWT invalide ou expiré")
            return None
        elif response.status_code != 200:
            print(f"Erreur API : {response.status_code} - {response.text}")
            return None
            
        return response.json()
    except Exception as e:
        print(f"Erreur lors de la récupération des métriques : {e}")
        return None

def analyze_metrics(metrics):
    recommendations = []
    
    # Analyse CPU
    if metrics['cpu_usage'] > 80:
        recommendations.append("⚠️ Utilisation CPU élevée (>80%). Considérez l'augmentation des ressources CPU.")
    
    # Analyse Mémoire
    if metrics['memory_usage'] > 85:
        recommendations.append("⚠️ Utilisation mémoire élevée (>85%). Augmentez la RAM ou optimisez l'utilisation mémoire.")
    
    # Analyse Disque
    if metrics['disk_usage'] > 90:
        recommendations.append("⚠️ Espace disque critique (>90%). Nettoyez les fichiers inutiles ou augmentez l'espace disque.")
    
    # Analyse Réseau
    if metrics['network_in'] > 1000000000 or metrics['network_out'] > 1000000000:  # 1GB/s
        recommendations.append("⚠️ Trafic réseau élevé. Vérifiez les connexions et optimisez le trafic.")
    
    return recommendations

def send_telegram_alert(recommendations):
    if not recommendations or not bot:
        return
    
    message = "🔍 Recommandations pour le nœud Feustey :\n\n"
    message += "\n".join(recommendations)
    
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    except Exception as e:
        print(f"Erreur lors de l'envoi du message Telegram : {e}")

def update_metrics(metrics):
    node_cpu_usage.set(metrics['cpu_usage'])
    node_memory_usage.set(metrics['memory_usage'])
    node_disk_usage.set(metrics['disk_usage'])
    node_network_in.set(metrics['network_in'])
    node_network_out.set(metrics['network_out'])
    node_uptime.set(metrics['uptime'])

def main():
    # Démarrer le serveur HTTP pour Prometheus
    start_http_server(METRICS_PORT)
    print(f"Serveur de métriques démarré sur le port {METRICS_PORT}")
    
    while True:
        metrics = get_node_metrics()
        if metrics:
            update_metrics(metrics)
            recommendations = analyze_metrics(metrics)
            if recommendations:
                send_telegram_alert(recommendations)
                print("Recommandations :", "\n".join(recommendations))
        
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main() 