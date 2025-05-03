from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    secret_key: str
    algo: str
    access_token_expire_minutes: int


settings = Settings()