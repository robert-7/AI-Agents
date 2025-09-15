#!/usr/bin/env python3
from agents import Agent
from agents import Runner

import env

OPENAI_API_KEY = env._get_required_env("OPENAI_API_KEY")

def haiku_agent():
    '''An agent that writes a a haiku about recursion.'''
    agent = Agent(name="Assistant", instructions="You are a helpful assistant")
    result = Runner.run_sync(agent, "Write a haiku about recursion in programming.")
    print(result.final_output)

if __name__ == "__main__":
    haiku_agent()
