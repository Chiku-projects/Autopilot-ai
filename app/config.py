from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    log_level: str = "INFO"
    groq_api_key: str = ""
    groq_model: str = "openai/gpt-oss-120b"
    ai_provider: str = "anthropic"  # "anthropic" or "groq"
    

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()