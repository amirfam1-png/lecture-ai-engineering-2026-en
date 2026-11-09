# Lecture 03 Answers

## Exercises

- Differences between the Lecture 01 (bare LLM) and agent answers:
  In Lecture 01, `gemini-3.5-flash-lite` said it had no information about AIE2026 (3/3 runs) and `gemini-3.8-flash` invented 3 levels. The agent calls `search_glossary` first and answers from the `homework-levels` entry (Basic / Implementation / Advanced, any one completes the homework). Live run: row "E0 baseline | What are the 3 homework levels..." in the table below.
- Tool calls shown by `--trace` (tool names and arguments): see the E0 rows in the live table (LoRA vs QLoRA question).
- Number of LLM calls for one question (`requests`): see the `requests` column in the live table. One search round = at least 2 requests (one to request the tool, one to answer).
- Tool added and the description in its docstring:
  `make_quiz(lecture: int)`: "Pick one glossary term from the given session and return a review question and its answer. Use when the learner asks for a review question, quiz, or self-check, such as 'Give me a review question for Lecture 02'. Show the question first and reveal the answer only after the learner has tried." Returns `{"lecture", "term", "question", "answer"}` as JSON; for a session with no terms (e.g. `lecture=0`) it returns a message listing the sessions that have terms. I also added "Use make_quiz when asked for a review question or quiz." to `INSTRUCTIONS`.

## Homework

- **Level attempted:** Advanced (I also did Basic and Implementation, and both Advanced options (a) and (b))

### How I worked and what I verified

- Offline (no API key, reproducible): `uv run pytest -q` → **21 passed** (11 original + 10 new in `tests/test_homework03.py`). `--list-tools` shows 4 tools. The approval flow is tested with a scripted `FunctionModel` (approve and deny paths). ADK and Pi were checked by loading their code.
- Live (Gemini API): `uv run python scripts/hw03_live.py` runs every Basic variant and the Implementation flow, saves the raw traces in `lectures/03/hw_runs/` and fills the table below. ADK: `PYTHONPATH=. uv run --with google-adk python adk_agent/compare.py`.

### Basic: change one text at a time, same questions, compare `--trace`

`scripts/hw03_live.py` builds one Agent per variant with exactly **one** change and the same model, tools and questions. This replaces editing and reverting `app/agent.py` by hand. `tool_plain(description=...)` replaces the docstring the model sees, which is the same as rewriting it in `tools.py`.

| ID | Single change |
|---|---|
| E0 | none (baseline) |
| E1 | INSTRUCTIONS: deleted "Always check the glossary with search_glossary before answering..." |
| E2 | `search_glossary` docstring: "Put only one term to look up in query" → "Put several terms together in query (for example, "LoRA QLoRA")" |
| E3 | INSTRUCTIONS: "End your answer by indicating the relevant session (Lecture NN)" → "End your answer with one review question for the learner" |

**Live results**

<!-- LIVE:BEGIN (filled by scripts/hw03_live.py) -->
_Not run yet. Run `uv run python scripts/hw03_live.py` in Codespaces._
<!-- LIVE:END -->

**Offline finding: what the tool returns when the model follows E2** (`hw_runs/search_offline.txt`, `search_glossary` called directly):

| query | returned terms |
|---|---|
| `LoRA` | LoRA, Rank (LoRA r), QLoRA |
| `LoRA QLoRA` / `LoRA, QLoRA` | LoRA, QLoRA |
| `PEFT LoRA QLoRA quantization` | PEFT, LoRA, QLoRA (**Quantization dropped**, `MAX_RESULTS = 3`) |
| `RAG` | Token, Fine-tuning, PEFT |
| `RAG, fine-tuning` | Fine-tuning |

1. Multi-term queries only work by accident. `search_glossary` removes spaces, then also matches when a glossary name of 3 or more characters is *contained in* the query, so `"LoRA QLoRA"` → `"loraqlora"` still hits both. Nothing in the code is designed for several terms.
2. The 3-result cap silently cuts the 4th term. With "several terms", one call can return fewer definitions than the model asked for, so the model has to fill in from memory or search again.
3. **The tool gives false positives for "RAG", even with one term.** RAG is not in the glossary. The definition substring match hits "f**rag**ments" (Token) and "sto**rag**e" (PEFT); only Fine-tuning mentions RAG for real. The model never gets "was not found", so the rule "say 'It is not in the glossary'" never fires. The live E0/E2 rows for the RAG question show whether the model still asserts a definition. Instructions cannot fix this: it needs a word-boundary match in the tool.

**Hypotheses written before the live run** (compare with the table):
- E1: with the general terms (LoRA/QLoRA, RAG), the model answers from its own knowledge with 0 tool calls and `requests=1`. With the course-specific `lecNN-start` it may still search, because the tool description says to use it for course-specific words. So the docstring still pushes the model to search after the INSTRUCTIONS line is gone.
- E2: fewer `search_glossary` calls (1 instead of 2 for LoRA/QLoRA), `requests` drops, answer quality is the same for 2 terms and worse for 4 terms (Quantization missing).
- E3: the answer ends with a question instead of "(Lecture 02)". The quiz may be written by the model itself, not by `make_quiz`.

### Implementation: `save_learning_log` with approval

- `app/tools.py`: `save_learning_log(lecture: int, title: str, content: str)` writes `learning_log/YYYYMMDD-HHMMSS-lecNN-<slug>.md`.
  - The file name is built only from a timestamp and a sanitized slug, so the model cannot write outside `learning_log/` (tested with `title="../../etc/passwd"`).
  - It never overwrites (adds `-2`, `-3`, ...), rejects empty text and caps the length at 5,000 characters.
  - The docstring says to use it only when the learner explicitly asks, and to write only what the learner said.
- `app/agent.py`:
  - `agent.tool_plain(tools.save_learning_log, requires_approval=True)`, `output_type=[str, DeferredToolRequests]`.
  - `run_with_approval()` loops while the output is `DeferredToolRequests`: it shows each call's arguments, asks `Save this? [y/N]`, then resumes with `DeferredToolResults` and `message_history=result.all_messages()`.
  - Denial is sent back as `ToolDenied("The user declined to save. Do not retry...")`. The default is No.
- **A problem I found and fixed:** after resuming, `result.usage` only counted the second run (`requests=1`), which hides the real cost of one question. I now pass `usage=result.usage` to the resumed `run_sync`, so `[usage]` shows the whole question (`requests=2` in the offline demo).
- Offline transcript (scripted model, `hw_runs/impl_offline.txt`): answering `y` creates one file; answering `n` creates none, and the model receives the denial message. A file is never written while the run is paused (`test_run_pauses_before_saving`).
- Live transcript (approve one, deny one, with the saved file contents): `hw_runs/impl_run.md`.
- Side effect: the original `test_agent.py` uses `TestModel`, which calls every tool. It now ends paused on `save_learning_log` instead of writing a file. The course test already allows this (`waiting = len(result.output.approvals)`).

### Advanced (a): the same agent in Google ADK (`adk_agent/glossary_agent/`)

`agent.py` imports the same `INSTRUCTIONS` and the same 3 tool functions from `app/`, and nothing in `app/` was changed for it. Checked with ADK 2.14.0: `adk run adk_agent/glossary_agent` loads `glossary_agent` and reaches the prompt. Live answers to the exercise questions: `hw_runs/adk_runs.md` (from `adk_agent/compare.py`, which prints tool calls like `--trace`).

| Aspect | Pydantic AI (`app/agent.py`) | ADK (`adk_agent/glossary_agent/agent.py`) |
|---|---|---|
| Instructions | `Agent(instructions=INSTRUCTIONS)` | `Agent(instruction=INSTRUCTIONS)`. ADK treats `{name}` as session-state placeholders, so braces in the text would break it (checked: INSTRUCTIONS has none) |
| Tools | registered after construction: `agent.tool_plain(fn)` | passed in the constructor: `tools=[fn, ...]`, each plain function wrapped in a `FunctionTool` |
| Tool schema (same docstrings) | `{"query": {"type": "string"}}`, required, `additionalProperties: false` | `{"query": {"title": "Query", "type": "string"}}`, required. The descriptions the model reads are identical |
| Model | passed at run time (`run_sync(model=...)`), so tests swap in `TestModel` with no API key | fixed string at construction (`model="gemini-3.5-flash-lite"`) |
| Running | one call: `run_sync(question)` → `result.output`, `result.all_messages()` | `adk run` discovers `root_agent` in the package. In code: `InMemoryRunner` + a session, then iterate over the streamed `Event`s |
| Conversation state | you pass `message_history` yourself | kept in the `Session` by the session service |
| Approval | `requires_approval=True` + `DeferredToolRequests` | `FunctionTool(fn, require_confirmation=True)` exists in 2.14.0 (not used, out of scope) |

Note: `INSTRUCTIONS` mentions `save_learning_log`, which the ADK agent does not have. The live ADK runs show whether this confuses the model.

### Advanced (b): Pi's system prompt vs my INSTRUCTIONS

I rendered Pi's real default prompt by calling Pi's own `buildSystemPrompt()` from the published npm package (`@earendil-works/pi-coding-agent` 1.5.0), with its default tools read/bash/edit/write. Output: `hw_runs/pi_system_prompt.txt`. Source: `packages/coding-agent/src/core/system-prompt.ts`, commit `7d07332`.

| Topic | Pi | My INSTRUCTIONS |
|---|---|---|
| Role | "a coding assistant running inside pi, a coding agent harness" | learning support agent for AIE2026 |
| Tool list in the prompt | yes: one-line snippet per tool + "Additional tools may be available" | no, names only. Details are in the tool docstrings |
| Which tool for what | yes: "Use read to examine files instead of cat or sed", "Use write only for new files or complete rewrites" | partly: search before answering, summary for session content |
| Grounding / no guessing | **not written** | "Always check the glossary...", "say 'It is not in the glossary'" |
| Safety / confirmation | **not written**: no rule to ask before editing, deleting or running commands | saving needs approval, enforced in code with `requires_approval=True` |
| Output style | "Be concise", "Show file paths clearly" | "End your answer by indicating the relevant session (Lecture NN)" |
| Teaching policy | none | "Guide learners with hints... rather than writing homework answers" |
| Environment | `<cwd>`, docs paths, plus `AGENTS.md` / `CLAUDE.md` loaded as `<project_context>` | none |
| How the prompt is built | assembled by code: rules depend on the selected tools (e.g. "Use bash for ls, rg, find" only when no grep/find/ls tool exists), duplicates removed, XML-tagged sections. `diffSystemPromptSections()` sends only the changed sections later | one fixed string |

What I learned:
1. Pi's prompt is generic mechanics, and mine is domain policy. Pi tells the model *how to use its tools*; mine tells it *what is a good answer here* (grounded, cites the session, does not do the homework).
2. Pi needs tool-choice rules because its tools overlap: `bash` can do everything `read`/`edit`/`write` do. My tools do not overlap, so the docstrings are enough.
3. Pi has no confirmation rule, so it runs commands without asking, which is why the course says to run it in Codespaces. Safety comes from the environment (a disposable container), not the prompt. My agent does the reverse for its one risky action: the code enforces approval, so it does not depend on the model obeying a sentence.
4. Pi builds its prompt from the active tools. If I add or remove a tool in my agent, I have to edit INSTRUCTIONS by hand (I had to add the `make_quiz` and `save_learning_log` lines myself).

### Observations and questions

1. The tool's matching quality limits what instructions can achieve: no INSTRUCTIONS wording makes the agent say "not in the glossary" for RAG when the tool returns 3 hits. Should `search_glossary` use word-boundary matching and return an explicit `not_found` list for each term?
2. Approval in code beats a sentence in the prompt. `requires_approval=True` stops the run before the side effect whatever the model decides.
3. Question: with `requires_approval`, the model has already written `content` before the user sees it. Is there a standard Pydantic AI pattern to let the user *edit* the arguments (not just approve or deny) before the tool runs?
