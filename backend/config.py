from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "International Student AI Consultant"
    debug: bool = False

    # LLM
    env_name: str = ""
    gemini_api_key: str = ""
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    llm_model: str = "gpt-4o"

    # CORS
    allowed_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
