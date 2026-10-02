from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "Swarn Backend"
    tenant_id_header: str = "X-Tenant-ID"
    database_url: str = "sqlite+aiosqlite:///swarn.db"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
