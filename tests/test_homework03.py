"""Lecture 03 exercise and homework tests (no LLM or API key used).

FunctionModel is a scripted fake model: turn 1 requests save_learning_log, turn 2 answers in text.
This lets us check the approval pause, approve and deny paths deterministically.
"""

import json

import pytest
from pydantic_ai import DeferredToolRequests
from pydantic_ai.messages import ModelResponse, TextPart, ToolCallPart, ToolReturnPart
from pydantic_ai.models.function import FunctionModel

from app import agent as agent_module
from app import tools

LOG_ARGS = {"lecture": 3, "title": "Agents and tools", "content": "Agent = model + loop + tools."}


@pytest.fixture
def log_dir(tmp_path, monkeypatch):
    d = tmp_path / "learning_log"
    monkeypatch.setattr(tools, "LOG_DIR", d)
    return d


def test_make_quiz_returns_question_from_that_lecture():
    quiz = json.loads(tools.make_quiz(2))
    lecture2 = {e["term"]: e["definition"] for e in tools.load_glossary() if e["lecture"] == 2}
    assert quiz["term"] in lecture2
    assert quiz["answer"] == lecture2[quiz["term"]]
    assert quiz["term"] in quiz["question"]


def test_make_quiz_handles_missing_lecture():
    assert "No glossary terms" in tools.make_quiz(0)


def test_save_learning_log_writes_markdown(log_dir):
    msg = tools.save_learning_log(**LOG_ARGS)
    files = list(log_dir.glob("*.md"))
    assert len(files) == 1 and msg.startswith("Saved:")
    text = files[0].read_text(encoding="utf-8")
    assert "# Agents and tools" in text and "Agent = model + loop + tools." in text
    assert "-lec03-agents-and-tools" in files[0].name


def test_save_learning_log_never_overwrites(log_dir):
    tools.save_learning_log(**LOG_ARGS)
    tools.save_learning_log(**LOG_ARGS)
    assert len(list(log_dir.glob("*.md"))) == 2


def test_save_learning_log_cannot_escape_folder(log_dir):
    tools.save_learning_log(lecture=3, title="../../etc/passwd", content="x")
    files = list(log_dir.glob("*.md"))
    assert len(files) == 1 and files[0].parent == log_dir


def test_save_learning_log_rejects_empty(log_dir):
    assert "Not saved" in tools.save_learning_log(lecture=3, title=" ", content="x")
    assert not log_dir.exists()


def test_save_tool_requires_approval():
    tool = agent_module.agent._function_toolset.tools["save_learning_log"]
    assert tool.requires_approval
    for name in ("search_glossary", "get_lecture_summary", "make_quiz"):
        assert not agent_module.agent._function_toolset.tools[name].requires_approval


def _scripted_model():
    def respond(messages, info):
        returns = [p for m in messages for p in m.parts if isinstance(p, ToolReturnPart)]
        if not returns:
            return ModelResponse(parts=[ToolCallPart("save_learning_log", LOG_ARGS)])
        return ModelResponse(parts=[TextPart(f"Result: {returns[-1].content}")])

    return FunctionModel(respond)


def test_run_pauses_before_saving(log_dir):
    result = agent_module.agent.run_sync("Save my notes", model=_scripted_model())
    assert isinstance(result.output, DeferredToolRequests)
    assert [c.tool_name for c in result.output.approvals] == ["save_learning_log"]
    assert not log_dir.exists()  # Nothing is written while waiting


def test_approve_saves(log_dir, capsys):
    result = agent_module.run_with_approval(agent_module.agent, "Save my notes", _scripted_model(), ask=lambda _: "y")
    assert len(list(log_dir.glob("*.md"))) == 1
    assert "Saved:" in result.output
    assert "[approval needed] save_learning_log" in capsys.readouterr().out


def test_deny_does_not_save(log_dir):
    result = agent_module.run_with_approval(agent_module.agent, "Save my notes", _scripted_model(), ask=lambda _: "n")
    assert not log_dir.exists()
    assert "declined" in result.output
