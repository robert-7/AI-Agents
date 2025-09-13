#!/usr/bin/env python3
import os

import dotenv
from agents import Agent
from agents import Runner

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

# Validate once at import time; litellm will read OPENAI_API_KEY from the env.
OPENAI_API_KEY = _get_required_env("OPENAI_API_KEY")

# -----------------------------------------------------------------------------

def haiku_agent() -> str:
    '''And agent that writes a a haiku about recursion.'''
    agent = Agent(name="Assistant", instructions="You are a helpful assistant")
    result = Runner.run_sync(agent, "Write a haiku about recursion in programming.")
    return result.final_output

if __name__ == "__main__":
    print(haiku_agent())
