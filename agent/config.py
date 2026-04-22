"""Configuration management for Tenacious Agent."""

import os
from pathlib import Path
from typing import Optional, Literal
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load .env file
load_dotenv()

class OpenRouterConfig(BaseSettings):
    """OpenRouter API configuration."""
    
    api_key: SecretStr = Field(default=SecretStr(""), alias="OPENROUTER_API_KEY")
    base_url: str = Field(default="https://openrouter.ai/api/v1", alias="OPENROUTER_BASE_URL")
    model_dev: str = Field(default="deepseek/deepseek-v3-base:free", alias="OPENROUTER_MODEL_DEV")
    model_eval: str = Field(default="anthropic/claude-3.5-sonnet", alias="OPENROUTER_MODEL_EVAL")
    temperature: float = Field(default=0.1, alias="EVALUATION_TEMPERATURE")
    
    class Config:
        env_file = ".env"
        extra = "ignore"

class HubSpotConfig(BaseSettings):
    """HubSpot CRM configuration."""
    
    api_key: SecretStr = Field(default=SecretStr(""), alias="HUBSPOT_API_KEY")
    app_id: Optional[str] = Field(default=None, alias="HUBSPOT_APP_ID")
    
    class Config:
        env_file = ".env"
        extra = "ignore"

class ResendConfig(BaseSettings):
    """Resend email configuration."""
    
    api_key: SecretStr = Field(default=SecretStr(""), alias="RESEND_API_KEY")
    from_email: str = Field(default="hello@tenacious.com", alias="RESEND_FROM_EMAIL")
    webhook_secret: Optional[str] = Field(default=None, alias="RESEND_WEBHOOK_SECRET")
    
    class Config:
        env_file = ".env"
        extra = "ignore"

class AfricaTalkingConfig(BaseSettings):
    """Africa's Talking SMS configuration."""
    
    username: str = Field(default="sandbox", alias="AFRICASTALKING_USERNAME")
    api_key: SecretStr = Field(default=SecretStr(""), alias="AFRICASTALKING_API_KEY")
    short_code: str = Field(default="12345", alias="AFRICASTALKING_SHORT_CODE")
    
    class Config:
        env_file = ".env"
        extra = "ignore"

class CalComConfig(BaseSettings):
    """Cal.com configuration."""
    
    api_key: SecretStr = Field(default=SecretStr(""), alias="CALCOM_API_KEY")
    event_type_id: int = Field(default=123456, alias="CALCOM_EVENT_TYPE_ID")
    base_url: str = Field(default="http://localhost:3000", alias="CALCOM_BASE_URL")
    
    class Config:
        env_file = ".env"
        extra = "ignore"

class LangfuseConfig(BaseSettings):
    """Langfuse observability configuration."""
    
    public_key: str = Field(default="", alias="LANGFUSE_PUBLIC_KEY")
    secret_key: SecretStr = Field(default=SecretStr(""), alias="LANGFUSE_SECRET_KEY")
    host: str = Field(default="https://cloud.langfuse.com", alias="LANGFUSE_HOST")
    
    class Config:
        env_file = ".env"
        extra = "ignore"

class Settings(BaseSettings):
    """Master settings class."""
    
    # Sub-configs
    openrouter: OpenRouterConfig = Field(default_factory=OpenRouterConfig)
    hubspot: HubSpotConfig = Field(default_factory=HubSpotConfig)
    resend: ResendConfig = Field(default_factory=ResendConfig)
    africastalking: AfricaTalkingConfig = Field(default_factory=AfricaTalkingConfig)
    calcom: CalComConfig = Field(default_factory=CalComConfig)
    langfuse: LangfuseConfig = Field(default_factory=LangfuseConfig)
    
    # Global settings
    send_to_real_prospects: bool = Field(default=False, alias="SEND_TO_REAL_PROSPECTS")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_file: str = Field(default="logs/tenacious.log", alias="LOG_FILE")
    database_url: str = Field(default="sqlite:///./data/tenacious.db", alias="DATABASE_URL")
    
    # Evaluation
    tau2_held_out_seed: int = Field(default=42, alias="TAU2_BENCH_HELD_OUT_SEED")
    
    class Config:
        env_file = ".env"
        extra = "ignore"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return not self.send_to_real_prospects

# Global settings instance
settings = Settings()
