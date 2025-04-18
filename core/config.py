from typing import List, Optional, Union
from pydantic import AnyHttpUrl, validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Daznode"
    API_V1_STR: str = "/api/v1"
    
    # SÉCURITÉ
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 jours
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"]

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # MCP API CONFIGURATION
    MCP_API_URL: str = "https://api.mcp.network"
    MCP_API_KEY: Optional[str] = None
    
    # FEUSTEY NODE API
    FEUSTEY_API_URL: Optional[str] = None
    FEUSTEY_API_KEY: Optional[str] = None

    # DATABASE
    DATABASE_URL: Optional[str] = None

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)


settings = Settings() 