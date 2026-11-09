# Lecture 03 homework (Advanced a): ADK runs

Model: `gemini-3.5-flash-lite`

## What are the 3 homework levels in the AIE2026 course?

```text
In the AIE2026 course, the three homework levels are:

1. **Basic**: Review lecture content.
2. **Implementation**: Write your own code.
3. **Advanced**: Research and experimentation.

*(Note: Completing any one of these levels fulfills the homework requirement for that lecture, and as a rule, it is not graded.)*

(Lecture 01)

--- trace ---
[tool call]   search_glossary({'query': 'homework levels'})
[tool return] search_glossary -> {'result': '[{"term": "3 homework levels", "lecture": 1, "definition": "The structure of AIE2026 homework. There are thr…
[usage] model responses with usage=2, total_tokens=1335
```

## What is the difference between LoRA and QLoRA?

```text
To understand the difference between **LoRA** and **QLoRA**, let's look at how each handles model weights and memory:

- **LoRA (Low-Rank Adaptation):** This is a Parameter-Efficient Fine-Tuning (PEFT) method where the pretrained model weights are frozen, and weight updates are represented as a low-rank product of two small matrices. Only these small matrices (adapters) are trained, which significantly reduces the number of trainable parameters and storage space.
- **QLoRA (Quantized LoRA):** This method builds upon LoRA by further saving memory. It achieves this by **quantizing** the base-model weights down to a lower bit-width (such as 4-bit) before applying LoRA. This allows much larger models to fit into and be trained on smaller GPUs.

Think of LoRA as focusing on training fewer parameters through low-rank decomposition, while QLoRA adds precision reduction (quantization) to the base model weights to drastically lower memory usage during training.

Lecture 02

--- trace ---
[tool call]   search_glossary({'query': 'LoRA'})
[tool call]   search_glossary({'query': 'QLoRA'})
[tool return] search_glossary -> {'result': '[{"term": "LoRA", "lecture": 2, "definition": "A PEFT method that freezes pretrained weights, represents wei…
[tool return] search_glossary -> {'result': '[{"term": "QLoRA", "lecture": 2, "definition": "A method that saves memory by quantizing base-model weights …
[usage] model responses with usage=2, total_tokens=1873
```

## Give me one review question from Lecture 02

```text
Here is a review question from Lecture 02:

**Question:** What does "Epoch" mean?

Give it your best try! Let me know your answer, and we can check it together. 

(Lecture 02)

--- trace ---
[tool call]   make_quiz({'lecture': 2})
[tool return] make_quiz -> {'result': '{"lecture": 2, "term": "Epoch", "question": "What does \\"Epoch\\" mean?", "answer": "One pass through the e…
[usage] model responses with usage=2, total_tokens=1233
```

## What is the difference between RAG and fine-tuning?

```text
When comparing **Fine-tuning** and methods like RAG (Retrieval-Augmented Generation), it helps to look at what each approach is best designed to achieve.

According to our glossary:
* **Fine-tuning** is defined as further training a pretrained model on data suited to a specific task or format. It is particularly suitable for teaching output format, tone, or behavior in a specific domain. However, for up-to-date facts, consulting external data through tools or RAG is often more suitable.
* Regarding **RAG**, the term itself is not in the glossary, but we can understand it conceptually as a technique that retrieves external knowledge dynamically rather than baking facts directly into the model's weights through training.

To think about when to use which: consider whether you need to change *how* the model speaks and behaves (like its style or formatting) versus supplying it with *new or changing facts* that it hasn't seen before. 

(Lecture 02)

--- trace ---
[tool call]   search_glossary({'query': 'RAG'})
[tool call]   search_glossary({'query': 'Fine-tuning'})
[tool return] search_glossary -> {'result': '[{"term": "Token", "lecture": 1, "definition": "The smallest unit an LLM uses to process text. Text is split…
[tool return] search_glossary -> {'result': '[{"term": "Fine-tuning", "lecture": 2, "definition": "Further training a pretrained model on data suited to …
[tool call]   search_glossary({'query': 'RAG'})
[tool return] search_glossary -> {'result': '[{"term": "Token", "lecture": 1, "definition": "The smallest unit an LLM uses to process text. Text is split…
[tool call]   search_glossary({'query': 'Retrieval-Augmented Generation'})
[tool return] search_glossary -> {'result': "The term 'Retrieval-Augmented Generation' was not found in the glossary."}…
[usage] model responses with usage=4, total_tokens=4703
```
