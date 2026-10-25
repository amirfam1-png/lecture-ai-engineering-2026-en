# Lecture 01 Answers

## Exercises

- Model's answer to the course-specific question (the 3 homework levels; a summary is fine):
  `gemini-3.5-flash-lite` said in all 3 runs that it had no information about the AIE2026 course and asked for the syllabus. `gemini-3.8-flash` confidently described 3 invented levels (Core/Baseline, Extension or Stretch, and a Deployment "Hero" or "Boss Mode" level), attributing them to the "AI Makerspace" bootcamp.
- What you noticed when comparing it with the correct meaning in the glossary:
  The correct levels (`homework-levels` in `data/glossary.json`) are Basic (review lecture content), Implementation (write your own code) and Advanced (research and experimentation), and any one level completes the homework. Neither model got this right. Flash-lite refused honestly; 3.8-flash produced a detailed, plausible but wrong answer. Its level names do not match, and it misses the key rule that one level is enough.
- Token counts you displayed (input / output): not done. I chose the Basic level and did not modify `app/ask.py`.

## Homework

- **Level attempted:** Basic
- **What you did:**
  Ran the default course-specific question ("What are the 3 homework levels in the AIE2026 course?") 3 times on each of 2 models, switching with the `AIE_MODEL` environment variable, with a 15 s pause between calls to stay within free-tier limits. Raw output is saved in `lectures/01/runs.txt`.
  - `gemini-3.5-flash-lite` (default)
  - `gemini-3.8-flash` (higher tier)
  - I did not change temperature: the course notes say the parameter was deprecated by Google on 2026-07-21 and may be ignored.
- **Results:**

| Model | Run 1 | Run 2 | Run 3 |
|---|---|---|---|
| gemini-3.5-flash-lite | "No information", asks for syllabus | Same, also states a January 2025 knowledge cutoff and guesses the course may be "AI in Education" | Same refusal, suggests pasting from Canvas or Moodle |
| gemini-3.8-flash | Invents 3 levels (Core, Extension/Experimentation, Deployment "Hero"), adds a hedge at the end | 503: model busy | Invents 3 levels (Core, Stretch/Advanced, "Boss Mode"/Production) |

- **Observations and questions:**
  1. **Same question, different answers.** Flash-lite gave the same conclusion every time but with different wording and different extra details (only run 2 mentioned a knowledge cutoff). 3.8-flash kept the same overall structure but changed the level names and details between runs ("Hero" vs "Boss Mode", "Extension" vs "Stretch").
  2. **The stronger model was more confidently wrong.** The lighter model admitted it did not know; the higher-tier model hallucinated a detailed answer, likely matching "AIE" to a similarly named bootcamp it saw in training. A plausible, well-formatted answer is not evidence of correctness, so course-specific facts need grounding in the course's own data (the glossary search agent planned for Lecture 03).
  3. **Free-tier reliability.** 1 of 3 calls to `gemini-3.8-flash` failed with 503. For a real application this means retries and a fallback model are part of the design, not an afterthought.
  4. **Question:** with only 3 runs per model this is anecdotal. How many runs would be needed to measure the refusal vs hallucination rate reliably?
