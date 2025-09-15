import os

import dotenv

# --- Load & validate secrets -------------------------------------------------
# Load variables from the nearest .env (without overwriting existing real env vars)
dotenv.load_dotenv(dotenv_path=dotenv.find_dotenv(usecwd=True), override=False)

def _get_required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(
            f"Missing required environment variable: {name}. "
            "Create a .env file in your project root with this key, or set it in your shell."
        )
    return value
