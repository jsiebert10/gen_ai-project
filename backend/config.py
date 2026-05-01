from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "International Student AI Consultant"
    debug: bool = False

    # LLM Provider — "openai" or "gemini"
    llm_provider: str = "openai"

    # OpenAI
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"

    # Gemini
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-fast"

    # Data source
    data_source: str = "llm"  # "llm", "mockup", or "scraping"

    # CORS
    allowed_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
