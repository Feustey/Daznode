from unittest.mock import MagicMock, AsyncMock
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

class LNDClientMock(MagicMock):
    """Mock du client LND"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.get_node_info = MagicMock(return_value={
            "alias": "test_node",
            "pubkey": "test_pubkey",
            "block_height": 700000,
            "synced_to_chain": True
        })
        
        self.get_channels = MagicMock(return_value=[
            {
                "channel_id": "channel1",
                "remote_pubkey": "pubkey1",
                "capacity": 1000000,
                "local_balance": 500000,
                "remote_balance": 500000,
                "active": True
            }
        ])
        
        self.get_node = MagicMock(return_value={
            "node": {
                "alias": "remote_node",
                "pubkey": "pubkey1",
                "color": "#123456"
            }
        })

class MCPServiceMock(AsyncMock):
    """Mock du service MCP"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_url = "https://api.mcp.test"
        self.api_key = "test_key"
        
        self.get_network_stats = AsyncMock(return_value={
            "num_nodes": 10000,
            "num_channels": 50000,
            "total_capacity": 100000000000
        })
        
        self.get_node_info = AsyncMock(return_value={
            "node": {
                "alias": "mcp_node",
                "pubkey": "mcp_pubkey",
                "color": "#654321",
                "channels": [
                    {
                        "channel_id": "mcp_channel1",
                        "capacity": 2000000,
                        "node1_pub": "mcp_pubkey",
                        "node2_pub": "pubkey2"
                    }
                ]
            }
        })
        
        self.get_channel_info = AsyncMock(return_value={
            "channel": {
                "channel_id": "mcp_channel1",
                "capacity": 2000000,
                "node1_pub": "mcp_pubkey",
                "node2_pub": "pubkey2",
                "last_update": datetime.now().isoformat()
            }
        })

class LNRouterClientMock(AsyncMock):
    """Mock du client LNRouter"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_url = "https://lnrouter.test/api"
        self.api_key = "test_key"
        self.graph_cache_duration = timedelta(hours=12)
        self.last_graph_update = datetime.now()
        
        self.graph = {
            "nodes": [
                {
                    "pub_key": "pubkey1",
                    "alias": "node1",
                    "color": "#123456"
                },
                {
                    "pub_key": "pubkey2",
                    "alias": "node2",
                    "color": "#654321"
                }
            ],
            "channels": [
                {
                    "channel_id": "channel1",
                    "capacity": 1000000,
                    "node1_pub": "pubkey1",
                    "node2_pub": "pubkey2"
                }
            ]
        }
        
        self.get_graph = AsyncMock(return_value=self.graph)
        self.get_network_stats = AsyncMock(return_value={
            "nodes_count": len(self.graph["nodes"]),
            "channels_count": len(self.graph["channels"]),
            "total_capacity": sum(c["capacity"] for c in self.graph["channels"])
        })
        
        self.get_node_info = AsyncMock(return_value=self.graph["nodes"][0])
        self.get_channel_info = AsyncMock(return_value=self.graph["channels"][0]) 