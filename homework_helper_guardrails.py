#!/usr/bin/env python3
import asyncio # needed for async calls

from agents import Agent
from agents import GuardrailFunctionOutput
from agents import input_guardrail
from agents import InputGuardrail
from agents import RunContextWrapper
from agents import Runner
from agents.exceptions import InputGuardrailTripwireTriggered
from pydantic import BaseModel

import env

OPENAI_API_KEY = env.get_required_env("OPENAI_API_KEY")

class HomeworkOutput(BaseModel):
    is_relevant_homework: bool
    reasoning: str

input_guardrail_agent = Agent(
    name="Input Guardrail check",
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

async def homework_input_guardrail(ctx: RunContextWrapper[None], agent: Agent, input_data: str):
    """The Agent that's responsible for ensuring we stay on allowed homework topics."""
    result = await Runner.run(input_guardrail_agent, input_data, context=ctx.context)
    final_output = result.final_output_as(HomeworkOutput)
    return GuardrailFunctionOutput(
        output_info=final_output,
        tripwire_triggered=not final_output.is_relevant_homework, # we want to block requests that don't fit under math or history
    )

triage_agent = Agent(
    name="Triage Agent",
    instructions="You determine which agent to use based on the user's homework question",
    handoffs=[history_tutor_agent, math_tutor_agent],
    input_guardrails=[InputGuardrail(guardrail_function=homework_input_guardrail)]
)

async def homework_helper_agent_async():

    class Question:
        def __init__(self, type: str, question: str):
            self.type = type
            self.question = question

    questions = [
        Question("History question", "Be brief. When did Arminianism and Calvinism come about?"),
        Question("General/philosophical question", "Be brief. What is the meaning of life?"),
        Question("Math question (simple)", "Be brief. What is an isosceles triangle?"),
        Question("Math question (hard)", "Be brief. What is Zorn's Lemma?"),
        Question("Relationship advice", "Be brief. Can you give me some relationship advice?")
    ]

    for question in questions:
        try:
            result = await Runner.run(
                starting_agent=triage_agent,
                input=question.question
            )
            print(f"✅ {result.final_output}"+'\n')
        except InputGuardrailTripwireTriggered as e:
            print(f"📥 Input Guardrail blocked the question '{question.question}' of type '{question.type}': {e}\n")

if __name__ == "__main__":
    asyncio.run(homework_helper_agent_async()) # Web servers, notebooks, anything already async or needing concurrency/streaming
