import os
import secrets
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GATE_BLOCK_THRESHOLD = 0.85
GATE_SUSPICIOUS_THRESHOLD = 0.45
HMAC_SECRET = os.getenv("HMAC_SECRET", secrets.token_hex(32))
PORT = int(os.getenv("PORT", "8000"))
DEMO_MODE = not bool(OPENAI_API_KEY)
