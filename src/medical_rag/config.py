import os
import requests
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # NCBI
    ncbi_api_key: Optional[str] = None

    # LLM (Local/Cloud)
    llm_base_url: str = "http://localhost:8080/v1"
    llm_model: str = "auto-detect"

    # Embeddings
    embedding_base_url: str = "http://localhost:8081/v1"
    embedding_model: str = "embeddinggemma-300m"

    # API Key for local (if needed)
    openai_api_key: str = "not-needed"

    def get_actual_llm_model(self) -> str:
        """
        Attempts to fetch the currently loaded model from the LLM server
        if llm_model is set to 'auto-detect'.
        """
        if self.llm_model != "auto-detect":
            return self.llm_model

        try:
            # Standard OpenAI-compatible /v1/models endpoint
            response = requests.get(f"{self.llm_base_url}/models", timeout=5)
            if response.status_code == 200:
                models = response.json()
                # Most local servers return the currently loaded model as the first entry
                if "data" in models and len(models["data"]) > 0:
                    return str(models["data"][0]["id"])
        except Exception:
            pass

        # Fallback if detection fails
        return "default-model"


# Global settings instance
settings = Settings()
