#!/usr/bin/env python
import uvicorn
import argparse
import logging

if __name__ == "__main__":
    # Configuration de l'argument parser
    parser = argparse.ArgumentParser(description="Lancer le serveur API Daznode")
    parser.add_argument(
        "--host", 
        type=str, 
        default="127.0.0.1", 
        help="Adresse d'écoute (par défaut: 127.0.0.1)"
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
        "--log-level", 
        type=str, 
        default="info",
        choices=["debug", "info", "warning", "error", "critical"],
        help="Niveau de log (par défaut: info)"
    )
    
    args = parser.parse_args()
    
    # Configuration du logging
    log_level = getattr(logging, args.log_level.upper())
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Démarrer le serveur
    print(f"Démarrage du serveur API Daznode sur {args.host}:{args.port}...")
    uvicorn.run(
        "api:app", 
        host=args.host, 
        port=args.port, 
        reload=args.reload,
        log_level=args.log_level
    ) 