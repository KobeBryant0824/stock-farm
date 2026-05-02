from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # 本地开发默认 SQLite，Docker 环境通过环境变量覆盖为 PostgreSQL
    database_url: str = "sqlite:///./stockfarm.db"
    redis_url: str = "redis://localhost:6379/0"
    use_redis: bool = False  # 本地开发禁用 Redis，用内存字典代替
    quote_cache_ttl: int = 300       # 5 minutes
    stock_list_cache_ttl: int = 86400  # 1 day

    class Config:
        env_file = ".env"


settings = Settings()
