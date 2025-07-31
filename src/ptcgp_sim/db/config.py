import os
from dotenv import load_dotenv
from dataclasses import dataclass, asdict


# Load environment variables from .env file
load_dotenv()

# Update this config for your database
@dataclass
class DatabaseConfig:
    host: str = os.getenv("DB_HOST", "localhost")
    dbname: str = os.getenv("DB_DATABASE", "ptcgp")
    user: str = os.getenv("DB_USERNAME", "postgres")
    password: str = os.getenv("DB_PASSWORD", "password")
    port: int = os.getenv("DB_PORT", 5432)

    def dict(self) -> dict:
        return asdict(self)
