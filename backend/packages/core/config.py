from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "Swarn Backend"
    tenant_id_header: str = "X-Tenant-ID"
    database_url: str = "sqlite+aiosqlite:///swarn.db"
    clerk_secret_key: str | None = None
    clerk_publishable_key: str | None = None
    google_api_key: str | None = None
    strong_model: str | None = None
    cheap_model: str | None = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
