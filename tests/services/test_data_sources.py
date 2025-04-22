import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from datetime import datetime

from services.data_source_interface import DataSourceInterface
from services.local_data_source import LocalDataSource
from services.mcp_data_source import MCPDataSource
from tests.mocks.backend_clients import LNDClientMock, MCPServiceMock, LNRouterClientMock

class TestLocalDataSource:
    
    @pytest.fixture
    def mock_clients(self):
        """Crée les mocks des clients pour LocalDataSource"""
        return {
            "lnd_client": LNDClientMock(),
            "lnrouter_client": LNRouterClientMock()
        }
    
    @pytest.fixture
    def local_data_source(self, mock_clients):
        """Crée une instance de LocalDataSource avec les mocks"""
        return LocalDataSource(
            lnd_client=mock_clients["lnd_client"],
            lnrouter_client=mock_clients["lnrouter_client"]
        )
    
    @pytest.mark.asyncio
    async def test_get_node_info_success(self, local_data_source, mock_clients):
        """Test de la récupération réussie des informations d'un nœud"""
        result = await local_data_source.get_node_info("test_pubkey")
        
        # Vérifier que les méthodes appropriées ont été appelées
        mock_clients["lnd_client"].get_node_info.assert_called_once()
        
        # Vérifier le format de la réponse
        assert "node" in result
        assert "alias" in result["node"]
        assert "pubkey" in result["node"]
        assert "color" in result["node"]
    
    @pytest.mark.asyncio
    async def test_get_node_info_fallback(self, local_data_source, mock_clients):
        """Test du fallback sur LNRouter quand LND échoue"""
        # Faire échouer la requête LND
        mock_clients["lnd_client"].get_node_info.side_effect = Exception("LND error")
        
        # Configurer la réponse de LNRouter
        mock_clients["lnrouter_client"].get_node_info.return_value = {
            "pub_key": "test_pubkey",
            "alias": "test_node",
            "color": "#000000",
            "last_update": 0
        }
        
        result = await local_data_source.get_node_info("test_pubkey")
        
        # Vérifier que LNRouter a été appelé
        mock_clients["lnrouter_client"].get_node_info.assert_called_once_with("test_pubkey")
        
        # Vérifier le format de la réponse
        assert "node" in result
        assert result["node"]["pubkey"] == "test_pubkey"  # Vérifier les données de LNRouter
    
    @pytest.mark.asyncio
    async def test_get_channel_info_success(self, local_data_source, mock_clients):
        """Test de la récupération réussie des informations d'un canal"""
        result = await local_data_source.get_channel_info("channel1")
        
        # Vérifier que les méthodes appropriées ont été appelées
        mock_clients["lnd_client"].list_channels.assert_called_once()
        
        # Vérifier le format de la réponse
        assert "channel" in result
        assert "channel_id" in result["channel"]
        assert "capacity" in result["channel"]
    
    @pytest.mark.asyncio
    async def test_get_network_stats_success(self, local_data_source, mock_clients):
        """Test de la récupération réussie des statistiques réseau"""
        result = await local_data_source.get_network_stats()
        
        # Vérifier que les méthodes appropriées ont été appelées
        mock_clients["lnd_client"].get_node_info.assert_called_once()
        mock_clients["lnrouter_client"].analyze_network_topology.assert_called_once()
        
        # Vérifier le format de la réponse
        assert "node_stats" in result
        assert "network_stats" in result
        assert "source" in result
    
    @pytest.mark.asyncio
    async def test_get_node_info_both_fail(self, local_data_source, mock_clients):
        """Test du comportement quand LND et LNRouter échouent"""
        # Faire échouer les deux sources
        mock_clients["lnd_client"].get_node_info.side_effect = Exception("LND error")
        mock_clients["lnrouter_client"].get_node_info.side_effect = Exception("LNRouter error")
        
        result = await local_data_source.get_node_info("test_pubkey")
        assert result is None
    
    @pytest.mark.asyncio
    async def test_get_channel_info_not_found(self, local_data_source, mock_clients):
        """Test du comportement quand le canal n'est pas trouvé"""
        # Simuler un canal non trouvé
        mock_clients["lnd_client"].list_channels.return_value = []
        mock_clients["lnrouter_client"].get_channel_info.side_effect = Exception("Canal non trouvé")
        
        result = await local_data_source.get_channel_info("unknown_channel")
        assert result is None
    
    @pytest.mark.asyncio
    async def test_get_network_stats_lnrouter_fail(self, local_data_source, mock_clients):
        """Test du comportement quand LNRouter échoue pour les stats réseau"""
        mock_clients["lnrouter_client"].analyze_network_topology.side_effect = Exception("LNRouter error")
        
        result = await local_data_source.get_network_stats()
        assert "error" in result
        assert "LNRouter error" in result["error"]

class TestMCPDataSource:
    
    @pytest.fixture
    def mock_service(self):
        """Crée le mock du service MCP"""
        return MCPServiceMock()
    
    @pytest.fixture
    def mcp_data_source(self, mock_service):
        """Crée une instance de MCPDataSource avec le mock"""
        return MCPDataSource(mcp_service=mock_service)
    
    @pytest.mark.asyncio
    async def test_get_node_info_success(self, mcp_data_source, mock_service):
        """Test de la récupération réussie des informations d'un nœud via MCP"""
        result = await mcp_data_source.get_node_info("mcp_pubkey")
        
        # Vérifier que la méthode appropriée a été appelée
        mock_service.get_node_info.assert_called_once_with("mcp_pubkey")
        
        # Vérifier le format de la réponse
        assert "node" in result
        assert result["node"]["pubkey"] == "mcp_pubkey"
        assert "channels" in result["node"]
    
    @pytest.mark.asyncio
    async def test_get_node_info_error(self, mcp_data_source, mock_service):
        """Test de la gestion des erreurs lors de la récupération des informations d'un nœud"""
        mock_service.get_node_info.side_effect = Exception("MCP error")
        
        with pytest.raises(Exception) as exc_info:
            await mcp_data_source.get_node_info("mcp_pubkey")
        
        assert "MCP error" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_get_channel_info_success(self, mcp_data_source, mock_service):
        """Test de la récupération réussie des informations d'un canal via MCP"""
        result = await mcp_data_source.get_channel_info("mcp_channel1")
        
        # Vérifier que la méthode appropriée a été appelée
        mock_service.get_channel_info.assert_called_once_with("mcp_channel1")
        
        # Vérifier le format de la réponse
        assert "channel" in result
        assert result["channel"]["channel_id"] == "mcp_channel1"
        assert "last_update" in result["channel"]
    
    @pytest.mark.asyncio
    async def test_get_network_stats_success(self, mcp_data_source, mock_service):
        """Test de la récupération réussie des statistiques réseau via MCP"""
        result = await mcp_data_source.get_network_stats()
        
        # Vérifier que la méthode appropriée a été appelée
        mock_service.get_network_stats.assert_called_once()
        
        # Vérifier le format de la réponse
        assert "num_nodes" in result
        assert "num_channels" in result
        assert "total_capacity" in result
    
    @pytest.mark.asyncio
    async def test_get_node_info_not_found(self, mcp_data_source, mock_service):
        """Test du comportement quand le nœud n'est pas trouvé via MCP"""
        mock_service.get_node_info.side_effect = Exception("Nœud non trouvé")
        
        with pytest.raises(Exception) as exc_info:
            await mcp_data_source.get_node_info("unknown_pubkey")
        
        assert "Nœud non trouvé" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_get_channel_info_not_found(self, mcp_data_source, mock_service):
        """Test du comportement quand le canal n'est pas trouvé via MCP"""
        mock_service.get_channel_info.side_effect = Exception("Canal non trouvé")
        
        with pytest.raises(Exception) as exc_info:
            await mcp_data_source.get_channel_info("unknown_channel")
        
        assert "Canal non trouvé" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_get_network_stats_api_error(self, mcp_data_source, mock_service):
        """Test du comportement en cas d'erreur API pour les stats réseau"""
        mock_service.get_network_stats.side_effect = Exception("Erreur API MCP")
        
        with pytest.raises(Exception) as exc_info:
            await mcp_data_source.get_network_stats()
        
        assert "Erreur API MCP" in str(exc_info.value)

class TestDataSourceFactory:
    
    @pytest.fixture
    def mock_clients(self):
        """Crée les mocks des clients pour les tests de la factory"""
        return {
            "lnd_client": LNDClientMock(),
            "mcp_service": MCPServiceMock(),
            "lnrouter_client": LNRouterClientMock()
        }
    
    @pytest.mark.asyncio
    async def test_get_data_source_local(self, mock_clients):
        """Test de la création d'une source de données locale"""
        with patch('services.data_source_factory.LNDClient', return_value=mock_clients["lnd_client"]), \
             patch('services.data_source_factory.LNRouterClient', return_value=mock_clients["lnrouter_client"]):
            
            from services.data_source_factory import DataSourceFactory
            source = DataSourceFactory.get_data_source("local")
            
            assert isinstance(source, LocalDataSource)
            assert source.lnd_client == mock_clients["lnd_client"]
            assert source.lnrouter_client == mock_clients["lnrouter_client"]
    
    @pytest.mark.asyncio
    async def test_get_data_source_mcp(self, mock_clients):
        """Test de la création d'une source de données MCP"""
        with patch('services.data_source_factory.MCPService', return_value=mock_clients["mcp_service"]):
            
            from services.data_source_factory import DataSourceFactory
            source = DataSourceFactory.get_data_source("mcp")
            
            assert isinstance(source, MCPDataSource)
            assert source.mcp_service == mock_clients["mcp_service"]
    
    @pytest.mark.asyncio
    async def test_get_data_source_auto(self, mock_clients):
        """Test de la sélection automatique de la source de données"""
        with patch('services.data_source_factory.LNDClient', return_value=mock_clients["lnd_client"]), \
             patch('services.data_source_factory.MCPService', return_value=mock_clients["mcp_service"]), \
             patch('services.data_source_factory.LNRouterClient', return_value=mock_clients["lnrouter_client"]), \
             patch('core.config.settings.MCP_API_KEY', 'test_key'), \
             patch('core.config.settings.MCP_API_URL', 'https://api.test'), \
             patch('services.data_source_factory.asyncio.get_event_loop') as mock_loop:
            
            # Configurer le mock pour get_network_stats
            mock_clients["mcp_service"].get_network_stats = AsyncMock()
            mock_clients["mcp_service"].get_network_stats.return_value = {"success": True}
            
            # Configurer le mock pour run_until_complete
            mock_loop.return_value = MagicMock()
            mock_loop.return_value.run_until_complete = lambda x: None
            
            from services.data_source_factory import DataSourceFactory
            source = DataSourceFactory.get_data_source("auto")
            
            # En mode auto avec MCP configuré, devrait choisir MCP
            assert isinstance(source, MCPDataSource)
            assert source.mcp_service == mock_clients["mcp_service"]
    
    @pytest.mark.asyncio
    async def test_get_data_source_auto_fallback(self, mock_clients):
        """Test du fallback automatique quand MCP n'est pas disponible"""
        with patch('services.data_source_factory.LNDClient', return_value=mock_clients["lnd_client"]), \
             patch('services.data_source_factory.MCPService', return_value=mock_clients["mcp_service"]), \
             patch('services.data_source_factory.LNRouterClient', return_value=mock_clients["lnrouter_client"]), \
             patch('core.config.settings.MCP_API_KEY', None), \
             patch('core.config.settings.MCP_API_URL', None):
            
            from services.data_source_factory import DataSourceFactory
            source = DataSourceFactory.get_data_source("auto")
            
            # En mode auto sans MCP configuré, devrait choisir local
            assert isinstance(source, LocalDataSource)
    
    @pytest.mark.asyncio
    async def test_get_data_source_invalid_type(self, mock_clients):
        """Test du comportement avec un type de source invalide"""
        with patch('services.data_source_factory.LNDClient', return_value=mock_clients["lnd_client"]), \
             patch('services.data_source_factory.LNRouterClient', return_value=mock_clients["lnrouter_client"]):
            
            from services.data_source_factory import DataSourceFactory
            source = DataSourceFactory.get_data_source("invalid_type")
            
            # Devrait fallback sur local
            assert isinstance(source, LocalDataSource)
    
    @pytest.mark.asyncio
    async def test_get_data_source_auto_all_fail(self, mock_clients):
        """Test du comportement quand toutes les sources échouent en mode auto"""
        with patch('services.data_source_factory.LNDClient', return_value=mock_clients["lnd_client"]), \
             patch('services.data_source_factory.MCPService', return_value=mock_clients["mcp_service"]), \
             patch('services.data_source_factory.LNRouterClient', return_value=mock_clients["lnrouter_client"]), \
             patch('core.config.settings.MCP_API_KEY', 'test_key'), \
             patch('core.config.settings.MCP_API_URL', 'https://api.test'), \
             patch('services.data_source_factory.asyncio.get_event_loop') as mock_loop:
            
            # Faire échouer MCP
            mock_clients["mcp_service"].get_network_stats = AsyncMock(side_effect=Exception("MCP error"))
            
            # Configurer le mock pour run_until_complete
            mock_loop.return_value = MagicMock()
            mock_loop.return_value.run_until_complete = lambda x: None
            
            from services.data_source_factory import DataSourceFactory
            # Réinitialiser le cache des sources
            DataSourceFactory._sources = {}
            DataSourceFactory._lnd_client = mock_clients["lnd_client"]
            DataSourceFactory._lnrouter_client = mock_clients["lnrouter_client"]
            
            source = DataSourceFactory.get_data_source("auto")
            
            # Devrait fallback sur local
            assert isinstance(source, LocalDataSource)
            assert source.lnd_client == mock_clients["lnd_client"]
            assert source.lnrouter_client == mock_clients["lnrouter_client"]
    
    @pytest.mark.asyncio
    async def test_get_data_source_auto_mcp_unavailable(self, mock_clients):
        """Test du comportement quand MCP est configuré mais indisponible"""
        with patch('services.data_source_factory.LNDClient', return_value=mock_clients["lnd_client"]), \
             patch('services.data_source_factory.MCPService', return_value=mock_clients["mcp_service"]), \
             patch('services.data_source_factory.LNRouterClient', return_value=mock_clients["lnrouter_client"]), \
             patch('core.config.settings.MCP_API_KEY', 'test_key'), \
             patch('core.config.settings.MCP_API_URL', 'https://api.test'), \
             patch('services.data_source_factory.asyncio.get_event_loop') as mock_loop:
            
            # Simuler MCP indisponible
            mock_clients["mcp_service"].get_network_stats = AsyncMock(side_effect=Exception("Service indisponible"))
            
            # Configurer le mock pour run_until_complete
            mock_loop.return_value = MagicMock()
            mock_loop.return_value.run_until_complete = lambda x: None
            
            from services.data_source_factory import DataSourceFactory
            # Réinitialiser le cache des sources
            DataSourceFactory._sources = {}
            DataSourceFactory._lnd_client = mock_clients["lnd_client"]
            DataSourceFactory._lnrouter_client = mock_clients["lnrouter_client"]
            
            source = DataSourceFactory.get_data_source("auto")
            
            # Devrait fallback sur local
            assert isinstance(source, LocalDataSource)
            assert source.lnd_client == mock_clients["lnd_client"]
            assert source.lnrouter_client == mock_clients["lnrouter_client"] 