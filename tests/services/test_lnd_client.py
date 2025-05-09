import unittest
from unittest.mock import patch, Mock, MagicMock
import os
from datetime import datetime

# Mocker les modules protobuf
mock_ln = Mock()
mock_lnrpc = Mock()
mock_router = Mock()
mock_routerrpc = Mock()

with patch.dict('sys.modules', {
    'lightning_pb2': mock_ln,
    'lightning_pb2_grpc': mock_lnrpc,
    'router_pb2': mock_router,
    'router_pb2_grpc': mock_routerrpc
}):
    from services.lnd_client import LNDClient

class TestLNDClient(unittest.TestCase):
    """Tests unitaires pour le client LND"""
    
    def setUp(self):
        """Configuration initiale pour chaque test"""
        # Créer un mock pour le stub
        self.mock_stub = Mock()
        
        # Créer une instance du client avec des certificats factices
        self.lnd_client = LNDClient(
            cert_path="fake_cert.pem",
            macaroon_path="fake_macaroon",
            grpc_host="127.0.0.1:10009"
        )
        
        # Remplacer le stub par notre mock
        self.lnd_client._stub = self.mock_stub
        self.lnd_client._router_stub = self.mock_stub
    
    def test_init(self):
        """Test de l'initialisation du client"""
        self.assertEqual(self.lnd_client.grpc_host, "127.0.0.1:10009")
        self.assertEqual(self.lnd_client.cert_path, "fake_cert.pem")
        self.assertEqual(self.lnd_client.macaroon_path, "fake_macaroon")
    
    def test_get_node_info(self):
        """Test de récupération des informations du nœud"""
        # Configurer le mock pour GetInfo
        mock_info = Mock()
        mock_ln.GetInfoResponse.return_value = mock_info
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
        mock_info.uris = [
            "02778f4a4eb3a2344b9fd8ee72e7ec5f03f803e5f5273e2e1a2af508@127.0.0.1:9735"
        ]
        
        # Appeler la méthode à tester
        result = self.lnd_client.get_node_info()
        
        # Vérifier que les données ont été correctement récupérées
        self.assertEqual(
            result["pubkey"], 
            "02778f4a4eb3a2344b9fd8ee72e7ec5f03f803e5f5273e2e1a2af508"
        )
        self.assertEqual(result["alias"], "Feustey")
        self.assertEqual(result["block_height"], 820305)
        self.assertEqual(result["synced_to_chain"], True)
        self.assertEqual(result["synced_to_graph"], True)
        self.assertEqual(result["num_active_channels"], 10)
        self.assertEqual(result["num_inactive_channels"], 2)
        self.assertEqual(result["num_pending_channels"], 0)
        self.assertEqual(result["version"], "0.16.1")
        self.assertEqual(result["chains"], ["bitcoin"])
        self.assertEqual(
            result["uris"], 
            ["02778f4a4eb3a2344b9fd8ee72e7ec5f03f803e5f5273e2e1a2af508@127.0.0.1:9735"]
        )
    
    def test_list_channels(self):
        """Test de liste des canaux"""
        # Configurer le mock pour ListChannels
        mock_channels = Mock()
        mock_ln.ListChannelsResponse.return_value = mock_channels
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
        mock_channel1.local_balance_msat = 600000000
        mock_channel1.remote_balance_msat = 400000000
        
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
        mock_channel2.total_satoshis_sent = 0
        mock_channel2.total_satoshis_received = 0
        mock_channel2.num_updates = 0
        mock_channel2.commit_fee = 0
        mock_channel2.commit_weight = 0
        mock_channel2.fee_per_kw = 0
        mock_channel2.chan_status_flags = "inactive"
        mock_channel2.local_chan_reserve_sat = 20000
        mock_channel2.remote_chan_reserve_sat = 20000
        mock_channel2.local_balance_msat = 800000000
        mock_channel2.remote_balance_msat = 1200000000
        
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
        self.assertEqual(result[0]["total_satoshis_sent"], 500000)
        self.assertEqual(result[0]["total_satoshis_received"], 300000)
        self.assertEqual(result[0]["num_updates"], 100)
        self.assertEqual(result[0]["commit_fee"], 1000)
        self.assertEqual(result[0]["commit_weight"], 600)
        self.assertEqual(result[0]["fee_per_kw"], 500)
        self.assertEqual(result[0]["chan_status_flags"], "normal")
        self.assertEqual(result[0]["local_chan_reserve_sat"], 10000)
        self.assertEqual(result[0]["remote_chan_reserve_sat"], 10000)
        self.assertEqual(result[0]["local_balance_msat"], 600000000)
        self.assertEqual(result[0]["remote_balance_msat"], 400000000)
        
        # Vérifier le second canal
        self.assertEqual(result[1]["channel_id"], "789012")
        self.assertEqual(result[1]["active"], False)
        self.assertEqual(result[1]["private"], True)
        self.assertEqual(result[1]["initiator"], False)
        self.assertEqual(result[1]["local_balance_msat"], 800000000)
        self.assertEqual(result[1]["remote_balance_msat"], 1200000000)
        
        # Tester avec seulement les canaux actifs
        result_active = self.lnd_client.list_channels(active_only=True)
        self.assertEqual(len(result_active), 1)
        self.assertEqual(result_active[0]["channel_id"], "123456")
        
        # Tester avec seulement les canaux inactifs
        result_inactive = self.lnd_client.list_channels(inactive_only=True)
        self.assertEqual(len(result_inactive), 1)
        self.assertEqual(result_inactive[0]["channel_id"], "789012")
    
    def test_get_forwarding_history(self):
        """Test de récupération de l'historique de forwarding"""
        # Configurer le mock pour ForwardingHistory
        mock_forwarding = Mock()
        mock_ln.ForwardingHistoryResponse.return_value = mock_forwarding
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
        mock_event1.amt_in_msat = 1000000
        mock_event1.amt_out_msat = 990000
        
        mock_event2 = Mock()
        mock_event2.timestamp = 1648230000
        mock_event2.chan_id_in = 789012
        mock_event2.chan_id_out = 345678
        mock_event2.amt_in = 2000
        mock_event2.amt_out = 1980
        mock_event2.fee = 20
        mock_event2.fee_msat = 20000
        mock_event2.amt_in_msat = 2000000
        mock_event2.amt_out_msat = 1980000
        
        # Configurer le mock pour renvoyer ces événements
        mock_forwarding.forwarding_events = [mock_event1, mock_event2]
        mock_forwarding.last_offset_index = 0
        
        # Appeler la méthode à tester
        start_time = int(datetime(2022, 3, 1).timestamp())
        end_time = int(datetime(2022, 3, 31).timestamp())
        result = self.lnd_client.get_forwarding_history(
            start_time=start_time, 
            end_time=end_time, 
            limit=100
        )
        
        # Vérifier que le résultat est correct
        self.assertIn("forwarding_events", result)
        self.assertEqual(len(result["forwarding_events"]), 2)
        
        # Vérifier le premier événement
        event1 = result["forwarding_events"][0]
        self.assertEqual(
            event1["timestamp"], 
            datetime.fromtimestamp(1648220000).isoformat()
        )
        self.assertEqual(event1["chan_id_in"], "123456")
        self.assertEqual(event1["chan_id_out"], "789012")
        self.assertEqual(event1["amt_in"], 1000)
        self.assertEqual(event1["amt_out"], 990)
        self.assertEqual(event1["fee"], 10)
        self.assertEqual(event1["fee_msat"], 10000)
        self.assertEqual(event1["amt_in_msat"], 1000000)
        self.assertEqual(event1["amt_out_msat"], 990000)
        
        # Vérifier le second événement
        event2 = result["forwarding_events"][1]
        self.assertEqual(
            event2["timestamp"], 
            datetime.fromtimestamp(1648230000).isoformat()
        )
        self.assertEqual(event2["chan_id_in"], "789012")
        self.assertEqual(event2["chan_id_out"], "345678")
        self.assertEqual(event2["amt_in"], 2000)
        self.assertEqual(event2["amt_out"], 1980)
        self.assertEqual(event2["fee"], 20)
        self.assertEqual(event2["fee_msat"], 20000)
        self.assertEqual(event2["amt_in_msat"], 2000000)
        self.assertEqual(event2["amt_out_msat"], 1980000)

if __name__ == "__main__":
    unittest.main() 