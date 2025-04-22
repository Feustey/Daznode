from typing import Dict, Any, Optional
import matplotlib.pyplot as plt
import networkx as nx
from datetime import datetime
import json
import logging
from pathlib import Path

from services.data_source_factory import DataSourceFactory
from services.visualization_exporter import VisualizationExporter

logger = logging.getLogger(__name__)

class UmbrelUIExporter:
    """Service d'exportation des visualisations pour l'interface Umbrel"""
    
    def __init__(self, data_source=None):
        self.data_source = data_source or DataSourceFactory.get_data_source()
        self.visualization_exporter = VisualizationExporter(data_source=self.data_source)
        self.output_dir = Path("/data/umbrel-ui")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    async def generate_dashboard(self) -> str:
        """Génère un dashboard HTML complet"""
        try:
            # Récupérer les données nécessaires
            network_stats = await self.data_source.get_network_stats()
            graph_data = await self.visualization_exporter.generate_network_graph_dataset()
            
            # Générer les visualisations
            network_graph_svg = await self._generate_network_graph_svg(graph_data)
            stats_charts_svg = await self._generate_stats_charts_svg(network_stats)
            
            # Créer le HTML du dashboard
            dashboard_html = self._create_dashboard_html(
                network_graph_svg=network_graph_svg,
                stats_charts_svg=stats_charts_svg,
                network_stats=network_stats
            )
            
            # Sauvegarder le dashboard
            self._save_dashboard(dashboard_html)
            
            return dashboard_html
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération du dashboard: {str(e)}")
            raise
    
    async def _generate_network_graph_svg(self, graph_data: Dict[str, Any]) -> str:
        """Génère un SVG du graphe du réseau"""
        try:
            # Créer le graphe NetworkX
            G = nx.Graph()
            
            # Ajouter les nœuds
            for node in graph_data["nodes"]:
                G.add_node(
                    node["pub_key"],
                    alias=node["alias"],
                    color=node["color"]
                )
            
            # Ajouter les canaux
            for channel in graph_data["channels"]:
                G.add_edge(
                    channel["node1_pub"],
                    channel["node2_pub"],
                    capacity=channel["capacity"]
                )
            
            # Configurer le style du graphe
            plt.figure(figsize=(12, 8))
            pos = nx.spring_layout(G)
            
            # Dessiner les nœuds
            nx.draw_networkx_nodes(
                G, pos,
                node_color=[G.nodes[n]["color"] for n in G.nodes()],
                node_size=100
            )
            
            # Dessiner les arêtes
            nx.draw_networkx_edges(
                G, pos,
                width=[G[u][v]["capacity"] / 1000000 for u, v in G.edges()],
                alpha=0.5
            )
            
            # Ajouter les labels
            nx.draw_networkx_labels(
                G, pos,
                labels={n: G.nodes[n]["alias"] for n in G.nodes()}
            )
            
            # Convertir en SVG
            plt.axis('off')
            svg = self._fig_to_svg(plt.gcf())
            plt.close()
            
            return svg
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération du graphe SVG: {str(e)}")
            raise
    
    async def _generate_stats_charts_svg(self, stats: Dict[str, Any]) -> str:
        """Génère des graphiques SVG pour les statistiques"""
        try:
            # Créer les graphiques
            fig, axes = plt.subplots(2, 2, figsize=(12, 8))
            
            # Graphique du nombre de nœuds
            axes[0, 0].bar(["Nœuds"], [stats["num_nodes"]])
            axes[0, 0].set_title("Nombre de nœuds")
            
            # Graphique du nombre de canaux
            axes[0, 1].bar(["Canaux"], [stats["num_channels"]])
            axes[0, 1].set_title("Nombre de canaux")
            
            # Graphique de la capacité totale
            axes[1, 0].bar(["Capacité"], [stats["total_capacity"] / 100000000])
            axes[1, 0].set_title("Capacité totale (BTC)")
            
            # Graphique de la distribution des canaux
            axes[1, 1].hist([c["capacity"] for c in stats.get("channels", [])], bins=20)
            axes[1, 1].set_title("Distribution des capacités")
            
            plt.tight_layout()
            
            # Convertir en SVG
            svg = self._fig_to_svg(fig)
            plt.close()
            
            return svg
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération des graphiques SVG: {str(e)}")
            raise
    
    def _create_dashboard_html(self, network_graph_svg: str, stats_charts_svg: str, network_stats: Dict[str, Any]) -> str:
        """Crée le HTML du dashboard"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Daznode Dashboard</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .container {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
                .card {{ background: white; padding: 20px; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                .stats {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; }}
                .stat-item {{ text-align: center; }}
                .last-update {{ text-align: right; font-size: 0.8em; color: #666; }}
            </style>
        </head>
        <body>
            <h1>Daznode Dashboard</h1>
            <div class="container">
                <div class="card">
                    <h2>Graphe du réseau</h2>
                    {network_graph_svg}
                </div>
                <div class="card">
                    <h2>Statistiques</h2>
                    <div class="stats">
                        <div class="stat-item">
                            <h3>Nœuds</h3>
                            <p>{network_stats["num_nodes"]}</p>
                        </div>
                        <div class="stat-item">
                            <h3>Canaux</h3>
                            <p>{network_stats["num_channels"]}</p>
                        </div>
                        <div class="stat-item">
                            <h3>Capacité totale</h3>
                            <p>{network_stats["total_capacity"] / 100000000:.2f} BTC</p>
                        </div>
                    </div>
                    {stats_charts_svg}
                </div>
            </div>
            <div class="last-update">
                Dernière mise à jour: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            </div>
        </body>
        </html>
        """
    
    def _save_dashboard(self, html_content: str):
        """Sauvegarde le dashboard dans un fichier"""
        try:
            output_file = self.output_dir / "dashboard.html"
            output_file.write_text(html_content)
            logger.info(f"Dashboard sauvegardé dans {output_file}")
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde du dashboard: {str(e)}")
            raise
    
    def _fig_to_svg(self, fig) -> str:
        """Convertit une figure matplotlib en SVG"""
        from io import StringIO
        svg = StringIO()
        fig.savefig(svg, format='svg')
        return svg.getvalue() 