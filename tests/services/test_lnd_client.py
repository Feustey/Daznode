import unittest
from unittest.mock import patch, Mock, MagicMock
import os
from datetime import datetime

# Mocker les modules lnrpc et app.core.config
@patch('services.lnd_client.lnrpc')
@patch('services.lnd_client.settings')
class TestLNDClient(unittest.TestCase):
    """Tests unitaires pour le client LND"""
    
    def setUp(self):
        """Configuration initiale pour chaque test"""
        # Importer après les patches
        from services.lnd_client import LNDClient
        
        # Créer un mock pour le stub
        self.mock_stub = Mock()
        
        # Patcher l'initialisation de LNDClient pour qu'elle retourne notre mock_stub
        def mock_init_with_stub(*args, **kwargs):
            lnd_client = LNDClient(*args, **kwargs)
            lnd_client.stub = self.mock_stub
            return lnd_client
        
        # Appliquer notre patch
        self.patcher = patch('services.lnd_client.LNDClient.__new__', 
                              side_effect=lambda cls, *args, **kwargs: mock_init_with_stub(*args, **kwargs))
        self.mock_init = self.patcher.start()
        
        # Créer une instance du client avec des certificats factices
        self.lnd_client = LNDClient(
            host="127.0.0.1",
            port=10009,
            cert_path="fake_cert.pem",
            macaroon_path="fake_macaroon"
        )
    
    def tearDown(self):
        """Nettoyage après chaque test"""
        self.patcher.stop()
    
    def test_init(self, mock_settings, mock_lnrpc):
        """Test de l'initialisation du client"""
        self.assertEqual(self.lnd_client.host, "127.0.0.1")
        self.assertEqual(self.lnd_client.port, 10009)
        self.assertEqual(self.lnd_client.cert_path, "fake_cert.pem")
        self.assertEqual(self.lnd_client.macaroon_path, "fake_macaroon")
    
    def test_get_node_info(self, mock_settings, mock_lnrpc):
        """Test de récupération des informations du nœud"""
        # Configurer le mock pour GetInfo
        mock_info = Mock()
        mock_lnrpc.GetInfoResponse.return_value = mock_info
        self.mock_stub.GetInfo.return_value = mock_info
        
        # Configurer les propriétés du mock
        mock_info.identity_pubkey = "02778f4a4eb3a2344b9fd8ee72e7ec5f03f803e5f5273e2e1a2af508"
        mock_info.alias = "Feustey"
        mock_info.block_height = 820305
        mock_info.synced_to_chain = True
        mock_info.synced_to_graph = True
        mock_info.num_active_channels = 10
        mock_info.num_inactive_channels = 2
        mock_info.num_pending_channels = 0
        mock_info.version = "0.16.1"
        mock_info.chains = ["bitcoin"]
        mock_info.uris = ["02778f4a4eb3a2344b9fd8ee72e7ec5f03f803e5f5273e2e1a2af508@127.0.0.1:9735"]
        
        # Appeler la méthode à tester
        result = self.lnd_client.get_node_info()
        
        # Vérifier que les données ont été correctement récupérées
        self.assertEqual(result["pubkey"], "02778f4a4eb3a2344b9fd8ee72e7ec5f03f803e5f5273e2e1a2af508")
        self.assertEqual(result["alias"], "Feustey")
        self.assertEqual(result["block_height"], 820305)
        self.assertEqual(result["synced_to_chain"], True)
        self.assertEqual(result["synced_to_graph"], True)
        self.assertEqual(result["num_active_channels"], 10)
        self.assertEqual(result["num_inactive_channels"], 2)
        self.assertEqual(result["num_pending_channels"], 0)
        self.assertEqual(result["version"], "0.16.1")
        self.assertEqual(result["chains"], ["bitcoin"])
        self.assertEqual(result["uris"], ["02778f4a4eb3a2344b9fd8ee72e7ec5f03f803e5f5273e2e1a2af508@127.0.0.1:9735"])
    
    def test_list_channels(self, mock_settings, mock_lnrpc):
        """Test de liste des canaux"""
        # Configurer le mock pour ListChannels
        mock_channels = Mock()
        mock_lnrpc.ListChannelsResponse.return_value = mock_channels
        self.mock_stub.ListChannels.return_value = mock_channels
        
        # Créer un mock pour un canal
        mock_channel1 = Mock()
        mock_channel1.channel_id = 123456
        mock_channel1.remote_pubkey = "remote_pubkey_1"
        mock_channel1.capacity = 1000000
        mock_channel1.local_balance = 600000
        mock_channel1.remote_balance = 400000
        mock_channel1.unsettled_balance = 0
        mock_channel1.active = True
        mock_channel1.private = False
        mock_channel1.initiator = True
        mock_channel1.total_satoshis_sent = 500000
        mock_channel1.total_satoshis_received = 300000
        mock_channel1.num_updates = 100
        mock_channel1.commit_fee = 1000
        mock_channel1.commit_weight = 600
        mock_channel1.fee_per_kw = 500
        mock_channel1.chan_status_flags = "normal"
        mock_channel1.local_chan_reserve_sat = 10000
        mock_channel1.remote_chan_reserve_sat = 10000
        
        # Créer un mock pour un autre canal (inactif)
        mock_channel2 = Mock()
        mock_channel2.channel_id = 789012
        mock_channel2.remote_pubkey = "remote_pubkey_2"
        mock_channel2.capacity = 2000000
        mock_channel2.local_balance = 800000
        mock_channel2.remote_balance = 1200000
        mock_channel2.unsettled_balance = 0
        mock_channel2.active = False
        mock_channel2.private = True
        mock_channel2.initiator = False
        
        # Configurer le mock pour renvoyer ces canaux
        mock_channels.channels = [mock_channel1, mock_channel2]
        
        # Appeler la méthode à tester
        result = self.lnd_client.list_channels()
        
        # Vérifier que le résultat est correct
        self.assertEqual(len(result), 2)
        
        # Vérifier le premier canal
        self.assertEqual(result[0]["channel_id"], "123456")
        self.assertEqual(result[0]["remote_pubkey"], "remote_pubkey_1")
        self.assertEqual(result[0]["capacity"], 1000000)
        self.assertEqual(result[0]["local_balance"], 600000)
        self.assertEqual(result[0]["remote_balance"], 400000)
        self.assertEqual(result[0]["active"], True)
        self.assertEqual(result[0]["private"], False)
        self.assertEqual(result[0]["initiator"], True)
        
        # Vérifier le second canal
        self.assertEqual(result[1]["channel_id"], "789012")
        self.assertEqual(result[1]["active"], False)
        self.assertEqual(result[1]["private"], True)
        self.assertEqual(result[1]["initiator"], False)
        
        # Tester avec seulement les canaux actifs
        result_active = self.lnd_client.list_channels(active_only=True)
        self.assertEqual(len(result_active), 1)
        self.assertEqual(result_active[0]["channel_id"], "123456")
        
        # Tester avec seulement les canaux inactifs
        result_inactive = self.lnd_client.list_channels(inactive_only=True)
        self.assertEqual(len(result_inactive), 1)
        self.assertEqual(result_inactive[0]["channel_id"], "789012")
    
    def test_get_forwarding_history(self, mock_settings, mock_lnrpc):
        """Test de récupération de l'historique de forwarding"""
        # Configurer le mock pour ForwardingHistory
        mock_forwarding = Mock()
        mock_lnrpc.ForwardingHistoryResponse.return_value = mock_forwarding
        self.mock_stub.ForwardingHistory.return_value = mock_forwarding
        
        # Créer des mocks pour les événements de forwarding
        mock_event1 = Mock()
        mock_event1.timestamp = 1648220000
        mock_event1.chan_id_in = 123456
        mock_event1.chan_id_out = 789012
        mock_event1.amt_in = 1000
        mock_event1.amt_out = 990
        mock_event1.fee = 10
        mock_event1.fee_msat = 10000
        
        mock_event2 = Mock()
        mock_event2.timestamp = 1648230000
        mock_event2.chan_id_in = 789012
        mock_event2.chan_id_out = 345678
        mock_event2.amt_in = 2000
        mock_event2.amt_out = 1980
        mock_event2.fee = 20
        mock_event2.fee_msat = 20000
        
        # Configurer le mock pour renvoyer ces événements
        mock_forwarding.forwarding_events = [mock_event1, mock_event2]
        
        # Appeler la méthode à tester
        start_time = int(datetime(2022, 3, 1).timestamp())
        end_time = int(datetime(2022, 3, 31).timestamp())
        result = self.lnd_client.get_forwarding_history(start_time=start_time, end_time=end_time, limit=100)
        
        # Vérifier que le résultat est correct
        self.assertIn("forwarding_events", result)
        self.assertEqual(len(result["forwarding_events"]), 2)
        
        # Vérifier le premier événement
        event1 = result["forwarding_events"][0]
        self.assertEqual(event1["timestamp"], "1648220000")
        self.assertEqual(event1["chan_id_in"], "123456")
        self.assertEqual(event1["chan_id_out"], "789012")
        self.assertEqual(event1["amt_in"], 1000)
        self.assertEqual(event1["amt_out"], 990)
        self.assertEqual(event1["fee"], 10)
        self.assertEqual(event1["fee_msat"], 10000)
        
        # Vérifier le second événement
        event2 = result["forwarding_events"][1]
        self.assertEqual(event2["timestamp"], "1648230000")

if __name__ == "__main__":
    unittest.main() 