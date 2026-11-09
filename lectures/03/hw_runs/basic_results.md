# Lecture 03 homework (Basic): live results

Model: `gemini-3.5-flash-lite`

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

## Full answers

### E0 baseline | What are the 3 homework levels in the AIE2026 course?

Change: no change

```text
In the AIE2026 course, the homework is structured into three distinct levels so you can choose the one that best fits your current goals and schedule:

1. **Basic**: Focuses on reviewing the lecture content.
2. **Implementation**: Involves writing your own code.
3. **Advanced**: Involves research and experimentation.

As a rule, completing any one of these levels fulfills the homework requirement for that lecture, and assignments are generally not graded. 

*(Lecture 01)*

--- trace ---
[tool call] search_glossary({'query': 'homework levels'})
[usage] requests=2 in=1419 out=126
```

### E0 baseline | Give me one review question from Lecture 02

Change: no change

```text
Here is a review question from Lecture 02:

**Question:** What does "QLoRA" mean?

Give it a try, and let me know your answer! (Once you're ready, I can reveal the answer.)

Relevant session: Lecture 02

--- trace ---
[tool call] make_quiz({'lecture': 2})
[usage] requests=2 in=1415 out=72
```

### E0 baseline | What is a lecNN-start tag in the AIE2026 course?

Change: no change

```text
A **lecNN-start tag** is a Git tag placed on the starting code for each lecture's exercises in the AIE2026 course repository (for example, `lec03-start`). It allows you to create a fresh branch and start the current lecture's exercises even if you haven't finished the previous lecture.

(Lecture 1)

--- trace ---
[tool call] search_glossary({'query': 'lecNN-start'})
[usage] requests=2 in=1419 out=97
```

### E0 baseline | What is the difference between LoRA and QLoRA?

Change: no change

```text
To understand the difference between **LoRA** and **QLoRA**, let's look at how they handle the base model weights:

* **LoRA (Low-Rank Adaptation):** Freezes the pretrained model weights and adds small, trainable low-rank matrices (adapters) to approximate weight updates. However, the base model itself is typically loaded in standard precision (e.g., FP16 or BF16), which still requires significant GPU memory for large models.
* **QLoRA (Quantized LoRA):** Extends LoRA by quantizing the base-model weights down to a lower precision (such as 4 bits). It keeps the base model in this highly compressed format while training the LoRA adapters, allowing you to fine-tune much larger models on more limited GPU hardware.

Think about how model memory consumption changes when you reduce the precision of the base weights before applying your trainable low-rank adapters.

Lecture 02

--- trace ---
[tool call] search_glossary({'query': 'LoRA'})
[tool call] search_glossary({'query': 'QLoRA'})
[usage] requests=2 in=1805 out=235
```

### E0 baseline | Briefly explain PEFT, LoRA, QLoRA and quantization.

Change: no change

```text
Here is a brief overview of these concepts based on the course glossary:

* **PEFT (Parameter-Efficient Fine-Tuning):** An umbrella term for methods that train only a small subset of model parameters or a small set of added parameters instead of all parameters, greatly reducing GPU memory and storage requirements.
* **LoRA (Low-Rank Adaptation):** A popular PEFT method that freezes the pretrained weights and represents weight updates as a low-rank product of two small matrices, training only those small matrices.
* **Quantization:** A technique for representing model weights with fewer bits (for example, from 16 bits down to 4 bits) to reduce memory usage and computational cost, with a possible minor trade-off in accuracy.
* **QLoRA:** A method that combines quantization and LoRA by quantizing the base model's weights to a lower bit-width (such as 4 bits) and then training using LoRA, allowing much larger models to fit into smaller GPU memory.

(Relevant Session: Lecture 02)

--- trace ---
[tool call] search_glossary({'query': 'PEFT'})
[tool call] search_glossary({'query': 'LoRA'})
[tool call] search_glossary({'query': 'QLoRA'})
[tool call] search_glossary({'query': 'quantization'})
[usage] requests=2 in=2101 out=292
```

### E0 baseline | What is the difference between RAG and fine-tuning?

Change: no change

```text
The main difference lies in how they incorporate new information and their primary use cases:

- **Fine-tuning** involves further training a pretrained model on data suited to a specific task or format. It is best used for teaching output format, tone, or behavior in a specific domain.
- **RAG** (Retrieval-Augmented Generation) is not in the glossary, but generally in the context of our course, when dealing with up-to-date facts or external data, consulting external sources (like RAG or tools) is typically more suitable than fine-tuning.

To help you think about this further, consider: *If you need the model to adopt a specific company tone versus instantly retrieving the latest product inventory numbers every day, which approach would fit each scenario best?*

(Lecture 02)

--- trace ---
[tool call] search_glossary({'query': 'RAG'})
[tool call] search_glossary({'query': 'fine-tuning'})
[tool call] search_glossary({'query': 'RAG'})
[usage] requests=3 in=3288 out=223
```

### E1 no-always-search | What is a lecNN-start tag in the AIE2026 course?

Change: INSTRUCTIONS: deleted "Always check the glossary with search_glossary ..."

```text
A `lecNN-start` tag is a Git tag placed on the starting code for each lecture's exercises in the AIE2026 course repository (for example, `lec03-start`). It allows you to create a fresh branch and start the current lecture's exercises even if you haven't finished the previous lecture.

Lecture 01

--- trace ---
[tool call] search_glossary({'query': 'lecNN-start'})
[usage] requests=2 in=1377 out=96
```

### E1 no-always-search | What is the difference between LoRA and QLoRA?

Change: INSTRUCTIONS: deleted "Always check the glossary with search_glossary ..."

```text
To understand the difference between **LoRA** (Low-Rank Adaptation) and **QLoRA** (Quantized LoRA), it helps to look at how they handle the base model's weights during training:

* **LoRA** freezes the pretrained model weights (typically loaded in standard precision, such as FP16 or BF16) and adds trainable low-rank adaptation matrices to specific layers. This drastically reduces the number of trainable parameters compared to full fine-tuning.
* **QLoRA** takes it a step further to save even more memory. It quantizes the base model's weights to a lower precision (such as 4-bit) while keeping the low-rank adapters trainable. This allows much larger models to be fine-tuned on modest hardware (like consumer GPUs) without a significant drop in performance.

Think about how both methods freeze the base model and introduce low-rank matrices—how does quantization in QLoRA change the memory footprint of the base model itself?

(Lecture 02)

--- trace ---
[tool call] search_glossary({'query': 'LoRA'})
[tool call] search_glossary({'query': 'QLoRA'})
[usage] requests=2 in=1763 out=250
```

### E1 no-always-search | What is the difference between RAG and fine-tuning?

Change: INSTRUCTIONS: deleted "Always check the glossary with search_glossary ..."

```text
To understand the difference between RAG and fine-tuning, it helps to think about *where* the knowledge lives and *what* each approach is best designed to achieve.

- **Fine-tuning** involves further training a pretrained model on specific data. According to our course glossary, it is well-suited for teaching a model a specific **output format, tone, or behavior** in a particular domain. However, for handling frequently changing or up-to-date facts, consulting external data is typically preferred.
- **RAG (Retrieval-Augmented Generation)**, on the other hand, dynamically retrieves external information (like documents or databases) and supplies it to the model at inference time as context, rather than baking the facts directly into the model's weights.

To help you think through this: When would you want a model to *know* how to respond (behavior/style), and when would you want it to *look up* the answer (facts/documents)?

Lecture 02

--- trace ---
[tool call] search_glossary({'query': 'RAG'})
[tool call] search_glossary({'query': 'Fine-tuning'})
[tool call] search_glossary({'query': 'RAG'})
[usage] requests=3 in=3225 out=262
```

### E2 several-terms | What is the difference between LoRA and QLoRA?

Change: search_glossary docstring: "Put only one term" -> "Put several terms together"

```text
Based on the course glossary:

* **LoRA** (Low-Rank Adaptation) freezes pretrained model weights and represents weight updates as a low-rank product of two small matrices, training only those small parameters to save memory and storage.
* **QLoRA** takes this a step further by quantizing the base-model weights (for example, down to 4-bit precision) to save even more memory, and then trains with LoRA. This allows you to run and fine-tune much larger models on smaller GPUs.

To think about how they work together: imagine LoRA as the efficient training technique (training small adapter matrices), and QLoRA as the memory-saving foundation (compressing the base model so it fits easily into GPU memory in the first place).

*(Lecture 02)*

--- trace ---
[tool call] search_glossary({'query': 'LoRA QLoRA'})
[usage] requests=2 in=1518 out=188
```

### E2 several-terms | Briefly explain PEFT, LoRA, QLoRA and quantization.

Change: search_glossary docstring: "Put only one term" -> "Put several terms together"

```text
Here is a brief explanation of each concept based on the course materials:

* **PEFT (Parameter-Efficient Fine-Tuning):** An umbrella term for methods that train only a small subset of model parameters or a small set of added parameters instead of the entire model, greatly reducing GPU memory and storage requirements.
* **LoRA (Low-Rank Adaptation):** A popular PEFT method that freezes the pretrained model weights, represents weight updates using a low-rank product of two small matrices, and trains only those small matrices. This produces small adapter files while maintaining high performance.
* **Quantization:** The process of reducing the precision of a model's weights (for example, representing weights using fewer bits, such as 4-bit or 8-bit instead of 16-bit or 32-bit), which significantly reduces memory consumption.
* **QLoRA (Quantized Low-Rank Adaptation):** A method that combines quantization and LoRA by loading the base model in low-bit precision (like 4-bit) to save memory, and then training using LoRA adapters. This allows much larger models to be fine-tuned on modest hardware.

To explore this further, try thinking about how freezing the base weights in LoRA helps us avoid updating the billions of parameters in a large language model.

(Lecture 02)

--- trace ---
[tool call] search_glossary({'query': 'PEFT LoRA QLoRA quantization'})
[usage] requests=2 in=1599 out=306
```

### E2 several-terms | What is the difference between RAG and fine-tuning?

Change: search_glossary docstring: "Put only one term" -> "Put several terms together"

```text
To understand the difference between **RAG (Retrieval-Augmented Generation)** and **Fine-tuning**, it helps to think of them as two different ways to equip a language model with external knowledge or specialized capabilities:

* **Fine-tuning** updates the model's internal weights by training it on a specific dataset. As the glossary defines it, it is great for teaching a model a particular **output format, tone, or behavior in a specific domain**. However, it is not ideal for frequently changing facts because the model's knowledge is frozen in its weights after training.
* **RAG**, on the other hand, keeps the model's weights untouched. Instead, when a user asks a question, relevant documents or facts are retrieved from an external database and passed directly into the model's prompt as context. This makes RAG much more suitable for up-to-date facts and dynamic information.

**A good way to think about it:**
* *Fine-tuning* is like studying hard for an exam and relying on your long-term memory.
* *RAG* is like taking an open-book test where you look up the exact facts right when you need them.

(Lecture 02)

--- trace ---
[tool call] search_glossary({'query': 'RAG fine-tuning'})
[usage] requests=2 in=1411 out=274
```

### E3 end-with-quiz | What is the difference between LoRA and QLoRA?

Change: INSTRUCTIONS: "End ... (Lecture NN)" -> "End with one review question"

```text
Based on the course glossary for AIE2026:

* **LoRA (Low-Rank Adaptation):** A PEFT (Parameter-Efficient Fine-Tuning) method that freezes the pretrained model weights, represents weight updates as a low-rank product of two small matrices, and trains only those small matrices. This significantly reduces the number of trainable parameters and saves the results in small adapter files.
* **QLoRA (Quantized Low-Rank Adaptation):** An extension that saves memory by quantizing the base-model weights (for example, down to 4 bits) before applying LoRA. This allows you to fine-tune much larger models on smaller GPUs than would normally be possible.

To help you think about this further, try considering: **How does quantizing the base model weights to 4-bit in QLoRA affect the precision of the original model compared to standard LoRA, and why does this memory savings matter for fine-tuning?**

--- trace ---
[tool call] search_glossary({'query': 'LoRA'})
[usage] requests=2 in=1575 out=219
```
