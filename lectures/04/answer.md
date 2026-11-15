# Lecture 04 Answers

## Exercises

- Agreement by criterion (before revision): Grounding / , Scope / , Hint / , Clarity / , Lecture marker /
- Number of items needing review (before revision):
- Criterion revised and the policy added:
- Agreement by criterion and number of review items (after revision):
- Items where your labels differed from the instructor's, and your reasons:
- Observations and questions:

## Homework

- **Level attempted:** Advanced (one benchmark dataset, no code)
- **Dataset:** SWE-bench Verified
  - Dataset: https://huggingface.co/datasets/princeton-nlp/SWE-bench_Verified
  - Construction: OpenAI, "Introducing SWE-bench Verified" (2024-08-13): https://openai.com/index/introducing-swe-bench-verified/
  - Follow-up audit: OpenAI, "Why SWE-bench Verified no longer measures frontier coding capabilities" (2026-02-23): https://openai.com/index/why-we-no-longer-evaluate-swe-bench-verified/
  - Original benchmark: Jimenez et al., "SWE-bench: Can Language Models Resolve Real-World GitHub Issues?" (ICLR 2024, arXiv 2310.06770)
- **AI tools:** research and drafting with Claude. Every figure below was cross-checked against the two OpenAI posts and the dataset card linked above. Items were read in public mirrors of the Verified split (Harbor / terminal-bench task registries), because the Hugging Face viewer needs a login.

### What an item looks like

Each item is one resolved GitHub issue from one of 12 open-source Python repositories. The agent gets the issue text (`problem_statement`) and the repository at `base_commit`, and must edit the code. It never sees the tests. Hidden fields hold the gold patch, the test patch from the original PR, and two test lists: `FAIL_TO_PASS` (fail before the fix, must pass after) and `PASS_TO_PASS` (must keep passing, i.e. no regressions).

### Items I read (summaries, not copies)

| Item | What it asks | Could I solve it? | What is hard for an LLM |
|---|---|---|---|
| `django__django-11099` | Username validators use `^...$`, and Python's `$` also matches a trailing newline, so `"alice\n"` is accepted. Fix the two validators | Yes, quickly. The issue even proposes the fix (`\A...\Z`) | Almost nothing: the fix is in the issue text. This is the "easy, under 15 minutes" end of the set |
| `psf__requests-2317` | On Python 3, `builtin_str(method)` turns `b'GET'` into the literal string `"b'GET'"`, so the server returns 404. Make `requests` accept a bytes method | Yes, with some reading of `compat.py` and `sessions.py` | The bug only exists on Python 3 (the reporter says 2.6 works), so the model must reason about str/bytes across versions and pick a fix that the hidden test (a request with `b"GET"`) accepts |
| `sympy__sympy-20590` | `Symbol` uses `__slots__`, yet since 1.7 instances have a `__dict__`. The reporter suspects a parent class dropped `__slots__` | Probably, after walking the class hierarchy | Localisation: the symptom is on `Symbol`, the cause is in a mixin somewhere up the MRO. The issue does not name the file |
| `astropy__astropy-12907` | `separability_matrix` is correct for `A & B & C` but wrong when the same model is nested as `A & (B & C)` | Only with real time in the code: I would need to understand how `_cstack` builds the coordinate matrix | Deep domain logic. The gold fix is a one-line change in `astropy/modeling/separable.py`, but finding which line requires reasoning about matrix stacking, not pattern matching |

Also read, as the counter-example: `scikit-learn__scikit-learn-14520`, which OpenAI cites as a task that was **removed**. Its hidden test expects a specific deprecation message that the issue text never mentions, so a correct fix can still fail. This is a "narrow test".

### Who built it and how

| Step | People | Method |
|---|---|---|
| 1. Original SWE-bench (2023) | Princeton NLP authors; the issues and fixes were written by the real maintainers and contributors of the 12 repositories | Automatic mining of merged PRs that close an issue and change tests; kept only items whose tests fail before and pass after the PR. 2,294 test items |
| 2. Annotator onboarding | OpenAI engineers | Hand-labelled 50 samples to high confidence and used them as an entry test; annotators had to pass it |
| 3. Screening (2024) | **93** professional developers experienced in Python | 1,699 random samples, **3 annotators per sample**. Each sample scored 0 to 3 on: is the issue underspecified, and do the `FAIL_TO_PASS` tests reject valid solutions. Plus a difficulty estimate (time for a developer) and a free-text flag for other problems |
| 4. Aggregation and filtering | (rule) | Conservative ensemble: take the **highest** severity of the 3 annotators. Drop the sample if either main criterion is 2 or 3. 38.3% flagged as underspecified, 61.1% as having unfair tests, **68.3% removed** in total. 500 kept (196 "easy" under 15 min, 45 "hard" over 1 h) |
| 5. Grading | (code) | Execution-based: apply the model's patch in a Docker environment, run `FAIL_TO_PASS` and `PASS_TO_PASS`. Resolved only if both sets pass. No LLM and no human in the grading loop |
| 6. Audit (2026) | At least 6 experienced engineers per item, flagged issues re-checked by another team | 138 items that o3 did not solve consistently over 64 runs. **59.4%** of those 138 had material flaws: narrow tests 35.5%, wide tests (checking behaviour the issue never asks for) 18.8%, other 5.1%. Frontier models could also reproduce gold patches or problem text for some items (contamination). OpenAI stopped reporting the score and recommends SWE-bench Pro |

### How it differs from today's evaluation set

| | Today's set (`lec04_cases.jsonl`) | SWE-bench Verified |
|---|---|---|
| Purpose | Check whether the **grader** (LLM judge) can be trusted | Measure the **agent's** coding ability |
| Size | 10 items | 500 items (from 1,699 screened, from 2,294) |
| Who wrote the items | 1 instructor, generated with the Lecture 03 agent | Real GitHub users and maintainers (issues and fixes); OpenAI and Princeton curated them |
| Validators per item | 1 instructor label + 1 student label, compared on purpose to show human disagreement | 3 trained annotators (onboarding test, max-severity ensemble); later ≥6 in the audit |
| Items with known problems | Kept on purpose (deliberate failures, edge cases) because they test the grader | Removed (68.3%), because a broken item makes the agent's score wrong |
| Ground truth | Glossary entries + expected behaviour text | Gold patch + hidden unit tests |
| Grading | Human T/F/unsure + LLM judge on 4 criteria, code for the "Lecture N" marker | Code only: run the tests |
| What "unsure" becomes | Human review; the policy is then written into `rubric.md` ("Unresolved Questions") | Severity 2 or 3 → item discarded before release |
| Contamination | Private, fresh, course-specific | Public GitHub history; models have seen some items |

### Observations and questions

- **Code grading is not automatically objective.** In this exercise the "Lecture N" marker goes to code because it is a string check. SWE-bench pushes the whole judgment into code, and the 2026 audit shows the code (the tests) can be wrong in the same two ways as an LLM judge: a narrow test is a false alarm (correct answer rejected), and a wide test is a criterion that was never in the spec. That second one is the same problem as our Clarity criterion, which is not in `INSTRUCTIONS`.
- **Three expert reviewers with a max-severity rule still missed a lot.** Screening dropped 68% of the items, yet 59.4% of the 138 hardest survivors were still flawed. The 138 were chosen because o3 failed them, so 59.4% is not the flaw rate of the whole set, but it shows that a failure on a hard item is as likely to be a bad item as a weak model. Lesson for our set: when the agent "fails", check the label first.
- **The max-severity ensemble is a policy I could reuse.** With several human labellers on our 10 items, "any labeller says F" is a conservative rule, and the cost is lower coverage. It is the same trade-off as our unsure → human review path.
- **A benchmark has a lifespan.** Verified lasted about 18 months before contamination and saturation (74.9% → 80.9% over six months) made it uninformative. The items I read are mirrored widely with "should never appear in training corpora" canary strings, which tells me the text is already everywhere. Our private, regenerable set does not have this problem, but it also has only one author.
- **Question:** if an LLM judge were used on SWE-bench (reading the patch instead of running tests), would it catch the narrow-test cases that execution grading gets wrong, or would it add its own false passes? That would be a direct test of what today's exercise measures.
