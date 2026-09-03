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

    # Deve ser o MESMO segredo usado pelo BFF para assinar o cookie de sessão,
    # já que o backend confia no token repassado pelo BFF em vez de refazer o
    # login por conta própria.
    jwt_secret: str = "change-me-in-every-environment"
    jwt_algorithm: str = "HS256"

    cors_origins: str = "http://localhost:4000"

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
