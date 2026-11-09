"""Lecture 03 homework (Advanced a): the exercise agent rebuilt with Google ADK.

Same INSTRUCTIONS and the same tool functions as app/agent.py (Pydantic AI). Only the agent assembly differs.
Run from the repo root:
    PYTHONPATH=. uv run --with google-adk adk run adk_agent/glossary_agent
"""

import os

from google.adk.agents import Agent

from app import tools
from app.agent import INSTRUCTIONS

root_agent = Agent(
    model=os.getenv("AIE_MODEL", "gemini-3.5-flash-lite"),
    name="glossary_agent",
    description="Learning support agent for AIE2026 that answers from the course glossary.",
    instruction=INSTRUCTIONS,
    # Plain functions: ADK wraps each in a FunctionTool and builds the declaration from name, type hints and docstring.
    # save_learning_log (approval tool) is out of scope for (a), so it is not registered here.
    tools=[tools.search_glossary, tools.get_lecture_summary, tools.make_quiz],
)
