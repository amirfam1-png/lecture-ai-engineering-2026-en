# Lecture 03 Answers

## Exercises

- Differences between the Lecture 01 (bare LLM) and agent answers:
  In Lecture 01, `gemini-3.5-flash-lite` said it had no information about AIE2026 (3/3 runs) and `gemini-3.8-flash` invented 3 levels. The agent called `search_glossary({"query": "homework levels"})` and answered correctly from the glossary: Basic (review), Implementation (write your own code), Advanced (research and experimentation), any one completes the homework, ending with "(Lecture 01)". Same model, no invention, no refusal: the difference is the data, not the model.
- Tool calls shown by `--trace` (tool names and arguments): "What is the difference between LoRA and QLoRA?" → `search_glossary({'query': 'LoRA'})`, `search_glossary({'query': 'QLoRA'})`. "Give me one review question from Lecture 02" → `make_quiz({'lecture': 2})` (it asked "What does QLoRA mean?" and held back the answer).
- Number of LLM calls for one question (`requests`): 2 for most questions (1 to request the tools, 1 to answer). The number of tool calls does not set it: "Briefly explain PEFT, LoRA, QLoRA and quantization" made **4** `search_glossary` calls in **2** requests, because the model requested all 4 in parallel in one response. A second search round costs an extra request (RAG question: 3 calls, 3 requests).
- Tool added and the description in its docstring:
  `make_quiz(lecture: int)`: "Pick one glossary term from the given session and return a review question and its answer. Use when the learner asks for a review question, quiz, or self-check, such as 'Give me a review question for Lecture 02'. Show the question first and reveal the answer only after the learner has tried." Returns `{"lecture", "term", "question", "answer"}` as JSON; for a session with no terms (e.g. `lecture=0`) it returns a message listing the sessions that have terms. I also added "Use make_quiz when asked for a review question or quiz." to `INSTRUCTIONS`.

## Homework

- **Level attempted:** Advanced (I also did Basic and Implementation, and both Advanced options (a) and (b))

### How I worked and what I verified

- Offline (no API key, reproducible): `uv run pytest -q` → **21 passed** (11 original + 10 new in `tests/test_homework03.py`). `--list-tools` shows 4 tools. The approval flow is tested with a scripted `FunctionModel` (approve and deny paths). ADK and Pi were checked by loading their code.
- Live (Gemini API, `gemini-3.5-flash-lite`, Codespaces, 2026-11-09): `uv run python scripts/hw03_live.py` ran every Basic variant and the Implementation flow and filled the table below. ADK: `PYTHONPATH=. uv run --with google-adk python adk_agent/compare.py`. Raw traces are in `lectures/03/hw_runs/`. Each case ran once, so single differences may be run-to-run noise.

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
Model: `gemini-3.5-flash-lite`. Full answers and traces: [hw_runs/basic_results.md](hw_runs/basic_results.md)

| Experiment | Question | Tool calls (order, args) | #calls | requests | Ends 'Lecture NN' | 'not in glossary' |
|---|---|---|---|---|---|---|
| E0 baseline | What are the 3 homework levels in the AIE2026 course? | search_glossary({"query": "homework levels"}) | 1 | 2 | yes | no |
| E0 baseline | Give me one review question from Lecture 02 | make_quiz({"lecture": 2}) | 1 | 2 | yes | no |
| E0 baseline | What is a lecNN-start tag in the AIE2026 course? | search_glossary({"query": "lecNN-start"}) | 1 | 2 | yes | no |
| E0 baseline | What is the difference between LoRA and QLoRA? | search_glossary({"query": "LoRA"}); search_glossary({"query": "QLoRA"}) | 2 | 2 | yes | no |
| E0 baseline | Briefly explain PEFT, LoRA, QLoRA and quantization. | search_glossary({"query": "PEFT"}); search_glossary({"query": "LoRA"}); search_glossary({"query": "QLoRA"}); search_glossary({"query": "quantization"}) | 4 | 2 | yes | no |
| E0 baseline | What is the difference between RAG and fine-tuning? | search_glossary({"query": "RAG"}); search_glossary({"query": "fine-tuning"}); search_glossary({"query": "RAG"}) | 3 | 3 | yes | yes |
| E1 no-always-search | What is a lecNN-start tag in the AIE2026 course? | search_glossary({"query": "lecNN-start"}) | 1 | 2 | yes | no |
| E1 no-always-search | What is the difference between LoRA and QLoRA? | search_glossary({"query": "LoRA"}); search_glossary({"query": "QLoRA"}) | 2 | 2 | yes | no |
| E1 no-always-search | What is the difference between RAG and fine-tuning? | search_glossary({"query": "RAG"}); search_glossary({"query": "Fine-tuning"}); search_glossary({"query": "RAG"}) | 3 | 3 | yes | no |
| E2 several-terms | What is the difference between LoRA and QLoRA? | search_glossary({"query": "LoRA QLoRA"}) | 1 | 2 | yes | no |
| E2 several-terms | Briefly explain PEFT, LoRA, QLoRA and quantization. | search_glossary({"query": "PEFT LoRA QLoRA quantization"}) | 1 | 2 | yes | no |
| E2 several-terms | What is the difference between RAG and fine-tuning? | search_glossary({"query": "RAG fine-tuning"}) | 1 | 2 | yes | no |
| E3 end-with-quiz | What is the difference between LoRA and QLoRA? | search_glossary({"query": "LoRA"}) | 1 | 2 | no | no |
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
3. **The tool gives false positives for "RAG", even with one term.** RAG is not in the glossary. The definition substring match hits "f**rag**ments" (Token) and "sto**rag**e" (PEFT); only Fine-tuning mentions RAG for real. So the model never gets "was not found" and has to notice by itself that none of the 3 hits is RAG. Live, it managed in E0 and ADK but not in E1/E2 (see below). The reliable fix is a word-boundary match in the tool, not more instructions.

**What changed (observed)**

- **E1, deleting "Always check the glossary": no change in tool use.** All 3 questions still searched, with the same calls and request counts as E0. I expected the model to answer LoRA/QLoRA and RAG from memory with 0 calls; it did not. The `search_glossary` docstring ("Use before answering about AI engineering terms or words specific to this course") is enough on its own to trigger the search. **The tool description carries as much weight as INSTRUCTIONS.** One change did appear: for RAG, E0 said "RAG is not in the glossary" but E1 explained RAG from its own knowledge with no warning (same 3 searches). With one run each, I cannot tell if this is the deleted line or noise.
- **E2, "put several terms together": fewer calls, same requests, and silent gaps.** Every question became 1 combined call (`"LoRA QLoRA"`, `"PEFT LoRA QLoRA quantization"`, `"RAG fine-tuning"`). `requests` stayed at 2, since E0 already ran its searches in parallel, so the saving is tool calls, not LLM calls. The cost is in the answers:
  - 4 terms: the tool returned only PEFT, LoRA, QLoRA (3-result cap, see the offline table). The answer still defined Quantization and opened with "based on the course materials", so **a definition from the model's memory was presented as coming from the glossary.**
  - RAG: the combined query hit only Fine-tuning. The answer explained RAG at length with no "not in the glossary". E0, which searched RAG on its own (twice), did flag it.
- **E3, "end with one review question": format changed as asked, and fewer searches.** The answer ended with a review question (no "Lecture NN"), and the model searched only "LoRA" (1 call instead of 2) and took QLoRA from the LoRA results. It did not call `make_quiz`; it wrote the question itself. A line about the *ending* changed the *search behavior*, so INSTRUCTIONS lines interact.
- **RAG false positives, live:** in E0 the model searched "RAG" twice, got Token/Fine-tuning/PEFT both times, and still said "RAG is not in the glossary" correctly. The ADK agent did better: after 2 bad "RAG" results it searched "Retrieval-Augmented Generation" and got a clean "was not found". So the model can work around the bad matches, but it spends extra requests (3 to 4 instead of 2), and E1/E2 show it does not always manage.

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
- Live run (`hw_runs/impl_run.md`):
  - **Approve:** the CLI showed title "Agent, Loop, Tools and Tracing", lecture 3 and the content. After `y`, it wrote `learning_log/20261109-004424-lec03-agent-loop-tools-and-tracing.md` (committed). `requests=2`, so the usage fix works live.
  - **Deny:** after `n`, no file was written, and the model answered "the save was not completed", without retrying. Before asking to save, it called `search_glossary("DeferredToolRequests")` because of the "Always check the glossary" rule, which added a request (`requests=3`). That rule also fires on requests that are not questions.
- Side effect: the original `test_agent.py` uses `TestModel`, which calls every tool. It now ends paused on `save_learning_log` instead of writing a file. The course test already allows this (`waiting = len(result.output.approvals)`).

### Advanced (a): the same agent in Google ADK (`adk_agent/glossary_agent/`)

`agent.py` imports the same `INSTRUCTIONS` and the same 3 tool functions from `app/`, and nothing in `app/` was changed for it. Checked with ADK 2.14.0: `adk run adk_agent/glossary_agent` loads `glossary_agent` and reaches the prompt. Live answers to the exercise questions: `hw_runs/adk_runs.md` (from `adk_agent/compare.py`, which prints tool calls like `--trace`).

**Answers, ADK vs Pydantic AI (same model, same INSTRUCTIONS and tools):** with the same tools and instructions, the behavior was nearly the same.
- 3 homework levels: identical call (`search_glossary("homework levels")`) and a correct answer ending "(Lecture 01)".
- LoRA vs QLoRA: identical, 2 parallel searches.
- Review question: identical, `make_quiz({'lecture': 2})`. Different term (Epoch vs QLoRA), as expected from `random.choice`.
- RAG vs fine-tuning: ADK searched 4 times (RAG, Fine-tuning, RAG, then "Retrieval-Augmented Generation") and said "the term itself is not in the glossary". Pydantic AI searched 3 times and also flagged it.
- One visible framework difference: ADK wraps a `str` return as `{'result': '...'}` before passing it to the model, while Pydantic AI passes the string as is.
- The missing `save_learning_log` tool caused no problems: no question asked to save.

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

1. The tool's matching quality limits what instructions can achieve. For RAG, the tool returns 3 wrong hits instead of "not found", so the "say 'It is not in the glossary'" rule only works if the model notices the mismatch itself (it did in E0, not in E1/E2). Should `search_glossary` use word-boundary matching and return an explicit `not_found` list for each term?
2. Approval in code beats a sentence in the prompt. `requires_approval=True` stops the run before the side effect whatever the model decides.
3. INSTRUCTIONS and docstrings are not independent. Removing the "always search" line did nothing because the docstring says the same thing (E1). Changing the ending line also changed how many searches ran (E3). To test one sentence, both places must be read together.
4. "Based on the course materials" is not proof. In E2, a definition the tool never returned was labeled as coming from the glossary. A check that compares each defined term against the tool results would catch this; reading the answer would not.
5. Question: with `requires_approval`, the model has already written `content` before the user sees it. Is there a standard Pydantic AI pattern to let the user *edit* the arguments (not just approve or deny) before the tool runs?
