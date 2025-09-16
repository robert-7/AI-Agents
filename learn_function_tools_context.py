#!/usr/bin/env python3
import asyncio # needed for async calls

from agents import Agent
from agents import function_tool
from agents import Runner

import env

OPENAI_API_KEY = env.get_required_env("OPENAI_API_KEY")

@function_tool
def multiply(x: float, y: float) -> float:
    """Multiplies `x` and `y` to provide a precise answer."""
    return x*y

math_agent = Agent(
    name="Triage Agent",
    instructions=(
        "You're a helpful assistant, remember to always "
        "use the provided tools whenever possible. Do not "
        "rely on your own knowledge too much and instead "
        "use your tools to help you answer queries."
    ),
    model="gpt-4o-mini",
    tools=[multiply]
)

async def compute_multiplication():
    result = await Runner.run(starting_agent=math_agent, input="What is 7.814 multiplied by 103.892?")
    print(result.final_output+'\n')
    result = await Runner.run(starting_agent=math_agent, input=result.to_input_list()+[{"role": "user", "content": "What is the previous number times 14.23?"}])
    print(result.final_output)

if __name__ == "__main__":
    asyncio.run(compute_multiplication())
