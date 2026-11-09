# Lecture 02 Answers

## Exercises

- **Model and settings used** (from `config` in `result.json`): `Qwen/Qwen3.5-0.8B` at revision `2fc06364715b967f1860aea9cf38778875588b17`, LoRA without quantization, `lora_r` 16, `lora_alpha` 32, `lr` 2e-4, 20 epochs (40 steps), warmup 6, seed 42, greedy generation (`do_sample: False`). Colab T4 (15 GB), torch 2.14.1+cu130, transformers 5.18.0, peft 0.21.1, trl 1.14.2. Trainable parameters: 6,389,760.
- **Did you run training yourself** (`executed_training_myself`): Yes. I ran the whole notebook, sections 0 to 8, on a Colab T4. Training took 200 s. Loss went 1.696 (step 10), 0.066 (step 20), 0.018 (step 30), 0.015 (step 40).
- **Before training**: `format_rate` = 0.952 / `content_rate` = 0.381
- **After training**: `format_rate` = 1.000 / `content_rate` = 0.905
- **Questions that regressed**: none.
- **Failures remaining after training and their types** (2 of 21):
  - *Evasion through a confirmation request despite evidence being present*: "Can I submit a format other than PDF?" The FAQ says to submit one PDF, so the answer is "no". The tuned model answered with the "not in the FAQ, confirmation needed" template and `needs_review: true`. Before training it answered "No ... PDF" correctly but with the wrong flag.
  - *Assertion without evidence*: "Do office hours require an appointment?" The FAQ says nothing about appointments. The tuned model copied the office-hours sentence verbatim with `needs_review: false`. It matched on the words "office hours" and reused that FAQ item.
- **Results of knowledge questions** (section 6, before → after):

  | Question | In FAQ | Before | After |
  |---|---|---|---|
  | When is the final assignment deadline for this course? | No | asserted | asserted |
  | What is the instructor's name? | No | needs_review | needs_review |
  | What is the topic of the next lecture? | No | needs_review | needs_review |
  | When is the assignment deadline? (control) | Yes | asserted (correct) | asserted (correct) |

  Training did not fix the one fabrication. "Final assignment deadline" is close in wording to the FAQ's "assignment deadline", so both models answered September 30 with `needs_review: false`. After training the answer is the exact FAQ sentence, so it looks more authoritative while still wrong. The two questions with no word overlap with the FAQ were flagged correctly both before and after. On this data, whether the model asks for review depends on how close the question's wording is to an FAQ item, not on whether the FAQ actually answers it.
- **What changed and what stayed the same with training**:
  - Changed: the output style. Answers became the FAQ sentences copied verbatim (before training they were short paraphrases such as "Tuesday from 17:00 to 18:00"). Ungrounded questions now get the exact trained refusal sentence. The `needs_review` flag became much more consistent: grounded questions wrongly flagged `true` went from 7 of 15 to 1 of 15 (the PDF case), and ungrounded questions correctly flagged `true` went from 2 of 6 to 5 of 6. Generation also got faster (49.9 s → 37.9 s for 21 questions) because answers are short and stop cleanly.
  - Stayed the same: the model's judgment about whether the FAQ supports an answer. It still decides by word overlap. A wrong answer in the trained style is harder to spot because it looks exactly like a correct one.
  - Note on the starting point: format compliance was already 0.952 before training with the English prompt. The slides (Japanese run) expected many missing `needs_review` keys. In this English run, most of the improvement came from content, not format.
- **Section 8 (4-bit, no training)**: weight memory 3.01 GB → 0.76 GB. `format_rate` 0.952 → 1.000, but `content_rate` 0.381 → 0.048. The 4-bit model set `needs_review: true` on all 21 questions, answered all three "where do I submit" questions with the deadline sentence, and gave bare "Yes"/"No" to questions the FAQ does not cover. I got the same 4-bit outputs in two separate sessions, so the effect is repeatable with greedy decoding. This differs from the original Japanese run (string `"false"`), so the direction of quantization error is not predictable in advance and has to be measured.

## Homework

- **Level attempted:** Basic and Implementation (Implementation is the highest). All runs were on a Colab T4 with seed 42 and greedy generation. Each run used a fresh runtime, and I deleted the runtime after downloading the files.

### Basic: `num_train_epochs` 20 → 5

- **Settings changed:** only `num_train_epochs` (20 → 5, so 40 → 10 steps). Everything else as in the exercise.
- **Results:**

  | Setting | format_rate | content_rate | Final loss | Training time | Regressions |
  |---|---|---|---|---|---|
  | Before training (same for both) | 0.952 | 0.381 | - | - | - |
  | 20 epochs (exercise) | 1.000 | **0.905** | 0.015 (step 40) | 200 s | none |
  | 5 epochs | 1.000 | 0.714 | 1.714 (step 10) | 48 s | "When will grades be released?" |

  | Question group (test) | Before | 5 epochs | 20 epochs |
  |---|---|---|---|
  | Grounded, content correct (of 15) | 7 | **15** | 14 |
  | Ungrounded, content correct (of 6) | 1 | **0** | 5 |

- **Observations:**
  1. **The format is learned almost immediately.** With 5 epochs, format compliance was already 100% and every grounded question was answered with the FAQ sentence and `needs_review: false`, even though the loss was still 1.71. The loss is averaged over all tokens, so it says little about whether the short JSON structure has been learned.
  2. **The refusal behaviour needs much more training.** With 5 epochs, none of the 6 ungrounded questions passed. The model never produced the trained refusal sentence. Instead it answered in the trained style: "No, lecture recordings are not made available", "Yes, feedback is provided during office hours". These are fabrications with `needs_review: false`. Only 4 of the 14 training examples are refusals, so the model learns the majority pattern ("copy an FAQ sentence, flag false") first. It needed 20 epochs to learn the minority pattern.
  3. **Undertraining created a new fabrication.** The one regression: before training the model said "Confirmation is needed" for "When will grades be released?". After 5 epochs it answered "Grades are released on the last day of the semester, which is September 30 at 23:59". It took the deadline from the FAQ and attached it to a different question. A partly trained model can be worse than the base model on exactly the cases where caution matters.
  4. **More training also over-generalises.** With 20 epochs, "Can I submit a format other than PDF?" (grounded) was refused with the "not in the FAQ" template. 5 epochs answered it correctly. So 20 epochs is not better on every question.
  5. **Cost:** 5 epochs took a quarter of the time (48 s vs 200 s). The deciding question is which error is acceptable: 5 epochs never refuses, 20 epochs refuses most of the time and sometimes over-refuses.

### Implementation: own topic, fictional office IT helpdesk FAQ

- **Data changed:** I replaced the course FAQ with a fictional 5-item office IT helpdesk FAQ: staff Wi-Fi (SSID `NW-Staff`), VPN (`CorpVPN` client plus authenticator code), password expiry (90 days, self-service portal), incident tickets (Helpdesk app, urgent extension 4357) and guest Wi-Fi (code from reception, valid 24 hours). I chose this because it is close to my own work as a network architect. The JSON format, the `needs_review` design, the split sizes (train 14 / valid 7 / test 21), CONFIG and the evaluation code are unchanged. I also changed the first sentence of `SYSTEM` ("office IT helpdesk FAQ questions"), the refusal sentence ("Confirmation from the IT helpdesk is needed", still containing "Confirmation" for scoring) and the 3 knowledge questions in section 6. Section 8 was not rerun for this topic.
- **How I prepared the "ungrounded" questions** (12 in total: 4 train, 2 valid, 6 test):
  1. **Near misses (8):** each uses the vocabulary of one FAQ item but asks for a fact that item does not state. Examples: "What is the VPN server address?", "What are the password complexity rules?", "Is there staff Wi-Fi in the parking garage?", "Do visitors need to show ID to get a guest code?". These are the hardest case because word overlap with the FAQ is high.
  2. **General-knowledge traps (4, test only):** questions where a model can answer from pretraining even though the FAQ is silent, for example "What port does the VPN use?" (a model could say 443) and "Is the guest Wi-Fi network encrypted?".
  3. **Knowledge questions (section 6):** "Who is the head of IT at this company?", "When is the next scheduled network maintenance?", "What is the IP address of the main firewall?" (to see whether it invents a private IP), plus "How often must I change my password?" as the in-FAQ control.
  4. I checked that every required keyword in `gold` appears in the FAQ sentence, and that no question appears in more than one split (the notebook's assert passed: train=14 valid=7 test=21).
- **Results:**

  | | format_rate | content_rate | Grounded correct (of 15) | Ungrounded correct (of 6) | Loss (step 10 → 40) | Training time |
  |---|---|---|---|---|---|---|
  | Before training | 0.952 | 0.143 | 3 | 0 | - | - |
  | After training (20 epochs) | 1.000 | **0.905** | 14 | 5 | 1.979 → 0.014 | 220 s |

  Regressions: none. Section 6: all 3 knowledge questions were flagged `needs_review` both before and after training (after training with the exact refusal sentence). The control was answered correctly both times. The model did not invent a firewall IP.

- **What training fixed:** before training, the base model gave several confident, risky answers to ungrounded questions: "Yes, you can reset a colleague's password for them", "No, visitors do not need to show ID", "No" (staff Wi-Fi in the garage). For a helpdesk, the first one is a security problem. After training, 5 of the 6 were refused correctly. Before training it also gave bare values ("4357", "Reception") or flagged correct answers for review (8 of 15 grounded answers had `needs_review: true`). After training these became full FAQ sentences with the right flag.
- **Failures remaining after training (2 of 21):**
  - *Assertion without evidence:* "Do visitors need to show ID to get a guest code?" The model copied the guest Wi-Fi sentence with `needs_review: false`. This is the same failure type as "Do office hours require an appointment?" in the exercise: a near-miss question that shares words with one FAQ item.
  - *Wrong FAQ item for a grounded question:* "How do I work remotely on the company network?" was answered with the staff Wi-Fi sentence instead of the VPN sentence. The training paraphrase was "access the company network from home"; "work remotely" was not matched to it, but "company network" pulled it towards Wi-Fi.
  - The general-knowledge traps did not trigger. Even before training, the model said the FAQ does not give the VPN port.
- **Comparison with the course FAQ:** the starting content accuracy was lower on my topic (0.143 vs 0.381). The IT FAQ has more facts per sentence (SSID, client, second factor), and the base model often answered with only one of them ("4357", "Reception"), which fails the keyword check. After training both topics reached the same 0.905, with the same type of remaining error. The pattern repeats across domains.

### Discussion: when fine-tuning is and is not suitable

My results from three training runs on two topics:

- **Fine-tuning works well for the output contract.** Format went to 100% in all three runs, even after 10 steps. A fixed JSON schema, a fixed refusal sentence, a house style, a classification label: these are good uses of LoRA, especially on a small model that must run cheaply.
- **Fine-tuning does not teach the model whether the evidence supports the answer.** In every run the remaining failures were near-miss questions: the model matched words to an FAQ item and asserted it. Training made these errors look more authoritative, because they use the exact FAQ wording. Undertraining (5 epochs) made it worse and produced new fabrications.
- **Fine-tuning is the wrong place to store facts that change.** The FAQ facts were learned verbatim, so a changed deadline or extension number would need retraining, and the old value would still be in the adapter. For changing knowledge, retrieval (the glossary search agent in Lecture 03) is better: update the document, not the weights, and the answer can cite its source.
- **In practice I would combine them:** retrieval for the facts, a small fine-tune (or a strong prompt) for the output format, and a check outside the model for the risky decision. For example, `needs_review` should be set by code when retrieval finds no supporting passage above a similarity threshold, not by the model's own judgment. In an IT or security context, an answer like "Yes, you can reset a colleague's password" must never depend on the model alone.
- **Measurement matters.** Training loss did not predict behaviour (loss 1.71 already gave 100% format). The before/after evaluation split by grounded and ungrounded questions was what showed the real trade-off. I would not ship a fine-tuned model without that kind of test set.

### What I verified myself

All three notebooks were trained in my own Colab account on a T4 (`executed_training_myself: True`); the result files in this folder are the unmodified downloads. I used an AI assistant (Claude) to prepare the Basic and Implementation notebooks, to write the IT FAQ and questions, to operate Colab in my browser for the runs, and to draft this file. The counts above were computed from `eval_before.json` and `eval_after.json`.

Files in this folder: `exercise_ep20/`, `basic_ep5/`, `impl_it_helpdesk/` (each with `result.json`, `eval_before.json`, `eval_after.json`; the first two also have `eval_before_4bit.json`), and the two homework notebooks.
