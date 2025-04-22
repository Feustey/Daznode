"""Mocks pour les tests"""

from unittest.mock import MagicMock

# Mock des settings
mock_settings = MagicMock()
mock_settings.NODE_PUBKEY = "02778f4a4eb3a2344b9fd8ee72e7ec5f03f803e5f5273e2e1a2af508"
mock_settings.LND_HOST = "127.0.0.1"
mock_settings.LND_PORT = 10009
mock_settings.LND_CERT_PATH = "/fake/path/tls.cert"
mock_settings.LND_MACAROON_PATH = "/fake/path/admin.macaroon"
mock_settings.DATABASE_URL = "sqlite:///:memory:"
mock_settings.ENVIRONMENT = "test"
mock_settings.MCP_API_URL = "https://api.example.com/mcp"
mock_settings.MCP_API_KEY = "fake_api_key"
mock_settings.FEUSTEY_API_URL = "https://api.example.com/feustey"
mock_settings.FEUSTEY_API_KEY = "fake_feustey_api_key"
mock_settings.BACKEND_CORS_ORIGINS = ["http://localhost:3000"]
mock_settings.SECRET_KEY = "test_secret_key"

# Mock des modules
class MockConfigModule:
    settings = mock_settings

class MockCoreModule:
    config = MockConfigModule

class MockAppModule:
    core = MockCoreModule 