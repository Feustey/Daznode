import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, MagicMock
from datetime import datetime

from api.main import app
from services.health_check_manager import HealthCheckManager

client = TestClient(app)

class TestHealthEndpoint:
    
    @pytest.fixture
    def mock_health_manager(self):
        """Crée un mock du HealthCheckManager"""
        mock = MagicMock(spec=HealthCheckManager)
        mock.check_all_sources = AsyncMock()
        mock.get_all_statuses.return_value = {
            "timestamp": datetime.now().isoformat(),
            "sources": {
                "lnd": {
                    "status": "ok",
                    "last_check": datetime.now().isoformat(),
                    "error": None,
                    "details": {
                        "alias": "test_node",
                        "pubkey": "test_pubkey",
                        "block_height": 700000,
                        "synced": True,
                        "response_time_ms": 45.2
                    }
                },
                "mcp": {
                    "status": "ok",
                    "last_check": datetime.now().isoformat(),
                    "error": None,
                    "details": {
                        "api_url": "https://api.mcp.test",
                        "has_api_key": True,
                        "network_stats": {
                            "nodes_count": 10000,
                            "channels_count": 50000
                        },
                        "response_time_ms": 120.5
                    }
                },
                "lnrouter": {
                    "status": "ok",
                    "last_check": datetime.now().isoformat(),
                    "error": None,
                    "details": {
                        "api_url": "https://lnrouter.test/api",
                        "has_api_key": True,
                        "cache_status": "valid",
                        "cache_details": {
                            "nodes_count": 1000,
                            "channels_count": 5000,
                            "cache_age_hours": 2.5,
                            "last_update": datetime.now().isoformat()
                        }
                    }
                }
            },
            "global_status": "ok"
        }
        return mock
    
    @pytest.mark.asyncio
    async def test_get_health_success(self, mock_health_manager):
        """Test de la récupération réussie de l'état de santé"""
        with patch('api.health.DataSourceFactory.get_health_manager', return_value=mock_health_manager):
            response = client.get("/api/v1/system/health")
            
            assert response.status_code == 200
            assert response.json()["global_status"] == "ok"
            assert "sources" in response.json()
            assert "lnd" in response.json()["sources"]
            assert "mcp" in response.json()["sources"]
            assert "lnrouter" in response.json()["sources"]
            
            # Vérifier que check_all_sources a été appelé
            mock_health_manager.check_all_sources.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_health_error(self, mock_health_manager):
        """Test de la gestion des erreurs lors de la récupération de l'état de santé"""
        mock_health_manager.check_all_sources.side_effect = Exception("Test error")
        
        with patch('api.health.DataSourceFactory.get_health_manager', return_value=mock_health_manager):
            response = client.get("/api/v1/system/health")
            
            assert response.status_code == 200  # L'API retourne toujours 200 avec un message d'erreur
            assert "error" in response.json()
            assert "Test error" in response.json()["details"] 