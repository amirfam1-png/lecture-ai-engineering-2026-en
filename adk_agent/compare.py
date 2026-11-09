"""Lecture 03 homework (Advanced a): ask the ADK agent the exercise questions and record tool calls (like --trace).

Run from the repo root (GEMINI_API_KEY set):
    PYTHONPATH=. uv run --with google-adk python adk_agent/compare.py
Writes lectures/03/hw_runs/adk_runs.md
"""

import asyncio
import time
from pathlib import Path

from google.adk.runners import InMemoryRunner
from google.genai import types

from adk_agent.glossary_agent.agent import root_agent

QUESTIONS = [
    "What are the 3 homework levels in the AIE2026 course?",
    "What is the difference between LoRA and QLoRA?",
    "Give me one review question from Lecture 02",
    "What is the difference between RAG and fine-tuning?",
]
OUT = Path(__file__).resolve().parent.parent / "lectures" / "03" / "hw_runs" / "adk_runs.md"


async def ask(runner: InMemoryRunner, question: str) -> str:
    # New session per question, so answers do not depend on earlier questions (same as one app.agent run)
    session = await runner.session_service.create_session(app_name=runner.app_name, user_id="student")
    lines, answer, llm_calls, tokens = [], [], 0, 0
    message = types.Content(role="user", parts=[types.Part(text=question)])
    async for event in runner.run_async(user_id="student", session_id=session.id, new_message=message):
        if event.author == root_agent.name and event.usage_metadata:
            llm_calls += 1
            tokens += event.usage_metadata.total_token_count or 0
        for call in event.get_function_calls():
            lines.append(f"[tool call]   {call.name}({dict(call.args or {})})")
        for resp in event.get_function_responses():
            lines.append(f"[tool return] {resp.name} -> {str(resp.response)[:120]}…")
        if event.is_final_response() and event.content and event.content.parts:
            answer += [p.text for p in event.content.parts if p.text]
    lines.append(f"[usage] model responses with usage={llm_calls}, total_tokens={tokens}")
    return "\n".join(answer) + "\n\n--- trace ---\n" + "\n".join(lines)


async def main():
    runner = InMemoryRunner(agent=root_agent, app_name="glossary_agent")
    out = [f"# Lecture 03 homework (Advanced a): ADK runs\n\nModel: `{root_agent.model}`\n"]
    for q in QUESTIONS:
        print(f"> {q}")
        text = await ask(runner, q)
        print(text, "\n")
        out += [f"## {q}\n", "```text", text, "```\n"]
        time.sleep(8)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(out), encoding="utf-8")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    asyncio.run(main())
