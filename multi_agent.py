#!/usr/bin/env python3
import asyncio # needed for async calls
from datetime import datetime

import linkup
import requests
from agents import Agent
from agents import function_tool
from agents import Runner

import env

LINKUP_API_KEY = env.get_required_env("LINKUP_API_KEY")
OPENAI_API_KEY = env.get_required_env("OPENAI_API_KEY")

linkup_client = linkup.LinkupClient()

@function_tool
def get_current_date():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@function_tool
async def search_web(query: str) -> str:
    '''An agent that writes a a haiku about recursion.'''
    response = await linkup_client.async_search(
        query=query,
        depth="standard",
        output_type="searchResults"
    )

    answer = f"Search results for '{query}' on {get_current_date()}\n\n"
    relevant_results = response.results[:3]
    for result_i in range(len(relevant_results)):
        result = relevant_results[result_i]
        answer += f"#{result_i} - result.name={result.name}\nresult.url={result.url}\nresult.content={result.content}\n\n"

    return answer

@function_tool
async def search_internal_docs(query: str) -> str:
    res = requests.get(
        "https://raw.githubusercontent.com/aurelio-labs/agents-sdk-course/refs/heads/main/assets/skynet-fy25-q1.md"
    )
    skynet_docs = res.text
    return skynet_docs

@function_tool
def execute_code(code: str) -> str:
    """Execute Python code and return the output. The output must be assigned to a variable called `output`."""
    try:
        namespace = {}
        exec(code, namespace)
        return namespace['result']
    except Exception as e:
        return f"Error executing code: {e}"

web_search_agent = Agent(
    name="Web Search Agent",
    model="gpt-4.1-mini",
    instructions=(
        "You are a web search agent that can search the web for information. Once "
        "you have the required information, summarize it with cleanly formatted links "
        "sourcing each bit of information. Ensure you answer the question accurately "
        "and use markdown formatting."
    ),
    tools=[search_web],
)

internal_docs_agent = Agent(
    name="Internal Docs Agent",
    model="gpt-4.1-mini",
    instructions=(
        "You are an agent with access to internal company documents. User's will ask "
        "you questions about the company and you will use the provided internal docs "
        "to answer the question. Ensure you answer the question accurately and use "
        "markdown formatting."
    ),
    tools=[search_internal_docs],
)

code_execution_agent = Agent(
    name="Code Execution Agent",
    model="gpt-4.1",
    instructions=(
        "You are an agent with access to a code execution environment. You will be "
        "given a question and you will need to write code to answer the question. "
        "Ensure you write the code in a way that is easy to understand and use."
    ),
    tools=[execute_code],
)

orchestrator_agent = Agent(
    name="Orchestrator Agent",
    model="gpt-4.1",
    instructions=(
        "You are the orchestrator of a multi-agent system. Your task is to take "
        "the user's query and pass it to the appropriate agent tool. The agent "
        "tools will see the input you provide and use it to get all of the "
        "information that you need to answer the user's query. You may need to "
        "call multiple agents to get all of the information you need. Do not "
        "mention or draw attention to the fact that this is a multi-agent system "
        "in your conversation with the user. Note that you are an assistant for "
        "the Skynet company, if the user asks about company information or "
        "finances, you should use our internal information rather than public "
        "information."
    ),
    tools=[
        # we're using the agents as tools for the orchestrator
        web_search_agent.as_tool(
            tool_name="web_search_agent",
            tool_description="Search the web for up-to-date information"
        ),
        internal_docs_agent.as_tool(
            tool_name="internal_docs_agent",
            tool_description="Search the internal docs for information"
        ),
        code_execution_agent.as_tool(
            tool_name="code_execution_agent",
            tool_description="Execute code to answer the question"
        ),
        get_current_date,
    ]
)

async def summarize_latest_news(query: str) -> str:
    result = await Runner.run(starting_agent=web_search_agent, input=query)
    print(result)

async def search_internal_docs_for_query(query: str) -> str:
    result = await Runner.run(starting_agent=internal_docs_agent, input=query)
    print(result)

def delegate_code_execution(query: str) -> str:
    result = Runner.run_sync(starting_agent=code_execution_agent, input=query)
    print(result)

async def handle_query_with_orchestration(query: str) -> str:
    result = await Runner.run(starting_agent=orchestrator_agent, input=query)
    print(result)

if __name__ == "__main__":
    # asyncio.run(summarize_latest_news("Latest news about Charlie Kirk"))
    # asyncio.run(search_internal_docs_for_query("What was our revenue in Q1?"))
    # delegate_code_execution("If I have four apples and I multiply them by seventy-one and one tenth bananas, how many do I have?")
    # asyncio.run(handle_query_with_orchestration("How long ago from today was it when got our last revenue report?"))
    asyncio.run(handle_query_with_orchestration("What is our current revenue, and what percentage of revenue comes from the T-1000 units?"))
