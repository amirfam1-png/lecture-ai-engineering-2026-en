"""Lecture 03 homework: run the live experiments with the Gemini API and record the results.

Usage (from the repo root, in Codespaces where GEMINI_API_KEY is set):
    uv run python scripts/hw03_live.py            # Basic experiments + Implementation run
    uv run python scripts/hw03_live.py --basic    # Basic only
    uv run python scripts/hw03_live.py --impl     # Implementation only
    uv run python scripts/hw03_live.py --repeat 2 # Run each Basic case twice (tool use varies run to run)

Basic: instead of editing app/agent.py back and forth, each variant builds its own Agent with
exactly ONE text change (INSTRUCTIONS line or the search_glossary description). The tools,
the model, and the questions are the same, so only that one change differs.

Outputs:
    lectures/03/hw_runs/basic_runs.jsonl   raw data (tool calls, args, usage, answer)
    lectures/03/hw_runs/basic_results.md   summary table + full traces
    lectures/03/hw_runs/impl_run.md        approval flow transcript
    lectures/03/answer.md                  the block between LIVE markers is replaced with the summary
"""

import argparse
import json
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from pydantic_ai import Agent, DeferredToolRequests  # noqa: E402
from pydantic_ai.exceptions import ModelHTTPError  # noqa: E402
from pydantic_ai.messages import ToolCallPart  # noqa: E402

from app import agent as base  # noqa: E402
from app import tools  # noqa: E402
from app.config import MODEL  # noqa: E402

OUT = ROOT / "lectures" / "03" / "hw_runs"
ANSWER = ROOT / "lectures" / "03" / "answer.md"

LINE_ALWAYS = "- Always check the glossary with search_glossary before answering about terms or course-specific information.\n"
LINE_LECTURE = "- End your answer by indicating the relevant session (Lecture NN).\n"
ONE_TERM = 'Put only one term to look up in query (for example, "LoRA").'
SEVERAL = 'Put several terms together in query (for example, "LoRA QLoRA").'

Q_COURSE = "What is a lecNN-start tag in the AIE2026 course?"
Q_PAIR = "What is the difference between LoRA and QLoRA?"
Q_FOUR = "Briefly explain PEFT, LoRA, QLoRA and quantization."
Q_ABSENT = "What is the difference between RAG and fine-tuning?"
Q_LEVELS = "What are the 3 homework levels in the AIE2026 course?"  # Exercise step 2 (same as Lecture 01)
Q_QUIZ = "Give me one review question from Lecture 02"  # Exercise step 5 (make_quiz)


def variant_agent(instructions: str, search_description: str | None = None) -> Agent:
    a = Agent(instructions=instructions, output_type=[str, DeferredToolRequests])
    # description= replaces the docstring the model sees, exactly like rewriting it in tools.py
    a.tool_plain(tools.search_glossary, description=search_description)
    a.tool_plain(tools.get_lecture_summary)
    a.tool_plain(tools.make_quiz)
    a.tool_plain(tools.save_learning_log, requires_approval=True)
    return a


def experiments():
    assert LINE_ALWAYS in base.INSTRUCTIONS and LINE_LECTURE in base.INSTRUCTIONS
    doc = tools.search_glossary.__doc__
    assert ONE_TERM in doc
    return [
        ("E0 baseline", "no change", variant_agent(base.INSTRUCTIONS), [Q_LEVELS, Q_QUIZ, Q_COURSE, Q_PAIR, Q_FOUR, Q_ABSENT]),
        ("E1 no-always-search", 'INSTRUCTIONS: deleted "Always check the glossary with search_glossary ..."',
         variant_agent(base.INSTRUCTIONS.replace(LINE_ALWAYS, "")), [Q_COURSE, Q_PAIR, Q_ABSENT]),
        ("E2 several-terms", 'search_glossary docstring: "Put only one term" -> "Put several terms together"',
         variant_agent(base.INSTRUCTIONS, doc.replace(ONE_TERM, SEVERAL)), [Q_PAIR, Q_FOUR, Q_ABSENT]),
        ("E3 end-with-quiz", 'INSTRUCTIONS: "End ... (Lecture NN)" -> "End with one review question"',
         variant_agent(base.INSTRUCTIONS.replace(LINE_LECTURE, "- End your answer with one review question for the learner.\n")),
         [Q_PAIR]),
    ]


def run_once(agent: Agent, question: str, model, pause: float):
    for attempt in range(4):
        try:
            return base.run_with_approval(agent, question, model, ask=lambda _: "n")
        except ModelHTTPError as e:
            if e.status_code in (429, 503) and attempt < 3:
                print(f"  {e.status_code}, waiting 60 s and retrying…")
                time.sleep(60)
                continue
            raise
        finally:
            time.sleep(pause)


def summarize(name, change, question, result) -> dict:
    calls = [p for m in result.all_messages() for p in m.parts if isinstance(p, ToolCallPart)]
    answer = str(result.output)
    tail = answer.strip()[-200:]
    return {
        "experiment": name,
        "change": change,
        "question": question,
        "tool_calls": [{"tool": c.tool_name, "args": c.args_as_dict()} for c in calls],
        "n_tool_calls": len(calls),
        "requests": result.usage.requests,
        "input_tokens": result.usage.input_tokens,
        "output_tokens": result.usage.output_tokens,
        "ends_with_lecture": bool(re.search(r"Lecture\s*\d+\W*$", answer.strip())),
        "says_not_in_glossary": "not in the glossary" in answer.casefold(),
        "ends_with_question": "?" in tail[-80:],
        "answer": answer,
    }


def calls_text(r):
    return "; ".join(f"{c['tool']}({json.dumps(c['args'], ensure_ascii=False)})" for c in r["tool_calls"]) or "(none)"


def write_basic(rows):
    OUT.mkdir(parents=True, exist_ok=True)
    with open(OUT / "basic_runs.jsonl", "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    table = [
        "| Experiment | Question | Tool calls (order, args) | #calls | requests | Ends 'Lecture NN' | 'not in glossary' |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        table.append(
            f"| {r['experiment']} | {r['question']} | {calls_text(r)} | {r['n_tool_calls']} | {r['requests']} "
            f"| {'yes' if r['ends_with_lecture'] else 'no'} | {'yes' if r['says_not_in_glossary'] else 'no'} |"
        )
    table_md = "\n".join(table)

    detail = [f"# Lecture 03 homework (Basic): live results\n\nModel: `{MODEL}`\n", table_md, "\n## Full answers\n"]
    for r in rows:
        detail.append(f"### {r['experiment']} | {r['question']}\n\nChange: {r['change']}\n\n```text\n{r['answer']}\n\n--- trace ---")
        for c in r["tool_calls"]:
            detail.append(f"[tool call] {c['tool']}({c['args']})")
        detail.append(f"[usage] requests={r['requests']} in={r['input_tokens']} out={r['output_tokens']}\n```\n")
    (OUT / "basic_results.md").write_text("\n".join(detail), encoding="utf-8")
    return table_md


def update_answer(table_md: str):
    text = ANSWER.read_text(encoding="utf-8")
    block = (
        "<!-- LIVE:BEGIN (filled by scripts/hw03_live.py) -->\n"
        f"Model: `{MODEL}`. Full answers and traces: [hw_runs/basic_results.md](hw_runs/basic_results.md)\n\n"
        f"{table_md}\n<!-- LIVE:END -->"
    )
    new = re.sub(r"<!-- LIVE:BEGIN.*?<!-- LIVE:END -->", lambda _: block, text, flags=re.S)
    ANSWER.write_text(new, encoding="utf-8")


def run_basic(model, repeat: int, pause: float):
    rows = []
    for name, change, agent, questions in experiments():
        for q in questions:
            for i in range(repeat):
                label = name if repeat == 1 else f"{name} #{i + 1}"
                print(f"[{label}] {q}")
                result = run_once(agent, q, model, pause)
                r = summarize(label, change, q, result)
                print(f"  calls: {calls_text(r)} | requests={r['requests']}")
                rows.append(r)
    table_md = write_basic(rows)
    update_answer(table_md)
    print(f"\nWrote {OUT / 'basic_results.md'} and updated the LIVE block in {ANSWER}")


def run_impl(model, pause: float):
    """Two live runs: the user approves the first save and declines the second."""
    OUT.mkdir(parents=True, exist_ok=True)
    cases = [
        ("y", "Save a learning log for Lecture 03: I learned that an agent is model + loop + tools, "
              "and that --trace shows which tool was called with which arguments."),
        ("n", "Please record in my learning log that I got stuck on DeferredToolRequests in Lecture 03."),
    ]
    lines = [f"# Lecture 03 homework (Implementation): live approval runs\n\nModel: `{MODEL}`\n"]
    for answer, q in cases:
        before = set(tools.LOG_DIR.glob("*.md")) if tools.LOG_DIR.exists() else set()
        prompts = []

        def ask(prompt, answer=answer):
            prompts.append(prompt + answer)
            return answer

        import contextlib
        import io

        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            result = run_once_impl(q, model, ask, pause)
            print(result.output)
            base.print_trace(result)
        after = set(tools.LOG_DIR.glob("*.md")) if tools.LOG_DIR.exists() else set()
        new_files = sorted(p.name for p in after - before)
        out = buf.getvalue()
        print(out)
        lines += [f"## User answers '{answer}'\n\nQuestion: {q}\n", "```text", out.rstrip(), "```",
                  f"\nNew files in learning_log/: {new_files or 'none'}\n"]
        for name in new_files:
            lines += [f"Content of `{name}`:\n", "```markdown", (tools.LOG_DIR / name).read_text(encoding="utf-8").rstrip(), "```\n"]
    (OUT / "impl_run.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT / 'impl_run.md'}")


def run_once_impl(q, model, ask, pause):
    for attempt in range(4):
        try:
            return base.run_with_approval(base.agent, q, model, ask=ask)
        except ModelHTTPError as e:
            if e.status_code in (429, 503) and attempt < 3:
                time.sleep(60)
                continue
            raise
        finally:
            time.sleep(pause)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--basic", action="store_true")
    p.add_argument("--impl", action="store_true")
    p.add_argument("--repeat", type=int, default=1)
    p.add_argument("--pause", type=float, default=8.0, help="Seconds between runs (free-tier rate limit)")
    args = p.parse_args()
    both = not (args.basic or args.impl)
    model = base.build_model()
    if args.basic or both:
        run_basic(model, args.repeat, args.pause)
    if args.impl or both:
        run_impl(model, args.pause)


if __name__ == "__main__":
    main()
