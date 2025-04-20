import unittest
import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from datetime import datetime

# Utiliser patch pour mocker les imports
@patch('services.metrics_collector.MCPService')
@patch('services.metrics_collector.LNRouterClient')
class TestMetricsCollector(unittest.TestCase):
    """Tests unitaires pour le collecteur de métriques"""
    
    def setUp(self):
        """Configuration initiale pour chaque test"""
        # On importera MetricsCollector seulement après le patch des imports
        from services.metrics_collector import MetricsCollector
        from services.lnd_client import LNDClient
        
        self.mock_lnd_client = Mock(spec=LNDClient)
        self.metrics_collector = MetricsCollector(
            db_connection_string=None,  # Pas de connexion à la BDD pour les tests
            lnd_client=self.mock_lnd_client
        )
        
        # Configuration des mocks
        self.mock_lnd_client.get_node_info.return_value = {
            "pubkey": "02778f4a4eb3a2344b9fd8ee72e7ec5f03f803e5f5273e2e1a2af508",
            "alias": "Feustey",
            "block_height": 820305,
            "synced_to_chain": True,
            "synced_to_graph": True,
            "num_active_channels": 10,
            "num_inactive_channels": 2,
            "num_pending_channels": 0,
            "version": "0.16.1"
        }
        
        self.mock_lnd_client.list_channels.return_value = [
            {
                "channel_id": "123456",
                "remote_pubkey": "remote_pubkey_1",
                "capacity": 1000000,
                "local_balance": 600000,
                "remote_balance": 400000,
                "unsettled_balance": 0,
                "active": True,
                "private": False,
                "initiator": True,
                "total_satoshis_sent": 500000,
                "total_satoshis_received": 300000,
                "num_updates": 100,
                "commit_fee": 1000,
                "commit_weight": 600,
                "fee_per_kw": 500,
                "chan_status_flags": "normal",
                "local_chan_reserve_sat": 10000,
                "remote_chan_reserve_sat": 10000,
                "channel_point": "txid:0"
            },
            {
                "channel_id": "789012",
                "remote_pubkey": "remote_pubkey_2",
                "capacity": 2000000,
                "local_balance": 800000,
                "remote_balance": 1200000,
                "unsettled_balance": 0,
                "active": True,
                "private": True,
                "initiator": False,
                "total_satoshis_sent": 300000,
                "total_satoshis_received": 500000,
                "num_updates": 50,
                "commit_fee": 2000,
                "commit_weight": 700,
                "fee_per_kw": 600,
                "chan_status_flags": "normal",
                "local_chan_reserve_sat": 20000,
                "remote_chan_reserve_sat": 20000,
                "channel_point": "txid:1"
            },
            {
                "channel_id": "345678",
                "remote_pubkey": "remote_pubkey_3",
                "capacity": 1500000,
                "local_balance": 700000,
                "remote_balance": 800000,
                "unsettled_balance": 0,
                "active": False,
                "private": False,
                "initiator": True,
                "total_satoshis_sent": 200000,
                "total_satoshis_received": 100000,
                "num_updates": 30,
                "commit_fee": 1500,
                "commit_weight": 650,
                "fee_per_kw": 550,
                "chan_status_flags": "inactive",
                "local_chan_reserve_sat": 15000,
                "remote_chan_reserve_sat": 15000,
                "channel_point": "txid:2"
            }
        ]
        
        self.mock_lnd_client.get_forwarding_history.return_value = {
            "forwarding_events": [
                {
                    "timestamp": "1648220000",
                    "chan_id_in": "123456",
                    "chan_id_out": "789012",
                    "amt_in": 1000,
                    "amt_out": 990,
                    "fee": 10,
                    "fee_msat": 10000
                },
                {
                    "timestamp": "1648230000",
                    "chan_id_in": "789012",
                    "chan_id_out": "345678",
                    "amt_in": 2000,
                    "amt_out": 1980,
                    "fee": 20,
                    "fee_msat": 20000
                }
            ]
        }
    
    @pytest.mark.asyncio
    async def test_collect_node_metrics(self, mock_lnrouter_client, mock_mcp_service):
        """Test de la collecte des métriques du nœud"""
        result = await self.metrics_collector.collect_node_metrics()
        
        # Vérifier que le résultat contient les clés attendues
        expected_keys = [
            "node_pubkey", "timestamp", "num_active_channels", "num_inactive_channels",
            "num_pending_channels", "total_channels", "channels_by_state", "block_height",
            "synced_to_chain", "synced_to_graph", "total_capacity", "total_local_balance",
            "total_remote_balance", "total_unsettled_balance", "local_ratio", "version"
        ]
        
        for key in expected_keys:
            self.assertIn(key, result)
        
        # Vérifier quelques valeurs calculées
        self.assertEqual(result["node_pubkey"], "02778f4a4eb3a2344b9fd8ee72e7ec5f03f803e5f5273e2e1a2af508")
        self.assertEqual(result["num_active_channels"], 10)
        self.assertEqual(result["total_channels"], 3)
        self.assertEqual(result["total_capacity"], 4500000)
        self.assertEqual(result["total_local_balance"], 2100000)
        self.assertEqual(result["total_remote_balance"], 2400000)
        
        # Vérifier les canaux par état
        channels_by_state = result["channels_by_state"]
        self.assertEqual(channels_by_state["active"], 2)
        self.assertEqual(channels_by_state["inactive"], 1)
        self.assertEqual(channels_by_state["private"], 1)
        self.assertEqual(channels_by_state["public"], 2)
        self.assertEqual(channels_by_state["initiated_by_us"], 2)
        self.assertEqual(channels_by_state["initiated_by_peer"], 1)
    
    @pytest.mark.asyncio
    async def test_collect_channel_metrics(self, mock_lnrouter_client, mock_mcp_service):
        """Test de la collecte des métriques des canaux"""
        result = await self.metrics_collector.collect_channel_metrics()
        
        # Vérifier que le nombre de résultats correspond au nombre de canaux
        self.assertEqual(len(result), 3)
        
        # Vérifier les métriques du premier canal
        first_channel = result[0]
        self.assertEqual(first_channel["channel_id"], "123456")
        self.assertEqual(first_channel["capacity"], 1000000)
        self.assertEqual(first_channel["local_balance"], 600000)
        self.assertEqual(first_channel["remote_balance"], 400000)
        
        # Vérifier les métriques calculées
        self.assertAlmostEqual(first_channel["local_ratio"], 0.6)
        self.assertAlmostEqual(first_channel["remote_ratio"], 0.4)
        
        # Le score d'équilibre devrait être 0.8 pour un ratio de 0.6 (1 - abs(0.5 - 0.6) * 2)
        self.assertAlmostEqual(first_channel["balance_score"], 0.8)
    
    @pytest.mark.asyncio
    async def test_collect_forwarding_metrics(self, mock_lnrouter_client, mock_mcp_service):
        """Test de la collecte des métriques de forwarding"""
        result = await self.metrics_collector.collect_forwarding_metrics(time_window_hours=24)
        
        # Vérifier les métriques de base
        self.assertIn("total_forwards", result)
        self.assertIn("total_amount_in", result)
        self.assertIn("total_amount_out", result)
        self.assertIn("total_fees", result)
        self.assertIn("average_fee", result)
        self.assertIn("fee_ppm", result)
        
        # Vérifier les valeurs calculées
        self.assertEqual(result["total_forwards"], 2)
        self.assertEqual(result["total_amount_in"], 3000)
        self.assertEqual(result["total_amount_out"], 2970)
        self.assertEqual(result["total_fees"], 30)
        self.assertEqual(result["average_fee"], 15)
        self.assertAlmostEqual(result["fee_ppm"], 10000)  # 30/3000*1000000
        
        # Vérifier les canaux impliqués
        self.assertEqual(len(result["channels_involved"]), 3)
        
        # Vérifier les statistiques par montant
        self.assertIn("amount_distribution", result)

if __name__ == "__main__":
    unittest.main() 