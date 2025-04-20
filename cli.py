#!/usr/bin/env python
import os
import sys
import json
import asyncio
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime, timedelta

import click
import tabulate
import yaml
import rich
from rich.console import Console
from rich.table import Table
from rich.progress import Progress

from core.config import settings
from services.lnd_client import LNDClient
from services.lnrouter_client import LNRouterClient
from services.metrics_collector import MetricsCollector
from services.node_aggregator import NodeAggregator, EnrichedNode, EnrichedChannel
from services.visualization_exporter import VisualizationExporter

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("daznode-cli")

# Initialisation de la console rich
console = Console()

# Clients et services
lnd_client = LNDClient()
lnrouter_client = LNRouterClient()
metrics_collector = MetricsCollector(lnd_client=lnd_client)
node_aggregator = NodeAggregator(lnd_client=lnd_client, lnrouter_client=lnrouter_client)
visualization_exporter = VisualizationExporter(metrics_collector=metrics_collector, node_aggregator=node_aggregator)

# Groupe principal de commandes
@click.group()
@click.option('--debug/--no-debug', default=False, help="Activer le mode debug")
def cli(debug):
    """Interface en ligne de commande pour Daznode - Gestionnaire de nœud Lightning Network"""
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
        click.echo("Mode debug activé")

# Commande pour afficher les informations du nœud
@cli.command('info')
@click.option('--json', 'output_json', is_flag=True, help="Sortie au format JSON")
def node_info(output_json):
    """Affiche les informations du nœud local"""
    try:
        node_info = lnd_client.get_node_info()
        
        if output_json:
            click.echo(json.dumps(node_info, indent=2))
        else:
            console.print("\n[bold cyan]Informations du nœud Lightning[/bold cyan]")
            console.print(f"Pubkey: [green]{node_info.get('pubkey')}[/green]")
            console.print(f"Alias: [yellow]{node_info.get('alias')}[/yellow]")
            console.print(f"Version: {node_info.get('version')}")
            console.print(f"Canaux actifs: {node_info.get('num_active_channels')}")
            console.print(f"Canaux inactifs: {node_info.get('num_inactive_channels')}")
            console.print(f"Canaux en attente: {node_info.get('num_pending_channels')}")
            console.print(f"Synchronisé avec la chaîne: {'Oui' if node_info.get('synced_to_chain') else 'Non'}")
            console.print(f"Synchronisé avec le graphe: {'Oui' if node_info.get('synced_to_graph') else 'Non'}")
            console.print(f"Hauteur de bloc: {node_info.get('block_height')}")
            
            uris = node_info.get('uris', [])
            if uris:
                console.print("\n[bold]URIs:[/bold]")
                for uri in uris:
                    console.print(f"  - {uri}")
            
    except Exception as e:
        console.print(f"[bold red]Erreur:[/bold red] {str(e)}")
        sys.exit(1)

# Groupe de commandes liées aux canaux
@cli.group()
def channels():
    """Commandes pour gérer les canaux Lightning"""
    pass

@channels.command('list')
@click.option('--active/--all', default=True, help="N'afficher que les canaux actifs")
@click.option('--json', 'output_json', is_flag=True, help="Sortie au format JSON")
def list_channels(active, output_json):
    """Liste les canaux du nœud"""
    try:
        channels = lnd_client.list_channels(active_only=active)
        
        if output_json:
            click.echo(json.dumps(channels, indent=2))
        else:
            table = Table(title=f"Canaux Lightning {'actifs' if active else ''}")
            table.add_column("ID", style="cyan")
            table.add_column("Peer", style="green")
            table.add_column("Capacité", justify="right")
            table.add_column("Balance Locale", justify="right")
            table.add_column("Balance Distante", justify="right")
            table.add_column("Ratio Local", justify="right")
            table.add_column("Actif", justify="center")
            table.add_column("Privé", justify="center")
            
            for channel in channels:
                capacity = channel["capacity"]
                local_balance = channel["local_balance"]
                remote_balance = channel["remote_balance"]
                local_ratio = local_balance / capacity if capacity > 0 else 0
                
                table.add_row(
                    str(channel["channel_id"]),
                    channel["remote_pubkey"][:10] + "...",
                    f"{capacity:,}",
                    f"{local_balance:,}",
                    f"{remote_balance:,}",
                    f"{local_ratio:.1%}",
                    "✓" if channel["active"] else "✗",
                    "✓" if channel["private"] else "✗"
                )
            
            console.print(table)
            console.print(f"Total: {len(channels)} canaux")
            
    except Exception as e:
        console.print(f"[bold red]Erreur:[/bold red] {str(e)}")
        sys.exit(1)

@channels.command('stats')
@click.option('--days', default=30, help="Nombre de jours d'historique à considérer")
def channel_stats(days):
    """Affiche les statistiques des canaux"""
    async def run():
        try:
            with console.status("[bold green]Collecte des statistiques des canaux..."):
                dataset = await visualization_exporter.generate_channel_performance_dataset(days=days)
            
            if "error" in dataset:
                console.print(f"[bold red]Erreur:[/bold red] {dataset['error']}")
                return
            
            # Afficher les statistiques globales
            summary = dataset.get("summary", {})
            console.print("\n[bold cyan]Statistiques globales des canaux[/bold cyan]")
            console.print(f"Période: {days} jours")
            console.print(f"Canaux totaux: {summary.get('total_channels', 0)}")
            console.print(f"Canaux actifs: {summary.get('active_channels', 0)}")
            console.print(f"Canaux rentables: {summary.get('profitable_channels', 0)}")
            console.print(f"Canaux bloqués: {summary.get('stuck_channels', 0)}")
            console.print(f"Capacité totale: {summary.get('total_capacity', 0):,} sats")
            console.print(f"Balance locale totale: {summary.get('total_local_balance', 0):,} sats")
            console.print(f"Volume total: {summary.get('total_volume', 0):,} sats")
            console.print(f"Frais totaux: {summary.get('total_fees', 0):,} sats")
            
            # Afficher les top canaux par volume
            channels_data = dataset.get("channels", [])
            sorted_by_volume = sorted(channels_data, key=lambda x: x.get("forwards_volume", 0), reverse=True)[:10]
            
            if sorted_by_volume:
                console.print("\n[bold cyan]Top 10 canaux par volume[/bold cyan]")
                table = Table()
                table.add_column("ID", style="cyan")
                table.add_column("Capacité", justify="right")
                table.add_column("Volume", justify="right")
                table.add_column("Nb Forwards", justify="right")
                table.add_column("Frais", justify="right")
                table.add_column("Taux effectif", justify="right")
                
                for channel in sorted_by_volume:
                    table.add_row(
                        str(channel.get("channel_id", "")),
                        f"{channel.get('capacity', 0):,}",
                        f"{channel.get('forwards_volume', 0):,}",
                        str(channel.get("forwards_count", 0)),
                        f"{channel.get('fees_earned', 0):,}",
                        f"{channel.get('effective_fee_rate', 0):.1f} ppm"
                    )
                
                console.print(table)
            
        except Exception as e:
            console.print(f"[bold red]Erreur:[/bold red] {str(e)}")
    
    asyncio.run(run())

# Groupe de commandes liées aux métriques
@cli.group()
def metrics():
    """Commandes pour collecter et visualiser les métriques"""
    pass

@metrics.command('collect')
@click.option('--daily', is_flag=True, help="Créer un snapshot quotidien")
@click.option('--export', type=click.Choice(['json', 'csv']), help="Exporter les métriques")
def collect_metrics(daily, export):
    """Collecte les métriques du nœud"""
    async def run():
        try:
            if daily:
                with console.status("[bold green]Création d'un snapshot quotidien..."):
                    snapshot_id = await metrics_collector.create_daily_snapshot()
                console.print(f"[green]Snapshot quotidien créé:[/green] {snapshot_id}")
            else:
                with console.status("[bold green]Collecte des métriques du nœud..."):
                    node_metrics = await metrics_collector.collect_node_metrics()
                    channel_metrics = await metrics_collector.collect_channel_metrics()
                    forwarding_metrics = await metrics_collector.collect_forwarding_metrics(time_window_hours=24)
                
                if export == 'json':
                    export_data = {
                        "timestamp": datetime.now().isoformat(),
                        "node_metrics": node_metrics,
                        "channel_metrics": channel_metrics,
                        "forwarding_metrics": forwarding_metrics
                    }
                    filename = f"metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    with open(filename, 'w') as f:
                        json.dump(export_data, f, indent=2)
                    console.print(f"[green]Métriques exportées vers:[/green] {filename}")
                elif export == 'csv':
                    # Exporter en CSV est plus complexe et nécessite de traiter chaque type séparément
                    Path("exports").mkdir(exist_ok=True)
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    
                    node_file = f"exports/node_metrics_{timestamp}.csv"
                    with open(node_file, 'w') as f:
                        f.write(",".join(node_metrics.keys()) + "\n")
                        f.write(",".join(str(v) for v in node_metrics.values()) + "\n")
                    
                    channel_file = f"exports/channel_metrics_{timestamp}.csv"
                    if channel_metrics:
                        import csv
                        with open(channel_file, 'w', newline='') as f:
                            writer = csv.DictWriter(f, fieldnames=channel_metrics[0].keys())
                            writer.writeheader()
                            writer.writerows(channel_metrics)
                    
                    console.print(f"[green]Métriques exportées vers le répertoire:[/green] exports/")
                else:
                    # Afficher un résumé des métriques
                    console.print("\n[bold cyan]Métriques du nœud[/bold cyan]")
                    console.print(f"Canaux actifs: {node_metrics.get('num_active_channels', 0)}")
                    console.print(f"Capacité totale: {node_metrics.get('total_capacity', 0):,} sats")
                    console.print(f"Balance locale: {node_metrics.get('total_local_balance', 0):,} sats")
                    console.print(f"Ratio local: {node_metrics.get('local_ratio', 0):.1%}")
                    
                    console.print("\n[bold cyan]Métriques de forwarding (24h)[/bold cyan]")
                    console.print(f"Nombre de forwards: {forwarding_metrics.get('total_forwards', 0)}")
                    console.print(f"Volume total: {forwarding_metrics.get('total_amount_forwarded', 0):,} sats")
                    console.print(f"Frais gagnés: {forwarding_metrics.get('total_fees_earned', 0):,} sats")
                    console.print(f"Taux moyen: {forwarding_metrics.get('avg_fee_rate_ppm', 0):.1f} ppm")
                    
        except Exception as e:
            console.print(f"[bold red]Erreur:[/bold red] {str(e)}")
    
    asyncio.run(run())

# Groupe de commandes liées aux visualisations
@cli.group()
def viz():
    """Commandes pour générer des visualisations"""
    pass

@viz.command('network')
@click.option('--export', type=click.Choice(['json', 'csv']), help="Format d'export")
@click.option('--output', '-o', type=click.Path(), help="Chemin du fichier d'export")
def network_graph(export, output):
    """Génère un dataset de graphe réseau"""
    async def run():
        try:
            with console.status("[bold green]Génération du graphe réseau..."):
                dataset = await visualization_exporter.generate_network_graph_dataset()
            
            if "error" in dataset:
                console.print(f"[bold red]Erreur:[/bold red] {dataset['error']}")
                return
            
            if export:
                if export == 'json':
                    if not output:
                        output = f"network_graph_{datetime.now().strftime('%Y%m%d')}.json"
                    with open(output, 'w') as f:
                        json.dump(dataset, f, indent=2)
                elif export == 'csv':
                    if not output:
                        output = f"network_graph_{datetime.now().strftime('%Y%m%d')}.csv"
                    visualization_exporter.export_to_csv("network_graph", output)
                
                console.print(f"[green]Dataset exporté vers:[/green] {output}")
            else:
                # Afficher un résumé
                console.print("\n[bold cyan]Graphe réseau[/bold cyan]")
                console.print(f"Nombre de nœuds: {len(dataset.get('nodes', []))}")
                console.print(f"Nombre de canaux: {len(dataset.get('edges', []))}")
                console.print(f"Capacité totale: {dataset.get('metadata', {}).get('totalCapacity', 0):,} sats")
                
                # Afficher les premiers nœuds
                console.print("\n[bold]Nœuds:[/bold]")
                for i, node in enumerate(dataset.get('nodes', [])[:5]):
                    console.print(f"  {i+1}. {node.get('label')} ({node.get('id')[:10]}...)")
                
                if len(dataset.get('nodes', [])) > 5:
                    console.print(f"  ... et {len(dataset.get('nodes', [])) - 5} autres nœuds")
        
        except Exception as e:
            console.print(f"[bold red]Erreur:[/bold red] {str(e)}")
    
    asyncio.run(run())

@viz.command('heatmap')
@click.option('--resolution', type=click.Choice(['hour', 'day', 'week']), default='hour', 
              help="Résolution temporelle")
@click.option('--export', type=click.Choice(['json', 'csv', 'parquet']), help="Format d'export")
@click.option('--output', '-o', type=click.Path(), help="Chemin du fichier d'export")
def routing_heatmap(resolution, export, output):
    """Génère un dataset pour heatmap de routage"""
    async def run():
        try:
            with console.status(f"[bold green]Génération de la heatmap de routage (résolution: {resolution})..."):
                dataset = await visualization_exporter.generate_routing_heatmap_dataset(time_resolution=resolution)
            
            if "error" in dataset:
                console.print(f"[bold red]Erreur:[/bold red] {dataset['error']}")
                return
            
            if export:
                if not output:
                    output = f"routing_heatmap_{resolution}_{datetime.now().strftime('%Y%m%d')}.{export}"
                
                if export == 'json':
                    visualization_exporter.export_to_json("routing_heatmap", output)
                elif export == 'csv':
                    visualization_exporter.export_to_csv("routing_heatmap", output)
                elif export == 'parquet':
                    visualization_exporter.export_to_parquet("routing_heatmap", output)
                
                console.print(f"[green]Dataset exporté vers:[/green] {output}")
            else:
                # Afficher un résumé
                metadata = dataset.get('metadata', {})
                console.print("\n[bold cyan]Heatmap de routage[/bold cyan]")
                console.print(f"Résolution: {resolution}")
                console.print(f"Période: {dataset.get('start_time')} à {dataset.get('end_time')}")
                console.print(f"Nombre de forwards: {metadata.get('total_forwards', 0)}")
                console.print(f"Volume total: {metadata.get('total_amount', 0):,} sats")
                console.print(f"Frais totaux: {metadata.get('total_fees', 0):,} sats")
                console.print(f"Canaux actifs: {metadata.get('active_channels', 0)}")
                
                # Afficher un échantillon de données
                heatmap_data = dataset.get('heatmap_data', [])
                if heatmap_data:
                    console.print("\n[bold]Exemple de données:[/bold]")
                    table = Table()
                    table.add_column("Période", style="cyan")
                    table.add_column("Canal", style="green")
                    table.add_column("Montant", justify="right")
                    table.add_column("Frais", justify="right")
                    table.add_column("Nb Forwards", justify="right")
                    
                    for data in heatmap_data[:5]:
                        if data.get("count", 0) > 0:  # Ne montrer que les entrées avec activité
                            table.add_row(
                                data.get("time_bucket", ""),
                                data.get("channel_id", "")[:10] + "...",
                                f"{data.get('amount', 0):,}",
                                f"{data.get('fee', 0):,}",
                                str(data.get("count", 0))
                            )
                    
                    console.print(table)
        
        except Exception as e:
            console.print(f"[bold red]Erreur:[/bold red] {str(e)}")
    
    asyncio.run(run())

@viz.command('fees')
@click.option('--export', type=click.Choice(['json', 'csv']), help="Format d'export")
@click.option('--output', '-o', type=click.Path(), help="Chemin du fichier d'export")
def fee_optimization(export, output):
    """Génère un dataset pour optimisation des frais"""
    async def run():
        try:
            with console.status("[bold green]Génération du dataset d'optimisation des frais..."):
                dataset = await visualization_exporter.generate_fee_optimization_dataset()
            
            if "error" in dataset:
                console.print(f"[bold red]Erreur:[/bold red] {dataset['error']}")
                return
            
            if export:
                if not output:
                    output = f"fee_optimization_{datetime.now().strftime('%Y%m%d')}.{export}"
                
                if export == 'json':
                    visualization_exporter.export_to_json("fee_optimization", output)
                elif export == 'csv':
                    visualization_exporter.export_to_csv("fee_optimization", output)
                
                console.print(f"[green]Dataset exporté vers:[/green] {output}")
            else:
                # Afficher un résumé et des recommandations
                metadata = dataset.get('metadata', {})
                console.print("\n[bold cyan]Optimisation des frais[/bold cyan]")
                console.print(f"Canaux totaux: {metadata.get('total_channels', 0)}")
                console.print(f"Canaux actifs pour le forwarding: {metadata.get('active_forwarding_channels', 0)}")
                console.print(f"Nombre de forwards: {metadata.get('total_forwards', 0)}")
                console.print(f"Frais totaux: {metadata.get('total_fees', 0):,} sats")
                console.print(f"Taux de frais moyen: {metadata.get('avg_effective_fee_rate', 0):.1f} ppm")
                
                # Afficher les suggestions de frais
                channels_data = dataset.get('channels', [])
                
                # Filtrer uniquement les canaux avec des suggestions
                channels_with_suggestions = [c for c in channels_data if c.get("suggested_fee_rate") is not None]
                
                if channels_with_suggestions:
                    console.print("\n[bold]Suggestions de taux de frais:[/bold]")
                    table = Table()
                    table.add_column("Canal", style="cyan")
                    table.add_column("Actuel", justify="right", style="yellow")
                    table.add_column("Suggéré", justify="right", style="green")
                    table.add_column("Écart", justify="right")
                    table.add_column("Forwards", justify="right")
                    table.add_column("Volume", justify="right")
                    
                    # Trier par nombre de forwards
                    sorted_channels = sorted(channels_with_suggestions, 
                                            key=lambda x: x.get("total_forwards", 0), 
                                            reverse=True)[:10]
                    
                    for channel in sorted_channels:
                        current = channel.get("current_fee_rate")
                        suggested = channel.get("suggested_fee_rate")
                        
                        if current is not None and suggested is not None:
                            diff = suggested - current
                            diff_str = f"{diff:+.0f}"
                            diff_style = "green" if diff > 0 else "red" if diff < 0 else ""
                            
                            table.add_row(
                                channel.get("channel_id", "")[:10] + "...",
                                f"{current:.0f} ppm",
                                f"{suggested:.0f} ppm",
                                f"[{diff_style}]{diff_str} ppm[/{diff_style}]" if diff_style else f"{diff_str} ppm",
                                str(channel.get("total_forwards", 0)),
                                f"{channel.get('total_amount', 0):,}"
                            )
                    
                    console.print(table)
                    console.print("\n[italic]Note: Ces suggestions sont basées sur l'historique de forwarding et " 
                                "l'utilisation des canaux.[/italic]")
        
        except Exception as e:
            console.print(f"[bold red]Erreur:[/bold red] {str(e)}")
    
    asyncio.run(run())

# Groupe de commandes liées à l'analyse approfondie du réseau
@cli.group()
def network():
    """Commandes pour analyser le réseau Lightning"""
    pass

@network.command('stats')
def network_stats():
    """Affiche les statistiques globales du réseau Lightning"""
    async def run():
        try:
            with console.status("[bold green]Récupération des statistiques réseau..."):
                context = await node_aggregator.get_network_context()
            
            if "error" in context:
                console.print(f"[bold red]Erreur:[/bold red] {context['error']}")
                return
            
            # Afficher les statistiques du réseau
            mcp = context.get('mcp', {})
            lnrouter = context.get('lnrouter', {})
            
            console.print("\n[bold cyan]Statistiques du réseau Lightning[/bold cyan]")
            
            table = Table(title="Comparaison des sources de données")
            table.add_column("Métrique", style="cyan")
            table.add_column("MCP", justify="right")
            table.add_column("LNRouter", justify="right")
            
            table.add_row("Nombre de nœuds", f"{mcp.get('num_nodes', 0):,}", f"{lnrouter.get('num_nodes', 0):,}")
            table.add_row("Nombre de canaux", f"{mcp.get('num_channels', 0):,}", f"{lnrouter.get('num_channels', 0):,}")
            table.add_row("Capacité totale", f"{mcp.get('total_capacity', 0):,} sats", f"{lnrouter.get('total_capacity', 0):,} sats")
            table.add_row("Taille moyenne des canaux", f"{mcp.get('avg_channel_size', 0):,} sats", f"{lnrouter.get('avg_channel_size', 0):,} sats")
            
            console.print(table)
            
            # Afficher des métriques avancées de LNRouter
            console.print("\n[bold]Métriques avancées de topologie:[/bold]")
            console.print(f"Diamètre du réseau: {lnrouter.get('network_diameter', 'N/A')}")
            console.print(f"Densité du réseau: {lnrouter.get('density', 0):.6f}")
            console.print(f"Degré moyen des nœuds: {lnrouter.get('avg_degree', 0):.2f}")
            console.print(f"Ratio du composant principal: {lnrouter.get('largest_component_ratio', 0):.2%}")
            
            # Afficher les nœuds centraux
            top_nodes = context.get('top_nodes', [])
            if top_nodes:
                console.print("\n[bold]Nœuds les plus centraux:[/bold]")
                table = Table()
                table.add_column("Pubkey", style="cyan")
                table.add_column("Centralité", justify="right")
                
                for node in top_nodes[:5]:
                    table.add_row(
                        node.get("pubkey", "")[:15] + "...",
                        f"{node.get('centrality', 0):.6f}"
                    )
                
                console.print(table)
        
        except Exception as e:
            console.print(f"[bold red]Erreur:[/bold red] {str(e)}")
    
    asyncio.run(run())

@network.command('node')
@click.argument('pubkey')
def node_details(pubkey):
    """Affiche les détails d'un nœud spécifique"""
    async def run():
        try:
            with console.status(f"[bold green]Récupération des informations du nœud {pubkey[:10]}..."):
                node = await node_aggregator.get_enriched_node(pubkey)
            
            console.print(f"\n[bold cyan]Détails du nœud {node.alias or pubkey[:10]}...[/bold cyan]")
            console.print(f"Pubkey: [green]{node.pubkey}[/green]")
            console.print(f"Alias: [yellow]{node.alias or 'Non défini'}[/yellow]")
            console.print(f"Nombre de canaux: {len(node.channels)}")
            console.print(f"Capacité totale: {node.total_capacity:,} sats")
            
            # Afficher les canaux
            if node.channels:
                console.print("\n[bold]Canaux:[/bold]")
                table = Table()
                table.add_column("ID", style="cyan")
                table.add_column("Capacité", justify="right")
                table.add_column("Balance Locale", justify="right")
                table.add_column("Ratio Local", justify="right")
                table.add_column("Actif", justify="center")
                table.add_column("Index Blocage", justify="right")
                
                for channel in list(node.channels.values())[:10]:
                    stuck_style = "red" if channel.stuck_index > 70 else "yellow" if channel.stuck_index > 50 else "green"
                    
                    table.add_row(
                        str(channel.channel_id),
                        f"{channel.capacity:,}",
                        f"{channel.local_balance:,}",
                        f"{channel.local_ratio:.1%}",
                        "✓" if channel.active else "✗",
                        f"[{stuck_style}]{channel.stuck_index}[/{stuck_style}]"
                    )
                
                console.print(table)
                
                if len(node.channels) > 10:
                    console.print(f"... et {len(node.channels) - 10} autres canaux")
                
                # Afficher les recommandations
                recommendations = node_aggregator.get_channel_recommendations(node)
                if recommendations:
                    console.print("\n[bold yellow]Recommandations:[/bold yellow]")
                    for i, rec in enumerate(recommendations[:5]):
                        severity = rec.get("severity", "medium")
                        color = "red" if severity == "high" else "yellow" if severity == "medium" else "green"
                        console.print(f"[{color}]{i+1}. {rec.get('details')}[/{color}]")
                        console.print(f"   Suggestion: {rec.get('suggestion')}")
                    
                    if len(recommendations) > 5:
                        console.print(f"... et {len(recommendations) - 5} autres recommandations")
        
        except Exception as e:
            console.print(f"[bold red]Erreur:[/bold red] {str(e)}")
    
    asyncio.run(run())

if __name__ == '__main__':
    cli() 