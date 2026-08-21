"""集中管理运行环境配置，支持用环境变量覆盖默认值。"""

from dataclasses import dataclass
import os

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    base_url: str = os.getenv("BASE_URL", "https://restful-booker.herokuapp.com")
    timeout: float = float(os.getenv("API_TIMEOUT", "10"))
    username: str = os.getenv("BOOKER_USERNAME", "admin")
    password: str = os.getenv("BOOKER_PASSWORD", "password123")


settings = Settings()
