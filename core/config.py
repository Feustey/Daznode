from typing import List, Optional, Union
import os
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Daznode"
    API_V1_STR: str = "/api/v1"
    
    # SÉCURITÉ
    SECRET_KEY: str = "developpement_secret_key_remplacer_en_production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 jours
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # SOURCE DE DONNÉES
    # Options: "local", "mcp", "auto"
    DEFAULT_DATA_SOURCE: str = "auto"
    
    # MCP API CONFIGURATION
    MCP_API_URL: str = "https://api.mcp.network"
    MCP_API_KEY: Optional[str] = None
    MCP_API_SECRET: Optional[str] = None
    MCP_NETWORK: Optional[str] = None
    MCP_WEBHOOK_SECRET: Optional[str] = None
    NODE_PUBKEY: Optional[str] = None
    
    # FEUSTEY NODE API
    FEUSTEY_API_URL: Optional[str] = None
    FEUSTEY_API_KEY: Optional[str] = None
    
    # LNROUTER API CONFIGURATION
    LNROUTER_API_URL: str = "https://lnrouter.app/api/v1"
    LNROUTER_API_KEY: Optional[str] = None
    
    # LND NODE CONFIGURATION
    LND_GRPC_HOST: str = "localhost:10009"
    LND_TLS_CERT_PATH: Optional[str] = None
    LND_MACAROON_PATH: Optional[str] = None
    
    # AMBOSS API CONFIGURATION
    AMBOSS_API_URL: str = "https://api.amboss.space/graphql"
    AMBOSS_API_KEY: Optional[str] = None
    
    # MEMPOOL API CONFIGURATION
    MEMPOOL_API_URL: str = "https://mempool.space/api"

    # DATABASE
    DATABASE_URL: Optional[str] = None
    
    # Alby Configuration
    ALBY_PUBLIC_KEY: Optional[str] = None
    ALBY_RELAY_URL: Optional[str] = None
    ALBY_SECRET: Optional[str] = None
    ALBY_LUD16: Optional[str] = None
    ALBY_WEBHOOK_SECRET: Optional[str] = None
    
    # Resend
    RESEND_API_KEY: Optional[str] = None
    
    # Public variables
    NEXT_PUBLIC_ALBY_PUBLIC_KEY: Optional[str] = None
    NEXT_PUBLIC_ALBY_RELAY_URL: Optional[str] = None
    NEXT_PUBLIC_APP_URL: Optional[str] = None
    
    # Supabase
    SUPABASE_API_KEY: Optional[str] = None
    NEXT_PUBLIC_SUPABASE_URL: Optional[str] = None
    NEXT_PUBLIC_SUPABASE_ANON_KEY: Optional[str] = None
    
    # METRICS COLLECTION
    METRICS_COLLECTION_INTERVAL_HOURS: int = 24
    METRICS_HISTORY_DAYS: int = 90

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")


settings = Settings() 