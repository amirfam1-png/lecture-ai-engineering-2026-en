# Lecture 05 Answers

## Exercises

- Answering model (`[model]` shown during execution): `gemini-3.5-flash-lite`
- Comparison question: "In Lecture 02, what does LoRA freeze and what does it train? What does QLoRA add?"
- Target materials (also record the difference in scope between full context and the other methods): vector search, Tree and Graph use the 214 pages of the Lecture 01–03 main materials. Full context passes all 8 documents and 398 pages in `lectures.json` (369,491 characters), including the exercise materials and Lecture 05. Same question, one run per method. Raw traces: `lectures/05/runs/ex_*.txt` and `q1_baseline.txt` (vector search).

### Results by Method

| Method | Key points and correctness of the answer | Cited pages and evidence | Time (seconds) | Input/output tokens | Model responses | Estimated generation API cost (USD) |
|---|---|---|---|---|---|---|
| Full context | Correct: freezes original weights, trains two thin matrices, QLoRA adds 4-bit compression | p52 (translated p.75) | 3.25 | 95,824 / 212 | 1 | 0.029277 |
| Vector search | Correct: freezes W, trains A and B, QLoRA 4-bit, about 1/4 memory. Mentions bitsandbytes, which p52 names only as an exercise library | pp. 51–52 (hits: p52, p51, p47, p60, p61) | 4.69 | 3,439 / 169 | 2 | 0.001454 |
| Tree | Correct and most detailed (W frozen, A and B trained, under 1%, about 4 GB for 7B). Adds "4-bit NormalFloat", which is **not** in the materials | pp. 51–52 (opened full text of p52 only) | 10.28 | 9,442 / 367 | 5 | 0.003750 |
| Graph | Correct: freezes W, trains A and B, QLoRA 4-bit | pp. 51–52 (seed p52 visible; trace truncates the rest) | 5.13 | 5,190 / 241 | 2 | 0.002160 |

- Pages found by running search alone, and what their text confirmed: `uv run python -m app.retrieval "LoRA QLoRA difference"` returned p52 (LoRA and QLoRA), p51 (PEFT), p60 (exercise with QLoRA), p47 (RAG vs FT for knowledge), p61 (exercise steps). p52 alone states all three facts: original W frozen, only A and B trained, QLoRA stores W at 4 bits (about one quarter of memory, about 4 GB for 7B). p51 repeats it as a comparison. p60, p61 and p47 only share terms.
- Tool calls shown by `--trace` (names, arguments, counts, table-of-contents paths followed by Tree, etc.):
  - Vector: 1 call, `search_materials('LoRA freeze train QLoRA add')`.
  - Tree: 4 calls: root → `lec02-main` → section `lec02-main-s045` ("When and how to adapt the selected model") → page `lec02-main-p052`. It picked the right section from titles and opened only one page.
  - Graph: 1 call, `search_graph('LoRA freeze train QLoRA add Lecture 02')`, seed p52.
  - Full context: no tool calls, one model response.
- Examples where retrieved information was insufficient, or was retrieved but not used in the answer: no method missed the evidence. Vector search retrieved p60, p61 and p47, which were not used (correctly). Tree's "4-bit NormalFloat" is a gap filled from model knowledge despite the instruction to stay within the retrieved text. Full context cited only p52 although p51 also supports the answer.
- Method you would adopt for this use case, your reasons, and limitations of the comparison conditions: vector search. It gave a correct, grounded answer at the lowest cost (1/20 of full context) and with the fewest tokens. Tree is a good second when titles are well written, but it took 5 responses and 10 s and added an unsupported detail. Full context works at this size but costs about 20x and will hit input limits as materials grow. Limits: one question, one run each, and its evidence is concentrated on one page, which favours every method. The scopes differ (398 vs 214 pages).
- Observations and questions: a single-page fact question does not separate the methods; a question spanning sections (see the compaction/memory question in the homework) is a better test. Question: can Tree be told to open two candidate pages before answering, to reduce answers built from one page plus model knowledge?

## Homework

<!-- Completing any one of Basic, Implementation, or Advanced is sufficient. -->

- Level attempted: **Implementation**
- What you did (files, settings, or processing changed, or retrieval method designed):
  - `app/retrieval.py`: added `add_neighbor_pages()` and `search_with_neighbors()`. After normal vector search, each hit gets the N pages before and after it, using the reading order from `load_pages()`.
    - Neighbors come only from the same `document_id` (no crossing into another lecture).
    - No page is returned twice. A page that is itself a hit keeps its hit entry, rank and `distance`, so it is never relabelled as a neighbor.
    - Each hit is followed by its own neighbors. Every entry carries `retrieval: "search" | "neighbor"`; neighbors also carry `neighbor_of` and `offset` (-1 / +1). Text and citation metadata are included as for hits.
  - `app/config.py`: `RAG_NEIGHBOR_PAGES`, read from `AIE_RAG_NEIGHBORS` (default `0`). With 0 the hits are returned unchanged, byte for byte, so the baseline is the original retrieval.
  - `app/tools.py`: `search_materials` calls `search_with_neighbors`. The docstring was **not** changed, so the model sees the same tool description in both conditions.
  - `app/agent.py`: `--trace` lists every page `search_materials` returned (hit with distance, or neighbor of which hit) and the total characters, so added evidence and added noise can be read directly.
  - `app/retrieval.py` CLI: `--neighbors N` for search-only inspection.
  - `tests/test_neighbors.py`: 10 offline tests (no API key): window 0 is unchanged, order, no crossing documents, no duplicates, adjacent hits keep their rank, citation metadata, unknown pages, negative window, the real neighbors of `lec02-main-p052`, and the tool path. `uv run pytest -q`: 41 passed.
  - Graph mode still uses plain `search()` for its seeds, so it is unaffected.
- Comparison question and conditions held fixed (model, target materials, etc.):
  - Q1: "In Lecture 02, what does LoRA freeze and what does it train? What does QLoRA add?" (evidence: `lec02-main-p051`, `p052`)
  - Q2: "In the Lecture 03 examples, how does compaction differ from memory across sessions? Do all daily notes go into long-term memory?" (evidence: `lec03-main-p013`, `p039`, `p040`)
  - Fixed: model `gemini-3.5-flash-lite`, bundled `index.sqlite3` (214 pages, Lectures 01–03 main), `RAG_TOP_K = 5`, `INSTRUCTIONS` and tool docstring. Only `AIE_RAG_NEIGHBORS` changed (0 → 1). One run per condition.
  - Raw `--trace` output: `lectures/05/runs/` (q1_baseline, q1_neighbors1, q2_baseline, q2_neighbors1).
- Results (answers and evidence before/after, `--trace` output, time, token counts, estimated generation API cost, etc.):

| Question | Neighbors | Pages returned (hits + neighbors) | Characters returned | Time (s) | Input / output tokens | Model responses | Est. generation cost (USD) | Answer |
|---|---|---|---|---|---|---|---|---|
| Q1 LoRA/QLoRA | 0 | 5 (5 + 0) | 5,844 | 4.69 | 3,439 / 169 | 2 | 0.001454 | Correct: freezes W, trains A and B, QLoRA adds 4-bit weights. Cites pp. 51–52 |
| Q1 LoRA/QLoRA | 1 | 11 (5 + 6) | 11,464 | 7.67 | 5,578 / 169 | 2 | 0.002096 | Correct, same content, adds "about 4 GB for 7B" (from p52, a hit in both runs). Cites pp. 51–52 |
| Q2 Compaction/memory | 0 | 5 (5 + 0) | 3,929 | 3.44 | 2,976 / 246 | 2 | 0.001508 | Correct on both parts. Cites p13, p39, p40, p65 |
| Q2 Compaction/memory | 1 | 11 (5 + 6) | 8,084 | 5.49 | 4,978 / 260 | 2 | 0.002143 | Correct on both parts. Cites p39, p40, p65 (no longer cites p13) |

  - Change with neighbors: input tokens +62% (Q1) and +67% (Q2), estimated cost +44% and +42%, time +2–3 s. Answers did not become more correct.
  - Neighbors added — Q1: p053 (what to fine-tune for a chatbot), p050 (decision sequence), p059 (Lecture 2 summary), p046, p048 (FT vs continued pre-training), p062 (next lecture preview). Q2: p041 (Skill), p064, p066 (supplements), p037 (Part 6 title page), p012 (loop), p014 (agent = model + harness). None of them was needed for the answer.
- Examples of improvements and remaining failures or limitations:
  - **No improvement on these two questions, because the baseline already found every evidence page.** With `RAG_TOP_K = 5`, p051 and p052 (Q1) and p013, p039 and p040 (Q2) were all direct hits. In Q2, p039 and p040 are adjacent and both were hits, so dedupe kept them as hits instead of adding them twice.
  - **Unnecessary information increased in every case**: 12 neighbor pages across the two questions, all off-target (section title pages, summaries, next-lecture previews, supplements). This is the cost side: about 2,000 extra input tokens per question.
  - Where it should help: when only one page of a multi-page explanation is a hit (e.g. p040 found without p039), or when top-k is smaller. I did not show such a case here; that is the next test (e.g. `RAG_TOP_K=2` with and without neighbors).
  - Confound: the model wrote a slightly different search query in each run (Q1: "LoRA freeze train QLoRA add" vs "LoRA freeze train QLoRA"), so distances and hit order changed a little. The hit **set** was the same in both Q1 runs and both Q2 runs, so the comparison is still about the neighbors.
  - Practical issue: my Codespace's default Python 3.14 has no `sqlite3.enable_load_extension`, so vector search crashed (`AttributeError`). Rebuilding the venv with uv-managed Python (`UV_PYTHON_PREFERENCE=only-managed uv sync --frozen --python 3.14`) fixed it. Two runs also hit HTTP 503 and were re-run.
- Observations and questions:
  - Fixed ±1 expansion is a blunt tool: it doubles the context whether or not the neighbors are related. A better version would add a neighbor only if it is in the same section as the hit, or only if its own distance to the query is below a threshold, or would let the model ask for neighbors with a separate `read_adjacent(page_id)` tool so it pays the cost only when a page looks cut off.
  - Question: for slide-style materials (one idea per page), is page-level adjacency the right unit at all, or would section-level expansion (Tree) be the better way to recover context?
