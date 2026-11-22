# Lecture 05 Answers

## Exercises

- Answering model (`[model]` shown during execution):
- Comparison question:
- Target materials (also record the difference in scope between full context and the other methods):

### Results by Method

| Method | Key points and correctness of the answer | Cited pages and evidence | Time (seconds) | Input/output tokens | Model responses | Estimated generation API cost (USD) |
|---|---|---|---|---|---|---|
| Full context | | | | | | |
| Vector search | | | | | | |
| Tree | | | | | | |
| Graph | | | | | | |

<!-- State when a method was not run or a cost was unavailable. Use a separate table for each additional question. -->

- Pages found by running search alone, and what their text confirmed:
- Tool calls shown by `--trace` (names, arguments, counts, table-of-contents paths followed by Tree, etc.):
- Examples where retrieved information was insufficient, or was retrieved but not used in the answer:
- Method you would adopt for this use case, your reasons, and limitations of the comparison conditions:
- Observations and questions:

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
