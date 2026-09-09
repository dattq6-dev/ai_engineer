# Building a Certification-Style AI Exam Generation System

## Recommended Architecture

Think of the process as a pipeline:

```text
Training Material
        ↓
Knowledge Extraction
        ↓
Knowledge Graph / Concept Catalog
        ↓
Question Blueprint Generation
        ↓
Question Generation
        ↓
Distractor Generation
        ↓
Quality Review
        ↓
Exam Bank
```

---

# Step 1: Build a Concept Catalog (Most Important)

first convert source materials into structured concepts.

Example:

## Source

```text
AI Gateway

Benefits:
- Credential management
- Usage tracking
- Guardrails
```

Convert to:

```yaml
concept_id: DB_AI4_001

name: AI Gateway

type: Feature

key_points:
  - credential management
  - token usage tracking
  - guardrails

common_misconceptions:
  - Secret Scope solves governance
  - UC grants solve governance
  - API keys in code are acceptable

use_cases:
  - enterprise governance
  - centralized LLM access

difficulty:
  medium
```

Now AI can generate many questions from the same concept.

This is how certification vendors work.

---

# Step 2: Extract More Than Facts

For each source topic, extract 6 dimensions:

```text
Definition
Feature
Architecture
Trade-off
Failure Mode
Best Practice
```

Example:

## RAG

Definition

```text
Context Recall
```

Formula

```text
retrieved relevant / total relevant
```

Failure Mode

```text
low recall
```

Mitigation

```text
improve retrieval
```

Architecture

```text
Vector Search
```

Trade-off

```text
precision vs recall
```

Now 1 source concept can create 10-20 questions.

---

# Step 3: Generate Question Blueprints

Before generating the actual question.

Create templates.

### Blueprint A

```text
Business Problem
↓
Which feature solves it?
```

Example:

```text
Need governance

Which feature?
```

### Blueprint B

```text
Observed Metrics
↓
Diagnosis
```

Example:

```text
Faithfulness=0.92
Relevance=0.61

What's wrong?
```

### Blueprint C

```text
Architecture Need
↓
Choose Architecture
```

Example:

```text
Need parallel processing

What design?
```

### Blueprint D

```text
Attack Scenario
↓
Identify Threat
↓
Choose Mitigation
```

Example:

```text
Ignore previous instructions

What attack?
```

---

# Step 4: Generate Distractors Separately

This is where most AI-generated exams fail.

The uploaded file has excellent distractors.

Use a dedicated process.

For every concept generate:

## Distractor Type 1

Extreme statement

```text
Always
Never
All
None
```

Example:

```text
Genie is always accurate
```

## Distractor Type 2

Partial truth

Example:

```text
Secret Scope
```

Solves credentials.

Not governance.

## Distractor Type 3

Related technology

Example:

```text
Spark UI
```

instead of

```text
MLflow Tracing
```

## Distractor Type 4

Common beginner mistake

Example:

```text
Use a bigger LLM
```

instead of fixing retrieval.

This one trick alone dramatically improves exam quality.

---

# Step 5: Use Retrieval Instead of Full Context

If building a large exam bank:

Don't stuff all training documents into the prompt.

Use:

```text
Source Document
      ↓
Chunking
      ↓
Vector Search
      ↓
Retrieve Relevant Concept
      ↓
Question Generator
```

RAG works much better once source content exceeds:

```text
100-200 pages
```

---

# Step 6: Generate Explanations Too

The uploaded exam succeeds because every answer contains:

```text
Correct Answer

Why Correct

Why Others Wrong

Reference
```

Example format:

```yaml
answer: C

explanation:
  correct:
    Context Recall =
    Retrieved Relevant /
    Total Relevant

  why_A_wrong:
    Uses total chunks

  why_B_wrong:
    Wrong denominator

  why_D_wrong:
    Inverted formula

reference:
    Databricks Academy
```

---

# Step 7: Maintain Metadata

Store every question like:

```json
{
  "id": "Q001",
  "source": "DB-AI2",
  "concept": "Context Recall",
  "difficulty": "Easy",
  "question_type": "Calculation",
  "taxonomy": "Apply",
  "answer": "C"
}
```

Then you can easily generate:

- Practice exams
- Final exams
- Difficult-only exams
- Topic-specific exams

---

# If I Were Building This at Techcombank

I would build a 3-layer architecture:

## Layer 1 - Knowledge Repository

Store:

```text
PDF
PPT
Course Notes
Internal Wiki
```

in Unity Catalog.

## Layer 2 - Concept Extraction Agent

LLM extracts:

```text
Concept
Definition
Best Practice
Trade-off
Failure Mode
Misconception
```

and saves into Delta tables.

Example:

```sql
exam_concepts
exam_sources
exam_misconceptions
exam_examples
```

## Layer 3 - Exam Generator Agent

Generate:

```text
Question
Options
Answer
Explanation
Difficulty
```

using predefined templates.

This produces consistent output.

---

# The Best Prompting Strategy

Instead of:

```text
Read this PDF.
Create 50 questions.
```

Use:

```text
For each concept:

1. Create realistic banking scenario.
2. Test understanding not memorization.
3. Create 3 strong distractors:
   - partial truth
   - common misconception
   - related technology
4. Include explanation.
5. Assign difficulty.
6. Ensure only one answer is correct.
```

This will get you much closer to the quality of the uploaded exam.

---

# Bottom Line

The highest-quality solution is not:

```text
Source → AI → Questions
```

It is:

```text
Source
↓
Concept Extraction
↓
Misconception Extraction
↓
Question Blueprint
↓
Question Generation
↓
Distractor Generation
↓
Quality Validation
↓
Exam Bank
```

That's essentially how professional certification providers build scalable question banks.
