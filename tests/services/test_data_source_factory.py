import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import asyncio
from unittest.mock import call

from services.data_source_factory import DataSourceFactory
from services.local_data_source import LocalDataSource
from services.mcp_data_source import MCPDataSource
from services.health_check_manager import HealthCheckManager


class TestDataSourceFactory:
    
    @pytest.fixture
    def mock_clients(self):
        """Crée les mocks des clients pour les tests"""
        health_manager = MagicMock(spec=HealthCheckManager)
        health_manager.set_clients = MagicMock()
        health_manager.check_all_sources = AsyncMock()
        health_manager.start_background_checks = AsyncMock()
        health_manager.stop_background_checks = AsyncMock()
        health_manager.is_source_available = MagicMock(return_value=True)
        health_manager.get_all_statuses = MagicMock(return_value={
            "timestamp": "2024-03-21T10:00:00Z",
            "sources": {
                "lnd": {"status": "ok"},
                "mcp": {"status": "ok"},
                "lnrouter": {"status": "ok"}
            },
            "global_status": "ok"
        })
        
        return {
            "lnd_client": MagicMock(),
            "mcp_service": MagicMock(),
            "lnrouter_client": MagicMock(),
            "health_manager": health_manager
        }
    
    @pytest.fixture
    async def setup_factory(self, mock_clients):
        """Configure la factory pour les tests"""
        # Réinitialiser l'état de la factory
        DataSourceFactory._sources = {}
        DataSourceFactory._lnd_client = None
        DataSourceFactory._lnrouter_client = None
        DataSourceFactory._mcp_service = None
        DataSourceFactory._health_manager = None
        DataSourceFactory._initialized = False
        
        # Réinitialiser les mocks
        for client in mock_clients.values():
            if hasattr(client, 'reset_mock'):
                client.reset_mock()
            if isinstance(client, MagicMock):
                client.side_effect = None
                client.return_value = None
        
        # Réinitialiser le health manager spécifiquement
        mock_clients["health_manager"].is_source_available.return_value = True
        
        yield
        
        # Cleanup après chaque test
        await DataSourceFactory.shutdown()
    
    @pytest.mark.asyncio
    async def test_initialize(self, mock_clients, setup_factory):
        """Test de l'initialisation de la factory"""
        with patch(
            'services.data_source_factory.LNDClient', 
            return_value=mock_clients["lnd_client"]
        ), patch(
            'services.data_source_factory.MCPService', 
            return_value=mock_clients["mcp_service"]
        ), patch(
            'services.data_source_factory.LNRouterClient', 
            return_value=mock_clients["lnrouter_client"]
        ), patch(
            'services.data_source_factory.HealthCheckManager', 
            return_value=mock_clients["health_manager"]
        ):
            
            await DataSourceFactory.initialize()
            
            assert DataSourceFactory._initialized
            assert DataSourceFactory._lnd_client == mock_clients["lnd_client"]
            assert DataSourceFactory._mcp_service == mock_clients["mcp_service"]
            assert DataSourceFactory._lnrouter_client == mock_clients["lnrouter_client"]
            assert DataSourceFactory._health_manager == mock_clients["health_manager"]
            
            # Vérifier que le health manager a été configuré correctement
            mock_clients["health_manager"].set_clients.assert_called_once()
            mock_clients["health_manager"].check_all_sources.assert_called_once()
            mock_clients["health_manager"].start_background_checks.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_initialize_idempotent(self, mock_clients, setup_factory):
        """Test que l'initialisation est idempotente"""
        with patch(
            'services.data_source_factory.LNDClient', 
            return_value=mock_clients["lnd_client"]
        ), patch(
            'services.data_source_factory.MCPService', 
            return_value=mock_clients["mcp_service"]
        ), patch(
            'services.data_source_factory.LNRouterClient', 
            return_value=mock_clients["lnrouter_client"]
        ), patch(
            'services.data_source_factory.HealthCheckManager', 
            return_value=mock_clients["health_manager"]
        ):
            
            await DataSourceFactory.initialize()
            initial_health_manager = DataSourceFactory._health_manager
            
            # Deuxième initialisation
            await DataSourceFactory.initialize()
            
            assert DataSourceFactory._health_manager == initial_health_manager
            # Vérifier que les méthodes n'ont été appelées qu'une fois
            mock_clients["health_manager"].set_clients.assert_called_once()
            mock_clients["health_manager"].check_all_sources.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_shutdown(self, mock_clients, setup_factory):
        """Test de l'arrêt propre de la factory"""
        with patch(
            'services.data_source_factory.LNDClient', 
            return_value=mock_clients["lnd_client"]
        ), patch(
            'services.data_source_factory.MCPService', 
            return_value=mock_clients["mcp_service"]
        ), patch(
            'services.data_source_factory.LNRouterClient', 
            return_value=mock_clients["lnrouter_client"]
        ), patch(
            'services.data_source_factory.HealthCheckManager', 
            return_value=mock_clients["health_manager"]
        ):
            
            await DataSourceFactory.initialize()
            await DataSourceFactory.shutdown()
            
            assert not DataSourceFactory._initialized
            mock_clients["health_manager"].stop_background_checks.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_data_source_auto_with_health_manager(
        self, 
        mock_clients, 
        setup_factory
    ):
        """Test de la sélection automatique avec le health manager"""
        with patch(
            'services.data_source_factory.LNDClient', 
            return_value=mock_clients["lnd_client"]
        ), patch(
            'services.data_source_factory.MCPService', 
            return_value=mock_clients["mcp_service"]
        ), patch(
            'services.data_source_factory.LNRouterClient', 
            return_value=mock_clients["lnrouter_client"]
        ), patch(
            'services.data_source_factory.HealthCheckManager', 
            return_value=mock_clients["health_manager"]
        ), patch(
            'core.config.settings.MCP_API_KEY', 
            'test_key'
        ), patch(
            'core.config.settings.MCP_API_URL', 
            'https://api.test'
        ):
            
            await DataSourceFactory.initialize()
            
            # Configurer le health manager pour indiquer que MCP est disponible
            mock_clients["health_manager"].is_source_available.return_value = True
            
            source = DataSourceFactory.get_data_source("auto")
            assert isinstance(source, MCPDataSource)
            mock_clients["health_manager"].is_source_available.assert_called_with("mcp")
    
    @pytest.mark.asyncio
    async def test_get_data_source_auto_fallback_with_health_manager(
        self, 
        mock_clients, 
        setup_factory
    ):
        """Test du fallback quand MCP n'est pas disponible selon le health manager"""
        with patch(
            'services.data_source_factory.LNDClient', 
            return_value=mock_clients["lnd_client"]
        ), patch(
            'services.data_source_factory.MCPService', 
            return_value=mock_clients["mcp_service"]
        ), patch(
            'services.data_source_factory.LNRouterClient', 
            return_value=mock_clients["lnrouter_client"]
        ), patch(
            'services.data_source_factory.HealthCheckManager', 
            return_value=mock_clients["health_manager"]
        ), patch(
            'core.config.settings.MCP_API_KEY', 
            'test_key'
        ), patch(
            'core.config.settings.MCP_API_URL', 
            'https://api.test'
        ):
            
            await DataSourceFactory.initialize()
            
            # Configurer le health manager pour indiquer que MCP n'est pas disponible
            def is_source_available(source_type):
                return source_type == "local"
            mock_clients["health_manager"].is_source_available.side_effect = is_source_available
            
            source = DataSourceFactory.get_data_source("auto")
            assert isinstance(source, LocalDataSource)
            
            # Vérifier que le health manager a été consulté pour les deux sources
            mock_clients["health_manager"].is_source_available.assert_any_call("mcp")
            mock_clients["health_manager"].is_source_available.assert_any_call("local")
    
    @pytest.mark.asyncio
    async def test_get_data_source_caching(self, setup_factory, mock_clients):
        """Vérifie que les sources de données sont correctement mises en cache"""
        with patch(
            'services.data_source_factory.LNDClient', 
            return_value=mock_clients["lnd_client"]
        ), patch(
            'services.data_source_factory.MCPService', 
            return_value=mock_clients["mcp_service"]
        ), patch(
            'services.data_source_factory.LNRouterClient', 
            return_value=mock_clients["lnrouter_client"]
        ), patch(
            'services.data_source_factory.HealthCheckManager', 
            return_value=mock_clients["health_manager"]
        ):
            
            # Initialiser la factory
            await DataSourceFactory.initialize()
            
            # Premier appel pour obtenir une source
            source1 = DataSourceFactory.get_data_source()
            assert source1 is not None
            
            # Deuxième appel - devrait retourner la même instance
            source2 = DataSourceFactory.get_data_source()
            assert source2 is not None
            assert source1 is source2  # Vérifie que c'est la même instance
            
            # Vérifie que le health manager a été appelé pour chaque appel à get_data_source
            assert mock_clients["health_manager"].is_source_available.call_count == 2
            mock_clients["health_manager"].is_source_available.assert_has_calls([
                call("local"),
                call("local")
            ])
    
    @pytest.mark.asyncio
    async def test_get_data_source_auto_without_health_manager(
        self, 
        mock_clients, 
        setup_factory
    ):
        """Test de la sélection automatique sans health manager initialisé"""
        with patch(
            'services.data_source_factory.LNDClient', 
            return_value=mock_clients["lnd_client"]
        ), patch(
            'services.data_source_factory.MCPService', 
            return_value=mock_clients["mcp_service"]
        ), patch(
            'services.data_source_factory.LNRouterClient', 
            return_value=mock_clients["lnrouter_client"]
        ), patch(
            'core.config.settings.MCP_API_KEY', 
            'test_key'
        ), patch(
            'core.config.settings.MCP_API_URL', 
            'https://api.test'
        ):
            
            # Configurer le mock MCP pour simuler une réponse réussie
            mock_clients["mcp_service"].get_network_stats = MagicMock(
                return_value={"success": True}
            )
            
            # Réinitialiser l'état de la factory
            DataSourceFactory._health_manager = None
            DataSourceFactory._initialized = False
            
            source = DataSourceFactory.get_data_source("auto")
            assert isinstance(source, MCPDataSource)
            mock_clients["mcp_service"].get_network_stats.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_data_source_auto_without_health_manager_mcp_fails(
        self, 
        mock_clients, 
        setup_factory
    ):
        """Test du fallback quand MCP échoue sans health manager"""
        with patch(
            'services.data_source_factory.LNDClient', 
            return_value=mock_clients["lnd_client"]
        ), patch(
            'services.data_source_factory.MCPService', 
            return_value=mock_clients["mcp_service"]
        ), patch(
            'services.data_source_factory.LNRouterClient', 
            return_value=mock_clients["lnrouter_client"]
        ), patch(
            'core.config.settings.MCP_API_KEY', 
            'test_key'
        ), patch(
            'core.config.settings.MCP_API_URL', 
            'https://api.test'
        ):
            
            # Configurer le mock MCP pour simuler une erreur
            mock_clients["mcp_service"].get_network_stats = AsyncMock(
                side_effect=Exception("MCP error")
            )
            
            source = DataSourceFactory.get_data_source("auto")
            assert isinstance(source, LocalDataSource)
            mock_clients["mcp_service"].get_network_stats.assert_called_once() 