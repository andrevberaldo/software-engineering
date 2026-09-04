from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = (
        "postgresql://novaseguro:novaseguro_dev_pw@localhost:5432/novaseguro"
    )

    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"
    openai_embedding_model: str = "text-embedding-3-small"

    # Deve ser o MESMO segredo usado pelo frontend (proxy.ts) para validar o
    # cookie de sessão — o backend assina o JWT no login e o frontend só
    # confere a assinatura para decidir se libera as páginas protegidas.
    jwt_secret: str = "change-me-in-every-environment"
    jwt_algorithm: str = "HS256"
    jwt_expires_minutes: int = 60 * 24 * 7  # 7 dias

    cookie_name: str = "ns_session"
    cookie_secure: bool = False

    cors_origins: str = "http://localhost:3000"

    # Diretório onde os PDFs enviados ficam guardados para download. Em
    # produção (docker-compose) isso é um volume nomeado; localmente, uma
    # pasta relativa dentro de backend/.
    storage_dir: str = "./data/documentos"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
