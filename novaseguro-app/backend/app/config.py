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
    # Domínio do cookie de sessão. None = host-only (funciona quando
    # frontend e backend estão no mesmo host, ignorando porta — o caso de
    # um único tenant). Para multi-tenant por subdomínio, onde o frontend
    # vive em <slug>.dominio.com mas a API fica num host fixo (ex.:
    # api.dominio.com), o cookie precisa de um domínio com o ponto à frente
    # (ex.: ".dominio.com" ou ".localhost" em dev) para ficar visível em
    # todos os subdomínios.
    cookie_domain: str | None = None

    cors_origins: str = "http://localhost:3000"
    # Regex de origens liberadas, para SaaS multi-tenant por subdomínio
    # (ex.: r"https://.*\.minhaempresa\.com"). Somado (OR) a cors_origins.
    cors_origin_regex: str | None = None

    # Diretório onde os PDFs e logos enviados ficam guardados. Em produção
    # (docker-compose) isso é um volume nomeado; localmente, uma pasta
    # relativa dentro de backend/.
    storage_dir: str = "./data/documentos"

    # Slug de tenant usado quando a requisição não indica subdomínio algum
    # (localhost, IP, ou host sem ponto) — mantém o fluxo de desenvolvimento
    # local funcionando sem exigir configuração de DNS/hosts.
    default_tenant_slug: str = "novaseguro"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
