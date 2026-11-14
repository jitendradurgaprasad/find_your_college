import os
from typing import List, Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Find Your Collage"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./find_your_college.db")
    
    # Crawler Security & SSRF Protection
    BLOCKED_IPS: List[str] = [
        "127.0.0.1", "localhost", "0.0.0.0",
        "10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16",
        "169.254.169.254" # Cloud metadata
    ]
    
    # Crawler Engine Limits
    MAX_CRAWL_DEPTH: int = int(os.getenv("MAX_CRAWL_DEPTH", "3"))
    MAX_PAGES_PER_SITE: int = int(os.getenv("MAX_PAGES_PER_SITE", "45"))
    REQUEST_DELAY_SECONDS: float = float(os.getenv("REQUEST_DELAY_SECONDS", "0.5"))
    REQUEST_TIMEOUT_SECONDS: int = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "15"))
    MAX_CONCURRENT_REQUESTS: int = int(os.getenv("MAX_CONCURRENT_REQUESTS", "5"))
    USER_AGENT: str = os.getenv(
        "USER_AGENT",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 (FindYourCollege Educational Intelligence Crawler)"
    )
    
    # Search Provider
    SEARCH_API_KEY: Optional[str] = os.getenv("SEARCH_API_KEY", None)
    SEARCH_PROVIDER: str = os.getenv("SEARCH_PROVIDER", "tavily") # tavily, brave, mock
    
    # AI Assistance (optional)
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY", None)
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY", None)
    
    # Security Secret for administrative tasks
    CRAWLER_API_SECRET: str = os.getenv("CRAWLER_API_SECRET", "super-secret-admin-key")
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000", "https://*"]
    
    class Config:
        case_sensitive = True
        extra = "allow"

settings = Settings()
