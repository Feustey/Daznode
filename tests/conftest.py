"""Configuration globale pour les tests pytest"""

import pytest
import os
import sys

# Ajouter le répertoire racine au PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importer les mocks pour app.core.config.settings
from tests.mocks import mock_settings, MockConfigModule, MockCoreModule, MockAppModule

# S'assurer que les modules mockés sont dans sys.modules
sys.modules['app'] = MockAppModule
sys.modules['app.core'] = MockCoreModule 
sys.modules['app.core.config'] = MockConfigModule

@pytest.fixture
def mock_env_vars(monkeypatch):
    """Fixture pour mocker les variables d'environnement"""
    monkeypatch.setenv('SECRET_KEY', 'test_secret_key')
    monkeypatch.setenv('NODE_PUBKEY', '02778f4a4eb3a2344b9fd8ee72e7ec5f03f803e5f5273e2e1a2af508')
    monkeypatch.setenv('LND_HOST', '127.0.0.1')
    monkeypatch.setenv('LND_PORT', '10009')
    monkeypatch.setenv('LND_CERT_PATH', '/fake/path/tls.cert')
    monkeypatch.setenv('LND_MACAROON_PATH', '/fake/path/admin.macaroon')
    monkeypatch.setenv('DATABASE_URL', 'sqlite:///:memory:')
    monkeypatch.setenv('ENVIRONMENT', 'test') 