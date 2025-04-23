#!/usr/bin/env python
import uvicorn
import argparse
import logging
import os
import sys
import importlib.util
import platform
import socket

# Ajouter le dossier proto au PYTHONPATH
sys.path.append(os.path.join(os.path.dirname(__file__), "proto"))

def get_ip_address():
    """Obtenir l'adresse IP du serveur"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

if __name__ == "__main__":
    # Configuration de l'argument parser
    parser = argparse.ArgumentParser(description="Lancer le serveur API Daznode")
    parser.add_argument(
        "--host", 
        type=str, 
        default="0.0.0.0", 
        help="Adresse d'écoute (par défaut: 0.0.0.0)"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=8000, 
        help="Port d'écoute (par défaut: 8000)"
    )
    parser.add_argument(
        "--reload", 
        action="store_true", 
        help="Activer le rechargement automatique du code"
    )
    parser.add_argument(
        "--production", 
        action="store_true", 
        help="Mode production (désactive le rechargement, optimise les performances)"
    )
    parser.add_argument(
        "--log-level", 
        type=str, 
        default="info",
        choices=["debug", "info", "warning", "error", "critical"],
        help="Niveau de log (par défaut: info)"
    )
    
    args = parser.parse_args()
    
    # Mode production écrase --reload
    if args.production:
        args.reload = False
    
    # Configuration du logging
    log_level = getattr(logging, args.log_level.upper())
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Démarrer le serveur
    # Charger explicitement le module api.py (éviter conflit avec le dossier api/)
    spec = importlib.util.spec_from_file_location(
        "daznode_api_module", os.path.join(os.path.dirname(__file__), "api.py")
    )
    api_module = importlib.util.module_from_spec(spec)
    sys.modules["daznode_api_module"] = api_module
    spec.loader.exec_module(api_module)
    app = api_module.app
    
    # Afficher des informations sur le système
    print(f"\n===== Daznode API =====")
    print(f"OS: {platform.system()} {platform.release()}")
    print(f"Python: {platform.python_version()}")
    print(f"Mode: {'Production' if args.production else 'Développement'}")
    print(f"Rechargement auto: {'Désactivé' if not args.reload else 'Activé'}")
    print(f"Niveau de log: {args.log_level.upper()}")
    
    # Afficher l'URL d'accès
    ip = get_ip_address() if args.host == "0.0.0.0" else args.host
    print(f"\nServeur accessible à:")
    print(f"- Local:   http://localhost:{args.port}")
    print(f"- Réseau:  http://{ip}:{args.port}")
    print(f"- API Doc: http://{ip}:{args.port}/docs")
    print("\nAppuyez sur CTRL+C pour arrêter le serveur")
    print("============================\n")
    
    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level=args.log_level
    ) 