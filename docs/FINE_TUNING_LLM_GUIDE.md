# Fine-Tuning LLM Models: A Comprehensive Guide

A practical guide covering concepts, techniques, and implementation for fine-tuning Large Language Models — with specific guidance for Vertex AI / Gemini (used in this project) and open-source models via Hugging Face.

---

## Table of Contents

1. [What Is Fine-Tuning?](#what-is-fine-tuning)
2. [When to Fine-Tune (vs. Alternatives)](#when-to-fine-tune-vs-alternatives)
3. [Fine-Tuning Techniques](#fine-tuning-techniques)
4. [Data Preparation](#data-preparation)
5. [Fine-Tuning on Vertex AI (Gemini)](#fine-tuning-on-vertex-ai-gemini)
6. [Fine-Tuning Open-Source Models (Hugging Face)](#fine-tuning-open-source-models-hugging-face)
7. [Hyperparameter Guide](#hyperparameter-guide)
8. [Evaluation and Iteration](#evaluation-and-iteration)
9. [Production Deployment](#production-deployment)
10. [Cost and Infrastructure](#cost-and-infrastructure)
11. [References](#references)

---

## What Is Fine-Tuning?

Fine-tuning adapts a pre-trained LLM to a specific task or domain by continuing training on a smaller, task-specific dataset. The base model already understands language broadly; fine-tuning specializes it.

```
Pre-trained Model  +  Task-Specific Data  →  Fine-Tuned Model
(general knowledge)   (your examples)        (specialized behavior)
```

**What fine-tuning changes:**
- Output style, format, and tone
- Task-specific behavior (classification, extraction, summarization)
- Domain vocabulary and conventions
- Adherence to specific instructions or constraints

**What fine-tuning does NOT do well:**
- Inject new factual knowledge (use RAG for this)
- Replace the need for good prompting
- Fix fundamental model capability limits

---

## When to Fine-Tune (vs. Alternatives)

### Decision Framework

```
Is prompt engineering sufficient?
  ├── YES → Don't fine-tune. Use prompt engineering.
  └── NO
      ├── Do you need the model to access external knowledge?
      │   └── YES → Use RAG (Retrieval-Augmented Generation)
      └── Do you need to change model behavior/style/format?
          └── YES → Fine-tune.
```

### When Fine-Tuning Makes Sense

| Scenario | Example |
|----------|---------|
| Consistent output format | Always return structured JSON with specific fields |
| Domain-specific language | Medical, legal, or industry-specific terminology |
| Behavioral alignment | Match a specific brand voice or communication style |
| Classification tasks | Categorize support tickets, detect sentiment |
| Entity extraction | Extract product names, prices, dates from text |
| Cost reduction | Replace expensive long prompts with learned behavior |

### When NOT to Fine-Tune

| Scenario | Better Alternative |
|----------|-------------------|
| Model lacks factual knowledge | RAG with a knowledge base |
| Simple formatting needs | Few-shot prompting |
| One-off tasks | Prompt engineering |
| Rapidly changing requirements | Prompt templates |

---

## Fine-Tuning Techniques

### 1. Full Fine-Tuning

Updates **every parameter** in the model.

| Aspect | Detail |
|--------|--------|
| **Accuracy** | Highest possible task-specific accuracy |
| **Memory** | Requires multi-GPU clusters (A100/H100) |
| **Cost** | Very expensive — 70B model needs ~1120GB GPU memory |
| **Speed** | Slowest to train |
| **Use case** | Large datasets, maximum quality, production models |

### 2. LoRA (Low-Rank Adaptation)

Freezes the base model and trains small **adapter matrices** injected into transformer layers. Only ~1-5% of parameters are trainable.

```
Original Weight Matrix W (frozen)
        +
Low-Rank Matrices A × B (trainable, rank r)
        =
Adapted Output
```

| Aspect | Detail |
|--------|--------|
| **Memory savings** | ~80% reduction vs full fine-tuning |
| **Quality** | 90-95% of full fine-tuning quality |
| **Speed** | Much faster training |
| **Inference** | Zero latency overhead (adapters merge into base weights) |
| **Use case** | Most fine-tuning scenarios; the default recommendation |

**Key insights from experiments:**
- Target **all linear layers**, not just attention blocks, for best results
- Increasing rank adds parameters; balance with alpha to avoid overfitting
- Choice of optimizer (AdamW vs SGD+scheduler) has minimal impact
- Iterating over the dataset more than once can worsen results

### 3. QLoRA (Quantized LoRA)

Combines LoRA with **4-bit quantization** of the base model, dramatically reducing memory.

| Aspect | Detail |
|--------|--------|
| **Memory savings** | ~33% beyond LoRA |
| **Training speed** | ~39% slower than LoRA (quantization overhead) |
| **Quality** | No discernible reduction vs LoRA in empirical tests |
| **Use case** | Large models on limited hardware (e.g., 70B on 24GB VRAM) |

QLoRA introduces: 4-bit NormalFloat quantization, Double Quantization, and Paged Optimizers.

### 4. Choosing the Right Technique

```
Does your base model fit in GPU memory?
  ├── YES, comfortably → Use LoRA
  ├── Barely → Use QLoRA
  └── NO → Use QLoRA or rent larger hardware

Is this for production with strict accuracy requirements?
  ├── YES → Prototype with LoRA, then full fine-tune the winner
  └── NO → LoRA is sufficient
```

---

## Data Preparation

### Dataset Size Guidelines

| Dataset Size | Expected Outcome |
|-------------|-----------------|
| 50-100 examples | Minimal behavioral change; good for format enforcement |
| 100-500 examples | Noticeable task-specific improvement |
| 500-1,000 examples | Strong performance for well-defined tasks |
| 1,000-10,000 examples | Robust fine-tuning for complex tasks |
| 10,000+ examples | Diminishing returns unless task is very complex |

### Data Quality Principles

1. **Quality over quantity** — 200 excellent examples beat 2,000 mediocre ones
2. **Diversity** — Cover the full range of expected inputs
3. **Consistency** — Same format and standards across all examples
4. **Accuracy** — Every example should represent the ideal output
5. **Balanced** — Avoid over-representing any single category

### Standard Data Formats

**Conversational format** (recommended for chat/instruction models):
```jsonl
{"messages": [{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": "Summarize this article..."}, {"role": "assistant", "content": "The article discusses..."}]}
{"messages": [{"role": "user", "content": "Classify this review..."}, {"role": "assistant", "content": "Positive"}]}
```

**Prompt-completion format** (simpler tasks):
```jsonl
{"prompt": "Translate to French: Hello, how are you?", "completion": "Bonjour, comment allez-vous?"}
{"prompt": "Extract the price: The laptop costs $999.", "completion": "$999"}
```

### Data Preparation Checklist

- [ ] Define the task clearly before collecting data
- [ ] Create 10-20 gold-standard examples first as a template
- [ ] Validate every example matches expected behavior
- [ ] Remove duplicates and near-duplicates
- [ ] Split into train (80-90%) and validation (10-20%) sets
- [ ] Store in JSONL format (one JSON object per line)
- [ ] For Vertex AI: upload to Google Cloud Storage

---

## Fine-Tuning on Vertex AI (Gemini)

Since this project uses Vertex AI and Gemini models, here is the specific workflow.

### Supported Models

- **Gemini 2.5 Flash** — Lightweight, cost-efficient (recommended for fine-tuning)
- **Gemini 2.5 Pro** — Higher capability, supports up to 131,072 tokens per training example

### Data Format for Vertex AI

```jsonl
{"systemInstruction": {"parts": [{"text": "You are a video production assistant."}]}, "contents": [{"role": "user", "parts": [{"text": "Suggest ad concepts for a yoga brand."}]}, {"role": "model", "parts": [{"text": "Here are 3 ad concepts for a yoga brand:\n\n1. **Morning Flow** - A serene sunrise scene..."}]}]}
```

### Using the Google Gen AI SDK (Recommended)

> **Note:** The `vertexai.tuning` module is deprecated as of June 2025. Use the Google Gen AI SDK instead.

```python
from google import genai
from google.genai.types import HttpOptions

# Initialize the client
client = genai.Client(
    vertexai=True,
    project="your-project-id",
    location="us-central1",
    http_options=HttpOptions(api_version="v1"),
)

# Launch a supervised fine-tuning job
tuning_job = client.tunings.tune(
    base_model="gemini-2.5-flash",
    training_dataset={
        "gcs_uri": "gs://your-bucket/training_data.jsonl",
    },
    config={
        "tuned_model_display_name": "my-tuned-model",
        "epoch_count": 3,
        "learning_rate_multiplier": 1.0,
    },
)

# Monitor progress
print(f"Tuning job name: {tuning_job.name}")
print(f"State: {tuning_job.state}")

# Once complete, use the tuned model
tuned_model_name = tuning_job.tuned_model.name
response = client.models.generate_content(
    model=tuned_model_name,
    contents="Your prompt here",
)
print(response.text)
```

### Using the Vertex AI SDK (Legacy, deprecated June 2025)

```python
import vertexai
from vertexai.tuning import sft

vertexai.init(project="your-project-id", location="us-central1")

# Create the tuning job
tuning_job = sft.train(
    source_model="gemini-2.5-flash",
    train_dataset="gs://your-bucket/training_data.jsonl",
    validation_dataset="gs://your-bucket/validation_data.jsonl",  # optional
    tuned_model_display_name="my-tuned-model",
    epochs=3,
    adapter_size=4,  # 1, 4, 8, or 16
    learning_rate_multiplier=1.0,
)

# Poll for completion
while not tuning_job.has_ended:
    time.sleep(60)
    tuning_job.refresh()

# Get the tuned model endpoint
print(f"Tuned model: {tuning_job.tuned_model_name}")
print(f"Endpoint: {tuning_job.tuned_model_endpoint_name}")
```

### Vertex AI Tuning Parameters

| Parameter | Description | Recommendation |
|-----------|-------------|----------------|
| `epoch_count` | Passes over training data | Start with default (auto-set by Vertex AI) |
| `adapter_size` | Number of trainable params (1, 4, 8, 16) | Start with 4; increase for complex tasks |
| `learning_rate_multiplier` | Scales the base learning rate | Start with 1.0; reduce if overfitting |

### Vertex AI Tips

- For thinking-enabled models, set thinking budget to off/lowest during fine-tuning
- Provide at least 100 examples for meaningful improvement
- SFT is best for style/format/behavior — use RAG for factual knowledge
- Monitor training loss in the Google Cloud Console
- Tuning jobs run asynchronously; typical jobs take 1-4 hours

---

## Fine-Tuning Open-Source Models (Hugging Face)

For experimentation, research, or scenarios where you want full control over the model.

### Using TRL's SFTTrainer (Recommended)

TRL (Transformer Reinforcement Learning) is the standard library for post-training LLMs.

#### Minimal Example

```python
from trl import SFTTrainer
from datasets import load_dataset

dataset = load_dataset("trl-lib/Capybara", split="train")

trainer = SFTTrainer(
    model="Qwen/Qwen3-0.6B",
    train_dataset=dataset,
)
trainer.train()
```

#### Full Example with LoRA

```python
from datasets import load_dataset
from trl import SFTConfig, SFTTrainer
from peft import LoraConfig
import torch

# 1. Load dataset
dataset = load_dataset("your-dataset", split="train")

# 2. Configure LoRA
peft_config = LoraConfig(
    r=16,                        # Rank of the low-rank matrices
    lora_alpha=16,               # Scaling factor
    lora_dropout=0.05,           # Dropout for regularization
    bias="none",
    target_modules="all-linear", # Apply to all linear layers
    task_type="CAUSAL_LM",
)

# 3. Configure training
training_args = SFTConfig(
    output_dir="./output",
    max_steps=1000,
    per_device_train_batch_size=4,
    gradient_accumulation_steps=4,
    learning_rate=2e-4,
    logging_steps=10,
    save_steps=100,
    eval_strategy="steps",
    eval_steps=50,
    bf16=True,                   # Use bfloat16 (default in trl >= 0.20)
    gradient_checkpointing=True, # Save memory at cost of speed
)

# 4. Train
trainer = SFTTrainer(
    model="meta-llama/Llama-3.1-8B",
    args=training_args,
    train_dataset=dataset,
    peft_config=peft_config,
)
trainer.train()

# 5. Save the adapter
trainer.save_model("./my-lora-adapter")
```

#### QLoRA Example (4-bit Quantization)

```python
from transformers import BitsAndBytesConfig
from trl import SFTConfig, SFTTrainer
from peft import LoraConfig
import torch

# Quantization config for QLoRA
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_use_double_quant=True,
)

peft_config = LoraConfig(
    r=16,
    lora_alpha=16,
    lora_dropout=0.05,
    bias="none",
    target_modules="all-linear",
    task_type="CAUSAL_LM",
)

training_args = SFTConfig(
    output_dir="./qlora-output",
    max_steps=500,
    per_device_train_batch_size=2,
    gradient_accumulation_steps=8,
    learning_rate=2e-4,
    bf16=True,
    gradient_checkpointing=True,
)

trainer = SFTTrainer(
    model="meta-llama/Llama-3.1-70B",
    args=training_args,
    train_dataset=dataset,
    peft_config=peft_config,
    model_init_kwargs={"quantization_config": bnb_config},
)
trainer.train()
```

### Preparing a Custom Dataset

```python
from datasets import Dataset

# From a list of conversations
data = [
    {
        "messages": [
            {"role": "system", "content": "You are a video production assistant."},
            {"role": "user", "content": "Suggest concepts for a yoga brand ad."},
            {"role": "assistant", "content": "Here are 3 concepts:\n1. Morning Flow..."},
        ]
    },
    # ... more examples
]

dataset = Dataset.from_list(data)
dataset.push_to_hub("your-org/your-dataset")  # optional: share on HF Hub
```

---

## Hyperparameter Guide

### Most Impactful Hyperparameters (in order)

1. **Learning rate** — Too high = divergence; too low = no learning
2. **Number of epochs** — 1-3 epochs is usually sufficient; more can overfit
3. **LoRA rank (r)** — Higher = more capacity but risk of overfitting
4. **Batch size** — Larger = more stable gradients; limited by memory
5. **LoRA alpha** — Typically set equal to rank, or 2× rank

### Recommended Starting Points

| Hyperparameter | Value | Notes |
|----------------|-------|-------|
| Learning rate | 2e-4 | For LoRA/QLoRA; 1e-5 for full fine-tuning |
| Epochs | 1-3 | Start with 1; increase only if underfitting |
| LoRA rank (r) | 16 | Good default; try 8 or 32 based on results |
| LoRA alpha | 16-32 | Common to set equal to or 2× rank |
| LoRA dropout | 0.05 | Light regularization |
| Batch size | 4-8 | Per device; use gradient accumulation if needed |
| Weight decay | 0.01 | Standard for AdamW |
| Warmup ratio | 0.03-0.1 | Gentle warmup over first 3-10% of steps |
| Max sequence length | 2048-4096 | Match your task requirements |

---

## Evaluation and Iteration

### Evaluation Strategy

1. **Hold out a test set** — Never train on evaluation data
2. **Use task-specific metrics** — Accuracy, F1, BLEU, ROUGE, or custom rubrics
3. **Compare against baseline** — Always compare tuned model vs. base model with prompting
4. **Human evaluation** — Essential for open-ended generation tasks

### Common Issues and Fixes

| Problem | Symptom | Fix |
|---------|---------|-----|
| **Overfitting** | Perfect train loss, poor eval | Reduce epochs, increase dropout, add more data |
| **Underfitting** | High train loss doesn't decrease | Increase learning rate, increase rank, check data quality |
| **Catastrophic forgetting** | Model loses general capabilities | Reduce learning rate, fewer epochs, use LoRA |
| **Inconsistent outputs** | Good on some examples, bad on others | More diverse training data, check for label noise |
| **Training instability** | Loss spikes or NaN values | Reduce learning rate, check for data issues |

### Iteration Workflow

```
1. Start with prompt engineering (baseline)
2. Collect 100-200 high-quality examples
3. Fine-tune with LoRA (default hyperparameters)
4. Evaluate on held-out test set
5. Analyze errors → improve data → repeat
6. Scale up data/parameters only when data quality is high
```

---

## Production Deployment

### Deployment Options

| Platform | Method | Pros | Cons |
|----------|--------|------|------|
| **Vertex AI** | Managed endpoint | Zero infra management, auto-scaling | Cost, vendor lock-in |
| **Hugging Face Inference** | Dedicated endpoints | Easy deployment, model versioning | Cost at scale |
| **vLLM / TGI** | Self-hosted on GPU | Full control, batch inference | Requires infra management |
| **Ollama** | Local/edge | Privacy, low latency | Limited to smaller models |

### Merging LoRA Adapters for Production

```python
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

# Load base model and adapter
base_model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-3.1-8B")
model = PeftModel.from_pretrained(base_model, "./my-lora-adapter")

# Merge adapter into base model (zero inference overhead)
merged_model = model.merge_and_unload()

# Save the merged model
merged_model.save_pretrained("./merged-model")
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.1-8B")
tokenizer.save_pretrained("./merged-model")
```

---

## Cost and Infrastructure

### Hardware Requirements (Approximate)

| Model Size | Full Fine-Tune | LoRA | QLoRA |
|-----------|---------------|------|-------|
| 1-3B | 1× A100 40GB | 1× T4 16GB | 1× T4 16GB |
| 7-8B | 2× A100 40GB | 1× A100 40GB | 1× T4 16GB |
| 13B | 4× A100 40GB | 1× A100 80GB | 1× A100 40GB |
| 70B | 16× A100 80GB | 4× A100 80GB | 1× A100 80GB |

### Cost Comparison (Cloud GPU, approximate)

| Method | 7B Model, 1000 examples | 70B Model, 1000 examples |
|--------|------------------------|-------------------------|
| Full fine-tuning | $50-200 | $500-2,000 |
| LoRA | $10-30 | $100-400 |
| QLoRA | $5-15 | $30-100 |
| Vertex AI (managed) | Pay per tuning hour | Pay per tuning hour |

---

## References

### Vertex AI / Gemini Fine-Tuning
- [Tune Gemini models by using supervised fine-tuning](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/models/gemini-use-supervised-tuning) — Official Google Cloud documentation
- [About supervised fine-tuning for Gemini models](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/models/gemini-supervised-tuning) — Conceptual overview
- [Prepare supervised fine-tuning data for Gemini](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/models/gemini-supervised-tuning-prepare) — Data format guide
- [Fine-tune Gemini on Vertex AI (Codelab)](https://codelabs.developers.google.com/codelabs/production-ready-ai-with-gc/9-ai-finetuning/finetune-gemini-vertex-ai) — Hands-on tutorial
- [Vertex AI Tuning API Reference](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/model-reference/tuning) — API details

### Hugging Face / Open-Source
- [TRL SFTTrainer Documentation](https://huggingface.co/docs/trl/en/sft_trainer) — Official SFTTrainer docs
- [Hugging Face LLM Course: Supervised Fine-Tuning](https://huggingface.co/learn/llm-course/chapter11/3) — Step-by-step tutorial
- [How to fine-tune open LLMs in 2025](https://www.philschmid.de/fine-tune-llms-in-2025) — Practical walkthrough
- [PEFT Library Documentation](https://huggingface.co/docs/peft) — LoRA/QLoRA implementation

### Research and Deep Dives
- [The Ultimate Guide to Fine-Tuning LLMs](https://arxiv.org/html/2408.13296v1) — Comprehensive survey paper
- [LoRA Insights from Hundreds of Experiments](https://lightning.ai/pages/community/lora-insights/) — Empirical findings on hyperparameters
- [Practical Tips for Fine-tuning LLMs with LoRA](https://magazine.sebastianraschka.com/p/practical-tips-for-finetuning-llms) — Sebastian Raschka's guide
- [LoRA vs QLoRA: Best Fine-Tuning Tools 2026](https://www.index.dev/blog/top-ai-fine-tuning-tools-lora-vs-qlora-vs-full) — Tool comparison
- [Efficient Fine-Tuning with LoRA (Databricks)](https://www.databricks.com/blog/efficient-fine-tuning-lora-guide-llms) — Parameter selection guide
- [LoRAFusion: Efficient LoRA Fine-Tuning (EuroSys '26)](https://arxiv.org/html/2510.00206v1) — Cutting-edge multi-LoRA optimization
