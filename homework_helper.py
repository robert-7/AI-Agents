#!/usr/bin/env python3
import asyncio # needed for async calls

from agents import Agent
from agents import GuardrailFunctionOutput
from agents import InputGuardrail
from agents import Runner
from agents.exceptions import InputGuardrailTripwireTriggered
from pydantic import BaseModel

import env

OPENAI_API_KEY = env._get_required_env("OPENAI_API_KEY")

class HomeworkOutput(BaseModel):
    is_homework: bool
    reasoning: str

guardrail_agent = Agent(
    name="Guardrail check",
    instructions="Check if the user is asking about homework.",
    output_type=HomeworkOutput,
)

history_tutor_agent = Agent(
    name="History Tutor",
    handoff_description="Specialist agent for historical questions",
    instructions="You provide assistance with historical queries. Explain important events and context clearly.",
)

math_tutor_agent = Agent(
    name="Math Tutor",
    handoff_description="Specialist agent for math questions",
    instructions="You provide help with math problems. Explain your reasoning at each step and include examples",
)

async def homework_guardrail(ctx, agent, input_data):
    result = await Runner.run(guardrail_agent, input_data, context=ctx.context)
    final_output = result.final_output_as(HomeworkOutput)
    return GuardrailFunctionOutput(
        output_info=final_output,
        tripwire_triggered=not final_output.is_homework, # we want to block requests that don't fit under math or history
    )

triage_agent = Agent(
    name="Triage Agent",
    instructions="You determine which agent to use based on the user's homework question",
    handoffs=[history_tutor_agent, math_tutor_agent],
    input_guardrails=[
        InputGuardrail(guardrail_function=homework_guardrail),
    ],
)

async def homework_helper_agent_async():

    class Question:
        def __init__(self, type: str, question: str):
            self.type = type
            self.question = question

    questions = [
        Question("History question", "Be brief. When did Arminianism and Calvinism come about?"),
        Question("General/philosophical question", "Be brief. What is the meaning of life?"),
        Question("Math question", "Be brief. What is the value of the Golden Ratio?"),
        Question("Relationship advice", "Be brief. Can you give me some relationship advice?")
    ]

    for question in questions:
        try:
            result = await Runner.run(triage_agent, question.question)
            print(result.final_output)
        except InputGuardrailTripwireTriggered as e:
            print(f"Guardrail blocked the question '{question.question}' of type '{question.type}':", e)

if __name__ == "__main__":
    asyncio.run(homework_helper_agent_async()) # Web servers, notebooks, anything already async or needing concurrency/streaming
