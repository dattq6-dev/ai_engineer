# Section 2: Data Preparation (14%) — MCQ Practice Set
**60 Questions | Difficulty: Beginner → Proficiency | Exam: Databricks Certified Generative AI Engineer Associate**

---

### Question 1
**Difficulty:** Beginner
> **Blueprint:** A – Business Problem → Which Feature Solves It?
> **Concept:** Chunking Strategy – Token Limit Constraint
> **Dimension:** Best Practice

A developer is ingesting plain-text product documentation into a Databricks RAG pipeline. The embedding model they chose has a maximum context limit of 512 tokens. Which chunking concern is MOST critical to address first?

* **A)** The chunks must all contain exactly the same number of sentences so that the LLM receives uniformly structured context regardless of the length of each sentence in the original document. *(Distractor type: Common misconception — uniform length is not a requirement)*
* **B)** No chunk should exceed 512 tokens, because text beyond the token limit is silently truncated by the embedding model, causing information loss and degrading the quality of the resulting vector.
* **C)** Every chunk must begin with the document's title so the LLM always knows which source document a chunk belongs to, preventing it from confusing content from different product manuals. *(Distractor type: Partial truth — metadata is useful but secondary)*
* **D)** Each chunk must be stored as a separate file in a Databricks Volume before embedding, because the embedding model cannot process chunks passed as in-memory Python strings directly. *(Distractor type: Beginner mistake — unnecessary overhead)*

**Correct Answer:** B

**Why B is Correct:** Embedding models have a hard token limit; any text beyond that limit is truncated before the embedding is computed, permanently losing part of the chunk's meaning and producing a misleading embedding vector. Ensuring no chunk exceeds 512 tokens is the most fundamental constraint.

**Why A is Wrong:** Uniform sentence count is not a requirement — chunk quality is about semantic completeness within the token limit, not uniform length.

**Why C is Wrong:** While adding metadata (like document title) is a useful best practice, it is a secondary concern to first ensuring chunks fit the model's token limit.

**Why D is Wrong:** Embedding models accept text strings directly in API calls; writing each chunk to a file first is unnecessary overhead with no benefit.

**Source:** Section 2: Data Preparation – Objective 1: Apply a chunking strategy for a given document structure and model constraints

```json
{
  "id": "S2Q001",
  "source": "DB-GenAI-S2",
  "concept": "Chunking Strategy – Token Limit Constraint",
  "dimension": "Best Practice",
  "difficulty": "Beginner",
  "question_type": "Scenario",
  "blueprint": "A",
  "taxonomy": "Understand",
  "answer": "B"
}
```

---

### Question 2
**Difficulty:** Beginner
> **Blueprint:** A – Business Problem → Which Feature Solves It?
> **Concept:** Content Filtering – Extraneous HTML Elements
> **Dimension:** Best Practice

A data engineer is preparing HTML web pages for a RAG knowledge base. Each page contains the actual article text, but also a navigation bar, header logo text, footer with copyright notices, and cookie consent banners. What should be done to these extra elements before chunking?

* **A)** Include all HTML elements in the chunks unchanged, because the embedding model and LLM are trained on web data and can automatically distinguish navigation text from article content. *(Distractor type: Extreme statement — "automatically distinguish")*
* **B)** Replace the navigation, footer, and banner text with placeholder tokens like `[NAV]`, `[FOOTER]`, and `[BANNER]` so the LLM knows to ignore them when generating answers. *(Distractor type: Common misconception — placeholders still consume embedding space)*
* **C)** Filter and remove the navigation bar, header, footer, and cookie banners before chunking, so that only the meaningful article content is embedded and stored in the Vector Search index.
* **D)** Convert all HTML pages to PDF format first, because PDF parsers automatically strip navigation elements and return only the main body text for downstream chunking and embedding. *(Distractor type: Beginner mistake — PDF conversion does not filter content)*

**Correct Answer:** C

**Why C is Correct:** Navigation bars, footers, and cookie banners are extraneous content that adds noise without contributing relevant knowledge. Embedding these elements dilutes the semantic signal of the chunk. Filtering them out using a library like `beautifulsoup4` before chunking is the standard approach.

**Why A is Wrong:** LLMs and embedding models do not automatically filter out boilerplate HTML structure; repeated boilerplate degrades retrieval quality.

**Why B is Wrong:** Placeholder tokens still consume embedding space and teach the retriever to associate queries with boilerplate metadata, which is counterproductive.

**Why D is Wrong:** HTML-to-PDF tools typically include all visible page elements, and the conversion adds processing overhead without solving the filtering problem.

**Source:** Section 2: Data Preparation – Objective 2: Filter extraneous content in source documents

```json
{
  "id": "S2Q002",
  "source": "DB-GenAI-S2",
  "concept": "Content Filtering – Extraneous HTML Elements",
  "dimension": "Best Practice",
  "difficulty": "Beginner",
  "question_type": "Scenario",
  "blueprint": "A",
  "taxonomy": "Apply",
  "answer": "C"
}
```

---

### Question 3
**Difficulty:** Beginner
> **Blueprint:** A – Business Problem → Which Feature Solves It?
> **Concept:** Document Extraction – OCR for Scanned PDFs
> **Dimension:** Feature

A team has a folder of scanned paper documents (image-based PDFs where the text is not selectable) and needs to extract the text content for a RAG pipeline. Which Python library should they use for this task?

* **A)** `beautifulsoup4` — because it can parse any binary file format including image-based PDFs by treating the file as an HTML document and stripping non-text elements. *(Distractor type: Related technology — wrong domain)*
* **B)** `PyPDF2` — because it reads PDF files page by page and extracts embedded text, including text in rasterized image layers within the PDF file. *(Distractor type: Partial truth — only extracts digital text layers)*
* **C)** `pytesseract` — because it performs Optical Character Recognition (OCR) on images and scanned documents, converting the visual text in the scanned pages into machine-readable strings.
* **D)** `unstructured` — because it natively handles all file formats including scanned image PDFs by directly reading the binary pixel data and converting it to structured text elements. *(Distractor type: Partial truth — unstructured uses pytesseract as a backend)*

**Correct Answer:** C

**Why C is Correct:** `pytesseract` is Python's wrapper for Google's Tesseract OCR engine. It processes images and scanned PDFs by analyzing the pixel patterns of characters and converting them into text strings. This is the only option that can extract text from image-based content where no digital text layer exists.

**Why A is Wrong:** `beautifulsoup4` is exclusively for parsing HTML/XML structured text — it has no capability to process binary image data or perform OCR.

**Why B is Wrong:** `PyPDF2` can only extract digitally embedded text layers from PDFs — it cannot read text from rasterized image layers where no text layer exists.

**Why D is Wrong:** While `unstructured` is a powerful multi-format library, it relies on OCR tools (including Tesseract) as a backend for scanned PDFs; `pytesseract` is the direct tool that actually performs the OCR operation.

**Source:** Section 2: Data Preparation – Objective 3: Choose the appropriate Python package to extract document content

```json
{
  "id": "S2Q003",
  "source": "DB-GenAI-S2",
  "concept": "Document Extraction – OCR for Scanned PDFs",
  "dimension": "Feature",
  "difficulty": "Beginner",
  "question_type": "Scenario",
  "blueprint": "A",
  "taxonomy": "Remember",
  "answer": "C"
}
```

---

### Question 4
**Difficulty:** Beginner
> **Blueprint:** C – Architecture Need → Choose Architecture
> **Concept:** Delta Lake – Vector Search Pipeline Sequence
> **Dimension:** Architecture

After chunking product documents, a developer has a Spark DataFrame with columns `id` (unique chunk identifier) and `chunk_text` (the text content). What is the correct sequence of operations to prepare this data for Databricks Vector Search?

* **A)** Create the Vector Search index first, then write the DataFrame to a Delta table, then enable Change Data Feed (CDF) on the table so that future updates sync to the index automatically. *(Distractor type: Common misconception — wrong order)*
* **B)** Write the DataFrame to a Unity Catalog Delta table, enable Change Data Feed (CDF) on the table with `SET TBLPROPERTIES (delta.enableChangeDataFeed = true)`, then create the Vector Search index pointing to that table.
* **C)** Enable CDF on the Unity Catalog schema first, then write the DataFrame to a Delta table, then create a Vector Search endpoint, and finally create the index using the endpoint name as the table reference. *(Distractor type: Common misconception — CDF is a table-level, not schema-level, property)*
* **D)** Write the DataFrame to a Databricks Volume as JSON files, enable Change Data Feed on the volume folder, then create a Vector Search index pointing to the volume path as the data source. *(Distractor type: Beginner mistake — Vector Search requires Delta tables)*

**Correct Answer:** B

**Why B is Correct:** The required sequence is: (1) write chunked data to a Unity Catalog Delta table, (2) enable Change Data Feed on that table (required for Vector Search to detect and sync incremental updates), (3) create the Vector Search index pointing to the Delta table. CDF must be enabled before the index is created so Vector Search can establish the sync pipeline.

**Why A is Wrong:** The index cannot be created before the source table exists and has CDF enabled.

**Why C is Wrong:** CDF is a table-level property, not a schema-level setting.

**Why D is Wrong:** Databricks Vector Search requires a Delta Lake table as its source — it does not support Volume JSON files as a sync source.

**Source:** Section 2: Data Preparation – Objective 4: Define operations and sequence to write chunked text into Delta Lake

```json
{
  "id": "S2Q004",
  "source": "DB-GenAI-S2",
  "concept": "Delta Lake – Vector Search Pipeline Sequence",
  "dimension": "Architecture",
  "difficulty": "Beginner",
  "question_type": "Scenario",
  "blueprint": "C",
  "taxonomy": "Apply",
  "answer": "B"
}
```

---

### Question 5
**Difficulty:** Beginner
> **Blueprint:** A – Business Problem → Which Feature Solves It?
> **Concept:** Knowledge Base Curation – Source Document Quality
> **Dimension:** Best Practice

A company is building an IT Support chatbot on Databricks. They have three potential document sources: (A) current approved troubleshooting guides (updated quarterly), (B) legacy system manuals from 2008 that cover deprecated hardware, and (C) employee birthday party announcements from the internal newsletter. Which documents should be included in the RAG knowledge base?

* **A)** All three sources should be included to maximize the breadth of the knowledge base; the LLM will automatically determine which content is relevant and ignore the irrelevant sources at query time. *(Distractor type: Extreme statement — LLMs cannot reliably ignore retrieved context)*
* **B)** Only source A (current troubleshooting guides) should be included, as it is the only source containing accurate, current, task-relevant information that the chatbot is expected to answer questions about.
* **C)** Sources A and B should be included because the legacy manuals may still contain relevant troubleshooting principles even if the specific hardware is deprecated. *(Distractor type: Partial truth — outdated information causes incorrect answers)*
* **D)** Sources A and C should be included because current guides answer technical questions, and newsletter announcements help the chatbot maintain a friendly conversational tone. *(Distractor type: Common misconception — tone is not sourced from knowledge base documents)*

**Correct Answer:** B

**Why B is Correct:** The knowledge base should contain only documents that are accurate, current, and directly relevant to the chatbot's purpose. The 2008 legacy manuals contain outdated information about deprecated hardware. The birthday announcements are entirely unrelated and will degrade retrieval precision.

**Why A is Wrong:** LLMs cannot reliably "ignore" irrelevant retrieved content — they tend to incorporate whatever context they receive into their generated answers.

**Why C is Wrong:** Including deprecated hardware manuals is likely to cause the chatbot to give outdated troubleshooting steps for hardware the company no longer uses.

**Why D is Wrong:** Newsletter announcements contain no IT support knowledge; including them would cause the retriever to return birthday announcements as context for technical queries.

**Source:** Section 2: Data Preparation – Objective 5: Identify needed source documents

```json
{
  "id": "S2Q005",
  "source": "DB-GenAI-S2",
  "concept": "Knowledge Base Curation – Source Document Quality",
  "dimension": "Best Practice",
  "difficulty": "Beginner",
  "question_type": "Scenario",
  "blueprint": "A",
  "taxonomy": "Evaluate",
  "answer": "B"
}
```

---

### Question 6
**Difficulty:** Intermediate
> **Blueprint:** B – Observed Metrics → Diagnosis
> **Concept:** Chunking Strategy – Document-Aware vs. Fixed-Size
> **Dimension:** Failure Mode

A developer has chunked a Markdown-formatted technical reference guide using fixed-size chunking with 500 characters and 50-character overlap. Users report that answers about configuration options are incomplete. Analysis shows that configuration tables in the Markdown are being split mid-row across chunk boundaries. What is the most targeted fix?

* **A)** Increase the chunk size from 500 to 5,000 characters, which ensures that even the longest configuration tables fit within a single chunk. *(Distractor type: Extreme statement — blunt fix that creates oversized chunks)*
* **B)** Switch from fixed-size chunking to document-aware (structure-based) chunking using Markdown headers and table boundaries as split points, keeping configuration tables intact within a single chunk.
* **C)** Add a 200-character overlap instead of 50 characters so that when a table is split, the overlapping content on both sides reconstructs the missing rows for the LLM during retrieval. *(Distractor type: Common misconception — overlap duplicates boundary content, doesn't reconstruct missing rows)*
* **D)** Convert the Markdown tables to plain prose before chunking (e.g., "Option X has value Y") so that the fixed-size chunker can split the flattened text without breaking logical table rows. *(Distractor type: Partial truth — loses relational table structure)*

**Correct Answer:** B

**Why B is Correct:** The root cause is that fixed-size chunking is structure-agnostic — it splits by character count regardless of document structure, breaking tables mid-row. Document-aware chunking uses the document's own structure (Markdown headers, table boundaries) as natural split points. A library like LangChain's `MarkdownHeaderTextSplitter` or `unstructured` can detect these boundaries and keep tables intact within a chunk.

**Why A is Wrong:** Increasing chunk size to 5,000 characters may solve the immediate problem but creates very large chunks that exceed embedding model token limits and reduce retrieval precision.

**Why C is Wrong:** Overlap preserves context at the edge of chunks but does not reconstruct full table rows.

**Why D is Wrong:** Converting tables to prose loses the relational structure of the table data.

**Source:** Section 2: Data Preparation – Objective 7: Design retrieval systems using advanced chunking strategies

```json
{
  "id": "S2Q006",
  "source": "DB-GenAI-S2",
  "concept": "Chunking Strategy – Document-Aware vs. Fixed-Size",
  "dimension": "Failure Mode",
  "difficulty": "Intermediate",
  "question_type": "Diagnosis",
  "blueprint": "B",
  "taxonomy": "Analyze",
  "answer": "B"
}
```

---

### Question 7
**Difficulty:** Intermediate
> **Blueprint:** A – Business Problem → Which Feature Solves It?
> **Concept:** Retrieval Evaluation – MLflow Tracing + RetrievalRelevance
> **Dimension:** Feature

After deploying a RAG application on Databricks, a developer wants to measure whether the Vector Search retriever is returning the correct document chunks for a given set of test queries. They have a test dataset with queries and the known correct chunk IDs that should be retrieved. Which approach uses the correct Databricks tooling?

* **A)** Manually compare the retrieved chunk IDs to the expected IDs in a Python loop, calculate a match percentage, and log the result as a custom MLflow metric using `mlflow.log_metric("retrieval_accuracy", score)`. *(Distractor type: Partial truth — works but bypasses the native framework)*
* **B)** Decorate the retrieval function with `@mlflow.trace(span_type="RETRIEVER")`, then run `mlflow.genai.evaluate()` with the `RetrievalRelevance` scorer, which uses the captured trace data to evaluate retrieval quality.
* **C)** Use Databricks Model Serving's built-in A/B testing framework to compare two retriever configurations and let the platform automatically select the one with higher user click-through rate on retrieved results. *(Distractor type: Related technology — A/B testing measures behavioral metrics, not retrieval quality)*
* **D)** Query the Vector Search index directly using the REST API, collect the returned chunk IDs into a Delta table, and then run a Spark JOIN against the expected results table to calculate Precision@k. *(Distractor type: Partial truth — valid but requires significant custom code)*

**Correct Answer:** B

**Why B is Correct:** The Databricks-recommended approach for evaluating retrieval is to instrument the retriever with `@mlflow.trace(span_type="RETRIEVER")` so MLflow captures exactly which chunks were retrieved for each query. Then `mlflow.genai.evaluate()` with the `RetrievalRelevance` scorer uses an LLM judge to assess whether the retrieved chunks are relevant to the query.

**Why A is Wrong:** Manually logging a custom match percentage bypasses MLflow's built-in GenAI evaluation framework and provides a less insightful metric.

**Why C is Wrong:** A/B testing with click-through rate is a user behavioral metric, not a retrieval quality metric — it requires actual users, not a test dataset.

**Why D is Wrong:** Manually running a Spark JOIN requires significant custom code compared to the native `mlflow.genai.evaluate()` approach.

**Source:** Section 2: Data Preparation – Objective 6: Use tools and metrics to evaluate retrieval performance

```json
{
  "id": "S2Q007",
  "source": "DB-GenAI-S2",
  "concept": "Retrieval Evaluation – MLflow Tracing + RetrievalRelevance",
  "dimension": "Feature",
  "difficulty": "Intermediate",
  "question_type": "Scenario",
  "blueprint": "A",
  "taxonomy": "Apply",
  "answer": "B"
}
```

---

### Question 8
**Difficulty:** Intermediate
> **Blueprint:** B – Observed Metrics → Diagnosis
> **Concept:** Retrieval Metrics – Recall@k Definition
> **Dimension:** Definition

A RAG application retrieves the top-5 chunks (`k=5`) from Vector Search for each query. A developer wants to understand what `Recall@5` measures in this context and how to interpret a value of 0.6.

* **A)** `Recall@5` measures what fraction of the 5 retrieved chunks are relevant (relevant retrieved ÷ total retrieved), so 0.6 means 3 out of 5 retrieved chunks are relevant to the query. *(Distractor type: Common misconception — that describes Precision@k, not Recall@k)*
* **B)** `Recall@5` measures what fraction of ALL known relevant chunks were found in the top-5 results (relevant retrieved ÷ total relevant), so 0.6 means 60% of all relevant chunks exist in the top-5 results.
* **C)** `Recall@5` measures the average rank position of the first relevant chunk within the top-5 results, so 0.6 means the first relevant chunk appears at rank position 3 on a normalized 0-to-1 scale. *(Distractor type: Related technology — that describes MRR)*
* **D)** `Recall@5` measures the semantic similarity score of the 5th-ranked chunk to the query, so 0.6 means the least-relevant chunk in the top-5 has a cosine similarity of 0.6 to the query vector. *(Distractor type: Common misconception — Recall@k is about coverage, not similarity scores)*

**Correct Answer:** B

**Why B is Correct:** Recall@k = (number of relevant chunks retrieved in top-k) ÷ (total number of relevant chunks in the dataset). A Recall@5 of 0.6 means that out of all the chunks that are actually relevant to the query, 60% of them appear in the top-5 retrieved results.

**Why A is Wrong:** That definition describes Precision@k, not Recall@k. Precision@5 = (relevant retrieved) ÷ k.

**Why C is Wrong:** That describes Mean Reciprocal Rank (MRR), which measures the rank position of the first relevant result.

**Why D is Wrong:** That describes a raw similarity threshold, not a retrieval recall metric; Recall@k is about coverage of relevant documents, not individual similarity scores.

**Source:** Section 2: Data Preparation – Objective 6: Use tools and metrics to evaluate retrieval performance

```json
{
  "id": "S2Q008",
  "source": "DB-GenAI-S2",
  "concept": "Retrieval Metrics – Recall@k Definition",
  "dimension": "Definition",
  "difficulty": "Intermediate",
  "question_type": "Concept",
  "blueprint": "B",
  "taxonomy": "Understand",
  "answer": "B"
}
```

---

### Question 9
**Difficulty:** Intermediate
> **Blueprint:** A – Business Problem → Which Feature Solves It?
> **Concept:** Document Extraction – Multi-Format Pipeline
> **Dimension:** Feature

A developer needs to extract text from Word documents (`.docx`), HTML web pages, and regular text-based PDFs in a single unified pipeline on Databricks. They want a single Python library that handles all three formats and returns structured output (separating titles from body text). Which library is most appropriate?

* **A)** `PyPDF2` — because it supports cross-format parsing and automatically detects the file type from the file extension, switching between PDF, HTML, and Word parsing modes internally. *(Distractor type: Common misconception — PyPDF2 is PDF-only)*
* **B)** `pytesseract` — because it uses the underlying image rendering of all document types to extract text uniformly across PDFs, HTML, and Word documents. *(Distractor type: Beginner mistake — OCR is for image-based, not digital documents)*
* **C)** `unstructured` — because it is a multi-format document parsing library that handles PDFs, Word, HTML, and many other formats, returning structured elements (titles, narrative text, tables) from each format.
* **D)** `beautifulsoup4` — because it is format-agnostic and can parse the raw binary content of any file type, automatically recognizing Word, HTML, and PDF document structures. *(Distractor type: Common misconception — beautifulsoup4 is HTML/XML only)*

**Correct Answer:** C

**Why C is Correct:** `unstructured` is the go-to library for multi-format document ingestion in RAG pipelines. It natively supports `.docx`, `.html`, `.pdf`, and many other formats, and parses them into typed elements (e.g., `Title`, `NarrativeText`, `Table`) — making it ideal for pipelines that need both format flexibility and structured output.

**Why A is Wrong:** `PyPDF2` only handles PDF files; it has no capability to parse Word or HTML documents.

**Why B is Wrong:** `pytesseract` is an OCR library for image-based text; standard Word, HTML, and digital PDFs have embedded text layers that do not need OCR.

**Why D is Wrong:** `beautifulsoup4` is exclusively an HTML/XML parser; it cannot parse Word documents or PDFs.

**Source:** Section 2: Data Preparation – Objective 3: Choose the appropriate Python package to extract document content

```json
{
  "id": "S2Q009",
  "source": "DB-GenAI-S2",
  "concept": "Document Extraction – Multi-Format Pipeline",
  "dimension": "Feature",
  "difficulty": "Intermediate",
  "question_type": "Scenario",
  "blueprint": "A",
  "taxonomy": "Apply",
  "answer": "C"
}
```

---

### Question 10
**Difficulty:** Intermediate
> **Blueprint:** C – Architecture Need → Choose Architecture
> **Concept:** Vector Search – TRIGGERED vs. CONTINUOUS Sync Mode
> **Dimension:** Trade-off

A Databricks Vector Search index is configured with `pipeline_type="TRIGGERED"` and source table `main.docs.policy_chunks`. A developer updates 500 rows in the source Delta table. When will these updates appear in the Vector Search index?

* **A)** Immediately — because Delta Lake's ACID transactions ensure that all Vector Search indexes always reflect the current committed state of the source table in real time. *(Distractor type: Extreme statement — ACID applies at the Delta table level, not the derived index)*
* **B)** Within 5 seconds — because `TRIGGERED` mode uses Change Data Feed micro-batching with a default polling interval of 5 seconds to detect and apply changes from the source Delta table. *(Distractor type: Common misconception — that describes CONTINUOUS mode)*
* **C)** Only after a manual sync is triggered — either by calling `index.sync()` via the Python SDK or scheduling a sync via the Databricks Vector Search UI or REST API, since `TRIGGERED` mode does not auto-sync.
* **D)** At the next scheduled Vector Search maintenance window — because Databricks performs index synchronization during off-peak hours to avoid impacting production query performance. *(Distractor type: Common misconception — no automatic maintenance window exists)*

**Correct Answer:** C

**Why C is Correct:** `TRIGGERED` pipeline mode means the Vector Search index only updates when explicitly triggered by calling `index.sync()` (Python SDK), the REST API, or via the UI. Updates to the source Delta table are detected via Change Data Feed, but they do not automatically propagate to the index.

**Why A is Wrong:** Delta ACID transactions guarantee consistency at the Delta table level, not at the Vector Search index level; the index is a separate derived artifact.

**Why B is Wrong:** Micro-batch auto-polling is the behavior of `CONTINUOUS` pipeline mode, not `TRIGGERED` mode.

**Why D is Wrong:** There is no automatic maintenance window sync in Databricks Vector Search; all syncs in `TRIGGERED` mode are explicitly initiated by the developer.

**Source:** Section 2: Data Preparation – Objective 4: Define operations and sequence to write chunked text into Delta Lake

```json
{
  "id": "S2Q010",
  "source": "DB-GenAI-S2",
  "concept": "Vector Search – TRIGGERED vs. CONTINUOUS Sync Mode",
  "dimension": "Trade-off",
  "difficulty": "Intermediate",
  "question_type": "Scenario",
  "blueprint": "C",
  "taxonomy": "Understand",
  "answer": "C"
}
```

---

### Question 11
**Difficulty:** Advanced
> **Blueprint:** B – Observed Metrics → Diagnosis
> **Concept:** Chunking Strategy – Repetitive Document Language
> **Dimension:** Failure Mode

A developer applies fixed-size chunking with 512 tokens and 64-token overlap to a lengthy legal contract. They observe that the embeddings for consecutive chunks have very high cosine similarity (≥ 0.97), making it hard for the retriever to distinguish between adjacent chunks. What is the most likely root cause and the correct fix?

* **A)** The cosine similarity is high because the 64-token overlap introduces duplicate content in consecutive chunks; reducing the overlap to zero eliminates the shared content and creates more distinct embeddings. *(Distractor type: Partial truth — removing overlap reduces duplication but not the root cause)*
* **B)** The cosine similarity is high because legal contracts use highly repetitive boilerplate language (e.g., "the party of the first part shall…"); document-aware chunking by contract section boundaries will produce more semantically distinct chunks.
* **C)** The cosine similarity is high because the embedding model has not been fine-tuned on legal text; replacing the embedding model with a legal-domain-specific model will produce embeddings that better distinguish contract clauses. *(Distractor type: Common misconception — domain model doesn't fix structural repetitiveness)*
* **D)** The cosine similarity is high because 512 tokens is too small for legal text; increasing the chunk size to 2,048 tokens makes each chunk more contextually complete, reducing semantic overlap with neighboring chunks. *(Distractor type: Beginner mistake — larger chunks with same boilerplate still produce high similarity)*

**Correct Answer:** B

**Why B is Correct:** Legal contracts are densely repetitive — the same boilerplate phrases, party names, and legal constructions appear throughout. Fixed-size chunking cuts across this repeated structure arbitrarily, producing chunks that are semantically nearly identical. Document-aware chunking by contract section (e.g., "Section 4: Indemnification") produces semantically distinct chunks that are more differentiable.

**Why A is Wrong:** Reducing overlap to zero reduces the duplicate content between adjacent chunks but does not solve the root cause — boilerplate legal language across all sections still produces high similarity.

**Why C is Wrong:** While a legal-domain embedding model may perform better overall, the root cause here is the structural repetitiveness of the source document, not the embedding model's domain knowledge.

**Why D is Wrong:** Larger chunks include more context but the boilerplate density remains; you'd still get high similarity between large chunks filled with similar legal language.

**Source:** Section 2: Data Preparation – Objective 1 & 7: Chunking strategy and advanced chunking

```json
{
  "id": "S2Q011",
  "source": "DB-GenAI-S2",
  "concept": "Chunking Strategy – Repetitive Document Language",
  "dimension": "Failure Mode",
  "difficulty": "Advanced",
  "question_type": "Diagnosis",
  "blueprint": "B",
  "taxonomy": "Analyze",
  "answer": "B"
}
```

---

### Question 12
**Difficulty:** Advanced
> **Blueprint:** C – Architecture Need → Choose Architecture
> **Concept:** Advanced Chunking – Parent-Child Strategy
> **Dimension:** Architecture

A developer implements Parent-Child chunking for a RAG pipeline. Small "child" chunks (150 tokens) are embedded and stored in Vector Search. When a query matches a child chunk, the retriever fetches the corresponding "parent" chunk (1,000 tokens) to send to the LLM. What problem does this architecture solve compared to embedding large chunks directly?

* **A)** It reduces the total storage cost of the Vector Search index because only the small child embeddings are stored as vectors, while the large parent chunks remain as plain text in the Delta table without requiring vector storage. *(Distractor type: Partial truth — storage savings are a secondary benefit)*
* **B)** It solves the precision-context tradeoff: small child chunks produce precise, focused embeddings that match queries accurately (high precision retrieval), while the large parent chunks provide the LLM with sufficient surrounding context to generate a complete answer.
* **C)** It eliminates the need for Change Data Feed because parent chunks are static and never updated — only the child chunks require CDF-based synchronization with the Vector Search index. *(Distractor type: Common misconception — CDF is required whenever the source table updates)*
* **D)** It improves retrieval speed because the Vector Search index only needs to store a fraction of the data (child chunks), reducing index size and making approximate nearest neighbor search significantly faster. *(Distractor type: Partial truth — speed is a secondary benefit)*

**Correct Answer:** B

**Why B is Correct:** This is the exact problem Parent-Child chunking is designed to solve. Embedding large chunks directly produces "fuzzy" embeddings that mix many topics, making precise query matching harder. Small child chunks produce highly focused, precise embeddings that match specific query terms well. However, the LLM needs the larger parent chunk's rich context to generate a complete, well-grounded answer.

**Why A is Wrong:** While it is true that only child embeddings are vectorized, the primary motivation is retrieval precision and context richness, not storage cost reduction.

**Why C is Wrong:** CDF is required whenever the source Delta table is updated, regardless of whether parent or child chunks change.

**Why D is Wrong:** While a smaller index does improve search speed, this is a secondary benefit; the primary motivation is the precision-context tradeoff.

**Source:** Section 2: Data Preparation – Objective 7: Design retrieval systems using advanced chunking strategies

```json
{
  "id": "S2Q012",
  "source": "DB-GenAI-S2",
  "concept": "Advanced Chunking – Parent-Child Strategy",
  "dimension": "Architecture",
  "difficulty": "Advanced",
  "question_type": "Scenario",
  "blueprint": "C",
  "taxonomy": "Analyze",
  "answer": "B"
}
```

---

### Question 13
**Difficulty:** Advanced
> **Blueprint:** B – Observed Metrics → Diagnosis
> **Concept:** MLflow Tracing – RETRIEVER Span Requirement
> **Dimension:** Failure Mode

A developer uses `mlflow.genai.evaluate()` with a `RetrievalRelevance` scorer on a test dataset. The test queries are logged but the scorer returns all null scores. Investigation reveals the `@mlflow.trace(span_type="RETRIEVER")` decorator was not applied to the retrieval function. Why does this cause null scores, and what is the fix?

* **A)** Without the `RETRIEVER` span, MLflow's `RetrievalRelevance` scorer cannot identify which part of the trace corresponds to the retrieval step; it needs the typed span to know which inputs and outputs to pass to the LLM judge for scoring.
* **B)** Without the `RETRIEVER` span, the retrieval function runs synchronously instead of asynchronously, which causes a thread lock that prevents MLflow from recording any evaluation scores during the evaluation run. *(Distractor type: Common misconception — the span type is metadata, not a concurrency mechanism)*
* **C)** Without the `RETRIEVER` span, the evaluation function falls back to using the final LLM output instead of the retrieved chunks for scoring, which inflates the relevance scores to 1.0 rather than returning null. *(Distractor type: Common misconception — no fallback behavior exists)*
* **D)** Without the `RETRIEVER` span, MLflow cannot authenticate the retrieval function's calls to the Vector Search index, causing a permissions error that silently returns null scores instead of raising an exception. *(Distractor type: Common misconception — tracing and authentication are independent)*

**Correct Answer:** A

**Why A is Correct:** MLflow's `RetrievalRelevance` scorer finds retrieval data by looking for a trace span typed as `"RETRIEVER"`, which contains the query input and the retrieved documents as outputs. Without this typed span, MLflow cannot locate the retrieval step in the trace tree and has no data to pass to the LLM judge, resulting in null scores. The fix is to add `@mlflow.trace(span_type="RETRIEVER")` to the retrieval function.

**Why B is Wrong:** The `RETRIEVER` span type is metadata for MLflow's evaluation framework — it has no effect on whether the function runs synchronously or asynchronously.

**Why C is Wrong:** Without a RETRIEVER span, MLflow doesn't fall back to using LLM output; it simply cannot find the data it needs and produces nulls.

**Why D is Wrong:** MLflow tracing and Vector Search authentication are independent; the `RETRIEVER` decorator is an instrumentation call, not an authentication mechanism.

**Source:** Section 2: Data Preparation – Objective 6: Use tools and metrics to evaluate retrieval performance

```json
{
  "id": "S2Q013",
  "source": "DB-GenAI-S2",
  "concept": "MLflow Tracing – RETRIEVER Span Requirement",
  "dimension": "Failure Mode",
  "difficulty": "Advanced",
  "question_type": "Diagnosis",
  "blueprint": "B",
  "taxonomy": "Analyze",
  "answer": "A"
}
```

---

### Question 14
**Difficulty:** Advanced
> **Blueprint:** C – Architecture Need → Choose Architecture
> **Concept:** Delta Lake – CDF Enablement and Initial Snapshot
> **Dimension:** Architecture

A developer needs to enable Change Data Feed on a Delta table that already has 2 million existing rows before creating a Vector Search index. They run: `ALTER TABLE main.docs.chunks SET TBLPROPERTIES (delta.enableChangeDataFeed = true)`. Will the existing 2 million rows be synced to the Vector Search index when it is created?

* **A)** Yes — but only if the developer runs `OPTIMIZE TABLE main.docs.chunks` after enabling CDF, which compacts the existing data files and triggers CDF to generate historical change records for all rows. *(Distractor type: Common misconception — OPTIMIZE is for compaction, not CDF)*
* **B)** No — enabling CDF only captures future changes (inserts, updates, deletes) after the property is set. When the Vector Search index is created, it performs an initial full-table snapshot read of all existing rows to seed the index, then uses CDF for subsequent incremental updates.
* **C)** Yes — enabling CDF retroactively creates change records for all 2 million existing rows, which the Vector Search index reads during its first sync to populate the index with all historical data. *(Distractor type: Common misconception — CDF does not retroactively create historical records)*
* **D)** No — enabling CDF on an existing table has no effect on historical data; the Vector Search index will only contain rows that were inserted or updated AFTER CDF was enabled, leaving all 2 million existing rows out of the index. *(Distractor type: Common misconception — confuses CDF ongoing behavior with initial index seeding)*

**Correct Answer:** B

**Why B is Correct:** When a Vector Search index is created on a Delta table with CDF enabled, it performs an initial full-table snapshot read to seed the index with all existing rows. After this initial load, it uses CDF records to track only incremental changes going forward. This means all 2 million existing rows are correctly included in the index.

**Why A is Wrong:** `OPTIMIZE` is for file compaction and does not generate CDF records for historical data.

**Why C is Wrong:** Enabling CDF does not retroactively create CDF records for historical data — CDF records only begin from the transaction version when CDF is enabled. The existing rows are captured via the initial snapshot.

**Why D is Wrong:** This confuses CDF's ongoing behavior (capturing changes) with the index creation behavior (initial full snapshot). The initial snapshot reads all rows regardless of when CDF was enabled.

**Source:** Section 2: Data Preparation – Objective 4: Define operations and sequence to write chunked text into Delta Lake

```json
{
  "id": "S2Q014",
  "source": "DB-GenAI-S2",
  "concept": "Delta Lake – CDF Enablement and Initial Snapshot",
  "dimension": "Architecture",
  "difficulty": "Advanced",
  "question_type": "Scenario",
  "blueprint": "C",
  "taxonomy": "Analyze",
  "answer": "B"
}
```

---

### Question 15
**Difficulty:** Advanced
> **Blueprint:** C – Architecture Need → Choose Architecture
> **Concept:** Vector Search – Sync Pipeline Operational Design
> **Dimension:** Trade-off

A developer is building a RAG pipeline for a company that publishes new product release notes weekly. The existing Vector Search index uses `pipeline_type="TRIGGERED"` sync. The team wants to ensure the index reflects new release notes within 1 hour of publication to the Delta table. What is the most operationally efficient solution?

* **A)** Switch the Vector Search index sync pipeline to `CONTINUOUS` mode, which automatically propagates Delta table changes to the index in near-real-time without requiring any scheduled jobs or manual intervention. *(Distractor type: Partial truth — valid but more expensive for infrequent weekly updates)*
* **B)** Keep the `TRIGGERED` mode but deploy a Databricks Workflow job scheduled every 1 hour that calls `index.sync()` on the Vector Search index after new data is written to the source Delta table.
* **C)** Switch to `CONTINUOUS` mode and enable Delta Structured Streaming on the source table, which creates a push-based pipeline where new rows are streamed directly to the Vector Search index as they are committed. *(Distractor type: Common misconception — conflates two different Databricks technologies)*
* **D)** Keep `TRIGGERED` mode and configure a Databricks Alert on the source Delta table that sends an API call to `index.sync()` whenever new rows are detected, replacing the need for a scheduled job. *(Distractor type: Common misconception — Databricks Alerts are monitoring notifications, not API orchestrators)*

**Correct Answer:** B

**Why B is Correct:** For a 1-hour freshness SLA, a scheduled Workflow job that calls `index.sync()` every hour is the most straightforward and operationally efficient solution with `TRIGGERED` mode. This approach is cost-effective (sync only runs when scheduled, not continuously) and meets the SLA perfectly for a weekly update pattern.

**Why A is Wrong:** `CONTINUOUS` mode would also satisfy the SLA but is more expensive — it keeps the sync pipeline running continuously even when there are no changes, incurring ongoing compute cost for what is a weekly update pattern.

**Why C is Wrong:** `CONTINUOUS` mode uses CDF-based propagation internally — there is no separate "Delta Structured Streaming push" mechanism for Vector Search.

**Why D is Wrong:** Databricks Alerts are monitoring notifications (email, Slack) — they cannot directly call the `index.sync()` API.

**Source:** Section 2: Data Preparation – Objective 4: Define operations and sequence to write chunked text into Delta Lake

```json
{
  "id": "S2Q015",
  "source": "DB-GenAI-S2",
  "concept": "Vector Search – Sync Pipeline Operational Design",
  "dimension": "Trade-off",
  "difficulty": "Advanced",
  "question_type": "Scenario",
  "blueprint": "C",
  "taxonomy": "Evaluate",
  "answer": "B"
}
```

---

### Question 16
**Difficulty:** Proficiency
> **Blueprint:** B – Observed Metrics → Diagnosis
> **Concept:** Retrieval Evaluation – Ablation Study Methodology
> **Dimension:** Best Practice

A company ingests 10,000 long-form research papers (each averaging 8,000 tokens) into a RAG pipeline using fixed-size chunking with 512-token chunks and 50-token overlap. Retrieval quality (`Recall@5 = 0.41`) is low. An engineer proposes Parent-Child chunking as the fix. A second engineer argues that improving the embedding model is the right solution. How should the team evaluate which fix addresses the root cause?

* **A)** Run an ablation study: first replace the embedding model while keeping fixed-size chunking, then switch to Parent-Child chunking while keeping the original embedding model, and compare `Recall@5` for each change to determine which variable drives the improvement.
* **B)** Switch to Parent-Child chunking immediately because chunking strategy always has a larger impact on retrieval quality than embedding model selection for long-form documents, making further evaluation unnecessary. *(Distractor type: Extreme statement — no universal hierarchy exists)*
* **C)** Replace the embedding model first because embedding quality is always the primary bottleneck in RAG pipelines; chunking strategy is a secondary factor. *(Distractor type: Extreme statement — reverses B's claim without evidence)*
* **D)** Add more documents to the knowledge base to increase the probability that the correct chunk is retrieved, since low `Recall@5` always indicates a knowledge gap. *(Distractor type: Common misconception — confuses knowledge gap with retrieval architecture gap)*

**Correct Answer:** A

**Why A is Correct:** The correct engineering approach is an ablation study — isolating each variable (embedding model vs. chunking strategy) while holding the other constant, and measuring the impact on `Recall@5`. This produces evidence about which factor is the actual bottleneck without making unsupported assumptions.

**Why B is Wrong:** There is no universal rule that chunking always dominates over embedding quality — the relative importance depends on the specific content type, query patterns, and current setup.

**Why C is Wrong:** For the same reason as B but in the opposite direction — there is no universal hierarchy that embedding model always matters more than chunking.

**Why D is Wrong:** `Recall@5 = 0.41` means 41% of known relevant chunks are found in top-5 — the relevant content is in the index; the problem is the retrieval system's ability to surface it, not a gap in the knowledge base.

**Source:** Section 2: Data Preparation – Objective 6 & 7: Evaluate retrieval and advanced chunking

```json
{
  "id": "S2Q016",
  "source": "DB-GenAI-S2",
  "concept": "Retrieval Evaluation – Ablation Study Methodology",
  "dimension": "Best Practice",
  "difficulty": "Proficiency",
  "question_type": "Scenario",
  "blueprint": "B",
  "taxonomy": "Evaluate",
  "answer": "A"
}
```

---

### Question 17
**Difficulty:** Proficiency
> **Blueprint:** C – Architecture Need → Choose Architecture
> **Concept:** Re-ranking – Retrieval Pool Size Design Implication
> **Dimension:** Architecture

A re-ranking stage is added after Vector Search retrieval in a RAG pipeline. Vector Search returns the top-50 candidate chunks; the reranker scores all 50 and passes the top-5 to the LLM. A senior engineer says: "If the correct chunk isn't in the top-50 from Vector Search, the reranker cannot help." Is this statement accurate, and what design implication does it have?

* **A)** The statement is inaccurate — rerankers can retrieve additional chunks from the Vector Search index beyond the initial top-50 candidates if they detect that the top-50 set does not contain a high-confidence match. *(Distractor type: Common misconception — rerankers only score existing candidates)*
* **B)** The statement is accurate — the reranker only scores candidates already retrieved by Vector Search. If the relevant chunk is ranked 51st or lower by Vector Search, it is never seen by the reranker. The design implication is that the initial Vector Search `num_results` (retrieval pool size) must be large enough to include all likely relevant chunks before reranking.
* **C)** The statement is accurate — but this limitation is acceptable because Vector Search's approximate nearest neighbor algorithm guarantees that any chunk with cosine similarity above 0.7 to the query will always appear in the top-50 results. *(Distractor type: Common misconception — ANN algorithms provide no such guarantee)*
* **D)** The statement is inaccurate — rerankers use a different embedding space than Vector Search, so a chunk ranked 51st by Vector Search may rank 1st by the reranker; both systems are queried independently and their results are merged. *(Distractor type: Common misconception — reranker and Vector Search are not independent systems)*

**Correct Answer:** B

**Why B is Correct:** The reranker is a second-stage filter, not an independent retrieval system. It receives only the candidates that Vector Search already returned. If the correct chunk is ranked 51st by Vector Search — even by the smallest cosine similarity margin — the reranker never sees it and cannot rescue it. The design implication is that the initial retrieval pool (`num_results`) must be generously sized.

**Why A is Wrong:** Rerankers in standard RAG architectures do not make additional retrieval calls to the Vector Search index — they operate purely on the already-retrieved candidate set.

**Why C is Wrong:** Approximate nearest neighbor algorithms have no such guarantee — they trade some accuracy for speed.

**Why D is Wrong:** The reranker and Vector Search use different scoring mechanisms, but they are not independent retrieval systems — the reranker receives only the Vector Search output.

**Source:** Section 2: Data Preparation – Objective 8: Explain the role of re-ranking in the information retrieval process

```json
{
  "id": "S2Q017",
  "source": "DB-GenAI-S2",
  "concept": "Re-ranking – Retrieval Pool Size Design Implication",
  "dimension": "Architecture",
  "difficulty": "Proficiency",
  "question_type": "Scenario",
  "blueprint": "C",
  "taxonomy": "Evaluate",
  "answer": "B"
}
```

---

### Question 18
**Difficulty:** Proficiency
> **Blueprint:** B – Observed Metrics → Diagnosis
> **Concept:** Delta Lake – CDF Missing Error Root Cause
> **Dimension:** Failure Mode

A developer writes the following Spark code to prepare chunked data for Vector Search:

```python
df.write.format("delta").mode("overwrite").saveAsTable("main.docs.chunks")
```

Then creates the Vector Search index immediately. Three days later, 200 new chunks are added using `df_new.write.format("delta").mode("append").saveAsTable("main.docs.chunks")`. The developer triggers a Vector Search sync and expects the 200 new chunks to appear. Instead, the sync fails with a "Change Data Feed not enabled" error. What went wrong?

* **A)** The `mode("overwrite")` used in the initial write destroyed and recreated the Delta table, which resets all table properties including `delta.enableChangeDataFeed = true` if it was previously set. *(Distractor type: Partial truth — overwrite CAN reset properties with overwriteSchema, but not standard behavior)*
* **B)** The `mode("append")` used for the new chunks created a separate Delta table partition that is not covered by the CDF property set on the main table, requiring a separate CDF enable statement for the new partition. *(Distractor type: Common misconception — CDF is a table-level property covering all partitions)*
* **C)** CDF was never enabled on the table before or after the initial write; the developer forgot to run `ALTER TABLE main.docs.chunks SET TBLPROPERTIES (delta.enableChangeDataFeed = true)` before creating the Vector Search index.
* **D)** The Vector Search index requires CDF to be enabled on the Unity Catalog schema (`main.docs`), not on the individual table; the developer incorrectly applied CDF at the table level instead of the schema level. *(Distractor type: Common misconception — CDF is table-level, not schema-level)*

**Correct Answer:** C

**Why C is Correct:** The most likely root cause is that CDF was never enabled on the table. The code shown creates a Delta table but does not enable CDF. The Vector Search index was created without CDF being active, and when new data was appended and a sync was triggered, Vector Search detected the missing CDF property and threw the error. The fix is to run `ALTER TABLE main.docs.chunks SET TBLPROPERTIES (delta.enableChangeDataFeed = true)` after the initial table creation and before creating the index.

**Why A is Wrong:** In standard behavior, `overwrite` mode replaces data files but preserves table metadata and properties.

**Why B is Wrong:** Delta Lake CDF is a table-level property — it applies to all partitions of the table uniformly.

**Why D is Wrong:** Unity Catalog does not have a schema-level CDF setting; CDF is configured at the individual Delta table level.

**Source:** Section 2: Data Preparation – Objective 4: Define operations and sequence to write chunked text into Delta Lake

```json
{
  "id": "S2Q018",
  "source": "DB-GenAI-S2",
  "concept": "Delta Lake – CDF Missing Error Root Cause",
  "dimension": "Failure Mode",
  "difficulty": "Proficiency",
  "question_type": "Code",
  "blueprint": "B",
  "taxonomy": "Analyze",
  "answer": "C"
}
```

---

### Question 19
**Difficulty:** Proficiency
> **Blueprint:** B – Observed Metrics → Diagnosis
> **Concept:** Retrieval Metrics – Low Recall in High-Stakes Contexts
> **Dimension:** Trade-off

An enterprise RAG pipeline processes 500,000 legal documents. After filtering, chunking, and embedding, the `Precision@5 = 0.88` but `Recall@5 = 0.31`. A principal engineer states: "High precision with low recall is the worst failure mode for a legal RAG application." Why is low recall especially dangerous in this legal context, and what architectural change best addresses it?

* **A)** Low recall means the chatbot frequently returns verbose answers with too much retrieved context (88% of retrieved chunks are relevant, creating information overload for the LLM). *(Distractor type: Common misconception — misinterprets Precision@5 as information overload)*
* **B)** Low recall means the system retrieves 88% relevant chunks but misses 69% of all relevant legal information that exists in the knowledge base — in legal contexts, missing a relevant precedent, clause, or exception could lead to legally incorrect guidance; increasing `num_results` and adding a reranker improves recall without sacrificing precision.
* **C)** Low recall means 31% of all user queries fail to retrieve any results at all, which is dangerous because legal professionals receive empty answers for nearly 1 in 3 queries. *(Distractor type: Common misconception — misdefines Recall@k as a query failure rate)*
* **D)** Low recall indicates that the Delta table holding the chunks has a low Change Data Feed transaction log retention period, causing 69% of indexed chunks to expire and become unavailable to Vector Search queries. *(Distractor type: Related technology — CDF retention is unrelated to retrieval recall metrics)*

**Correct Answer:** B

**Why B is Correct:** `Recall@5 = 0.31` means that for each query, only 31% of all truly relevant chunks in the knowledge base are being found in the top-5 results. In legal RAG, missing relevant information is catastrophic: an overlooked contract clause, missed legal precedent, or unstated exception could lead to legally incorrect advice. The fix is to increase the retrieval pool (`num_results`) and apply a reranker to select the best 5 from a larger, higher-recall candidate set.

**Why A is Wrong:** High Precision@5 = 0.88 means 88% of what IS retrieved is relevant — this is not information overload but high precision retrieval; the problem is what's being missed.

**Why C is Wrong:** Recall@k does not measure the percentage of queries that return zero results; it measures coverage of known relevant documents within the top-k results.

**Why D is Wrong:** Recall@5 is a retrieval quality metric, not a Delta Lake storage metric; CDF log retention affects sync performance, not the retrieval recall of indexed content.

**Source:** Section 2: Data Preparation – Objective 6: Use tools and metrics to evaluate retrieval performance

```json
{
  "id": "S2Q019",
  "source": "DB-GenAI-S2",
  "concept": "Retrieval Metrics – Low Recall in High-Stakes Contexts",
  "dimension": "Trade-off",
  "difficulty": "Proficiency",
  "question_type": "Scenario",
  "blueprint": "B",
  "taxonomy": "Evaluate",
  "answer": "B"
}
```

---

### Question 20
**Difficulty:** Proficiency
> **Blueprint:** B – Observed Metrics → Diagnosis
> **Concept:** Re-ranking – Latency Optimization
> **Dimension:** Trade-off

A RAG pipeline uses the following two-stage retrieval: Vector Search retrieves top-100 chunks, then a cross-encoder reranker scores them and passes top-5 to the LLM. After deployment, latency is 4.2 seconds per query (SLA: 2 seconds). Profiling shows: Vector Search = 0.3s, reranker = 3.7s, LLM = 0.2s. The bottleneck is clear. What architectural change best reduces latency while maintaining retrieval quality?

* **A)** Replace the cross-encoder reranker with a second bi-encoder embedding model that scores all 100 chunks against the query using cosine similarity, which runs in parallel and is significantly faster than the cross-encoder. *(Distractor type: Common misconception — bi-encoder re-scoring defeats the purpose of precision reranking)*
* **B)** Reduce the Vector Search initial retrieval from top-100 to top-10, which gives the reranker only 10 chunks to score instead of 100, reducing reranker compute time by ~90% while accepting a small recall trade-off.
* **C)** Move the reranker to a dedicated Databricks Model Serving endpoint with GPU-backed autoscaling, so it processes all 100 chunks in parallel on GPU hardware rather than sequentially on CPU. *(Distractor type: Partial truth — GPU helps but may not meet SLA at 100 candidates)*
* **D)** Eliminate the reranker entirely and rely solely on Vector Search's cosine similarity ranking, reverting to the original retrieval approach and accepting the quality reduction as the only option within the latency constraint. *(Distractor type: Common misconception — eliminating is last resort; reducing candidates is better)*

**Correct Answer:** B

**Why B is Correct:** The reranker's 3.7s latency scales with the number of chunks it must score. Reducing the candidate pool from 100 to 10 reduces the reranker's work by ~90%, bringing estimated reranker time to ~0.37s and total latency to approximately 0.87s — well within the 2-second SLA. The trade-off is a modest decrease in recall which the team must validate.

**Why A is Wrong:** A second bi-encoder simply re-ranks using cosine similarity — it does not achieve the precision improvement of a cross-encoder. Using a bi-encoder for reranking defeats the purpose of the reranking stage.

**Why C is Wrong:** While GPU-backed serving would improve throughput, scoring 100 query-document pairs on GPU reduces latency somewhat but not by the ~85% needed to meet the 2-second SLA.

**Why D is Wrong:** Eliminating the reranker should be the last resort; reducing the candidate pool (option B) achieves the latency target while preserving much of the quality benefit of reranking.

**Source:** Section 2: Data Preparation – Objective 8: Explain the role of re-ranking in the information retrieval process

```json
{
  "id": "S2Q020",
  "source": "DB-GenAI-S2",
  "concept": "Re-ranking – Latency Optimization",
  "dimension": "Trade-off",
  "difficulty": "Proficiency",
  "question_type": "Diagnosis",
  "blueprint": "B",
  "taxonomy": "Evaluate",
  "answer": "B"
}
```

---

### Question 21
**Difficulty:** Beginner
> **Blueprint:** A – Business Problem → Which Feature Solves It?
> **Concept:** Chunking Strategy – Plain Prose Documents
> **Dimension:** Best Practice

A developer needs to split a 50-page PDF user manual into chunks for a RAG pipeline. The manual is written in continuous plain prose with no consistent heading structure. Which chunking method is most reliable given this document structure?

* **A)** Document-aware chunking using Markdown header boundaries — the splitter detects `#`, `##`, and `###` headers and uses them as split points to keep related sections together in each chunk. *(Distractor type: Common misconception — requires Markdown headers that don't exist in plain prose)*
* **B)** Fixed-size chunking with an appropriate token limit and small overlap — it splits the text at a consistent token count with overlap to avoid losing context at boundaries, regardless of document structure.
* **C)** Semantic chunking using a topic model — the chunker runs an LDA topic model on the full PDF and groups sentences by topic, placing all sentences with the same dominant topic into a single chunk. *(Distractor type: Beginner mistake — computationally expensive and non-standard)*
* **D)** Table-based chunking — the chunker detects table boundaries in the PDF and uses each table cell as a single chunk, which is appropriate for prose documents that lack explicit section headers. *(Distractor type: Common misconception — table-based chunking is for tabular data, not prose)*

**Correct Answer:** B

**Why B is Correct:** For a plain prose document with no consistent structural markers, document-aware or header-based chunking cannot find split points. Fixed-size chunking with overlap is the reliable fallback — it splits at a consistent token count and uses overlap to prevent losing context at chunk boundaries.

**Why A is Wrong:** Document-aware Markdown header chunking requires the document to actually have Markdown headers; a PDF with plain prose has no such headers.

**Why C is Wrong:** Running an LDA topic model as a chunking strategy is extremely computationally expensive and non-standard for production RAG pipelines.

**Why D is Wrong:** Table-based chunking is designed for documents with tabular data, not continuous prose.

**Source:** Section 2: Data Preparation – Objective 1: Apply a chunking strategy for a given document structure and model constraints

```json
{
  "id": "S2Q021",
  "source": "DB-GenAI-S2",
  "concept": "Chunking Strategy – Plain Prose Documents",
  "dimension": "Best Practice",
  "difficulty": "Beginner",
  "question_type": "Scenario",
  "blueprint": "A",
  "taxonomy": "Apply",
  "answer": "B"
}
```

---

### Question 22
**Difficulty:** Beginner
> **Blueprint:** A – Business Problem → Which Feature Solves It?
> **Concept:** Delta Lake – Primary Key Requirement for Vector Search
> **Dimension:** Feature

A developer is preparing a Delta table to serve as the source for a Databricks Vector Search index. They realize the table has no primary key column. Why is a unique `id` column required?

* **A)** The Vector Search index uses the `id` column as the vector embedding storage key, mapping each unique ID to its corresponding high-dimensional vector in the FAISS index file. *(Distractor type: Common misconception — id is a logical identifier, not the embedding storage key)*
* **B)** The `id` column is required so that Vector Search can uniquely identify each chunk during delta sync operations — specifically to detect which chunks have been updated or deleted and apply those changes incrementally.
* **C)** Unity Catalog enforces that all Delta tables used by AI services must have a primary key column for compliance auditing, so that the data lineage of each chunk can be traced back to its original document. *(Distractor type: Common misconception — the requirement is operational, not a governance policy)*
* **D)** The `id` column is used by the LLM at inference time to cite the exact source document and chunk position in its response, enabling automatic footnote generation in the chatbot's answers. *(Distractor type: Common misconception — citation is an application-layer feature, not driven by the id column)*

**Correct Answer:** B

**Why B is Correct:** Databricks Vector Search uses the `id` column to uniquely identify each row (chunk) in the source Delta table. During incremental sync operations, the Vector Search pipeline uses Change Data Feed records alongside the `id` to determine which specific rows have been inserted, updated, or deleted — and applies those changes to the index precisely.

**Why A is Wrong:** The `id` column is a logical identifier for the chunk, not the key used to store the embedding vector in the underlying vector storage.

**Why C is Wrong:** Unity Catalog does not require a primary key column for AI service compliance; the `id` requirement is a Vector Search operational requirement.

**Why D is Wrong:** The LLM does not use the `id` column from the Delta table at inference time; citation is a separate application-level feature.

**Source:** Section 2: Data Preparation – Objective 4: Define operations and sequence to write chunked text into Delta Lake

```json
{
  "id": "S2Q022",
  "source": "DB-GenAI-S2",
  "concept": "Delta Lake – Primary Key Requirement for Vector Search",
  "dimension": "Feature",
  "difficulty": "Beginner",
  "question_type": "Concept",
  "blueprint": "A",
  "taxonomy": "Understand",
  "answer": "B"
}
```

---

### Question 23
**Difficulty:** Beginner
> **Blueprint:** A – Business Problem → Which Feature Solves It?
> **Concept:** Content Filtering – Text Normalization After HTML Extraction
> **Dimension:** Best Practice

A developer uses `beautifulsoup4` to extract text from HTML pages. They run `soup.get_text()` and get back a string, but it contains many unwanted newlines, tab characters, and whitespace runs from the original HTML formatting. What should they do before writing this text to a Delta table for chunking?

* **A)** Re-parse the HTML with `pytesseract` OCR after rendering the page to an image, which produces cleaner text by re-reading the visual characters rather than the raw HTML source text. *(Distractor type: Beginner mistake — OCR is lossy and unnecessary for digital HTML)*
* **B)** Apply string cleaning operations — strip leading/trailing whitespace, collapse multiple consecutive whitespace characters, and remove newlines from within sentences — to normalize the extracted text.
* **C)** Write the raw uncleaned text to the Delta table and rely on the embedding model to normalize whitespace during the vectorization process, since embedding models ignore whitespace tokens. *(Distractor type: Common misconception — embedding models do NOT normalize whitespace)*
* **D)** Convert the HTML to PDF first using `pdfkit`, then use `PyPDF2` to extract clean text, which strips HTML formatting artifacts and produces uniform paragraph text automatically. *(Distractor type: Beginner mistake — unnecessary multi-step conversion)*

**Correct Answer:** B

**Why B is Correct:** After extracting raw text from HTML using `soup.get_text()`, the output typically contains formatting artifacts from the original HTML structure — excessive newlines, tabs, and whitespace runs. Standard text cleaning (using Python's `str.strip()`, `re.sub(r'\s+', ' ', text)`, and similar operations) normalizes the text before chunking and embedding, ensuring cleaner, higher-quality chunks.

**Why A is Wrong:** Converting a text-based HTML page to an image and running OCR is a wasteful, lossy approach.

**Why C is Wrong:** Embedding models do NOT normalize whitespace — they tokenize the input as-is, and excessive whitespace tokens reduce the effective content density of the embedding.

**Why D is Wrong:** HTML → PDF → text extraction is a multi-step conversion that adds complexity and potential content loss.

**Source:** Section 2: Data Preparation – Objective 2: Filter extraneous content in source documents

```json
{
  "id": "S2Q023",
  "source": "DB-GenAI-S2",
  "concept": "Content Filtering – Text Normalization After HTML Extraction",
  "dimension": "Best Practice",
  "difficulty": "Beginner",
  "question_type": "Scenario",
  "blueprint": "A",
  "taxonomy": "Apply",
  "answer": "B"
}
```

---

### Question 24
**Difficulty:** Beginner
> **Blueprint:** A – Business Problem → Which Feature Solves It?
> **Concept:** Document Extraction – Word Document Parsing
> **Dimension:** Feature

A team has a collection of `.docx` Word documents that they want to parse for a RAG pipeline. Which Python library is most appropriate for extracting text content from Word documents on Databricks?

* **A)** `beautifulsoup4` — because Word documents are internally structured as ZIP archives containing XML files, and BeautifulSoup can parse XML to extract text from the document body elements. *(Distractor type: Partial truth — technically possible but requires manual namespace handling; unstructured is superior)*
* **B)** `pytesseract` — because Word documents are often printed and scanned, making OCR the standard text extraction approach for this document format in enterprise pipelines. *(Distractor type: Common misconception — standard .docx files have embedded digital text, not scanned images)*
* **C)** `unstructured` — because it natively supports `.docx` Word document parsing, extracting text with structural awareness (distinguishing headings from body text) without requiring manual XML parsing.
* **D)** `PyPDF2` — because Word documents and PDF files use the same underlying binary format, and PyPDF2's universal document reader handles both `.pdf` and `.docx` file extensions. *(Distractor type: Common misconception — Word and PDF are completely different binary formats)*

**Correct Answer:** C

**Why C is Correct:** The `unstructured` library is the recommended multi-format document parsing tool for RAG pipelines. It natively reads `.docx` files using the python-docx backend and returns structured elements (Title, NarrativeText, Table, etc.), making it easy to filter and process different content types.

**Why A is Wrong:** While Word's `.docx` format is internally XML, using `beautifulsoup4` requires significant manual handling of namespace prefixes and schema knowledge; `unstructured` abstracts this complexity.

**Why B is Wrong:** `.docx` files contain embedded digital text — OCR is only needed for scanned image files where no digital text layer exists.

**Why D is Wrong:** Word and PDF are completely different binary formats; `PyPDF2` can only read PDF files.

**Source:** Section 2: Data Preparation – Objective 3: Choose the appropriate Python package

```json
{
  "id": "S2Q024",
  "source": "DB-GenAI-S2",
  "concept": "Document Extraction – Word Document Parsing",
  "dimension": "Feature",
  "difficulty": "Beginner",
  "question_type": "Scenario",
  "blueprint": "A",
  "taxonomy": "Remember",
  "answer": "C"
}
```

---

### Question 25
**Difficulty:** Beginner
> **Blueprint:** A – Business Problem → Which Feature Solves It?
> **Concept:** Knowledge Base Curation – Informal vs. Authoritative Sources
> **Dimension:** Best Practice

A developer is curating documents for a customer support RAG chatbot. They have access to: (A) official product FAQs updated monthly, (B) internal Slack message threads from the support team, and (C) competitor product reviews from public websites. Which documents should be excluded, and why?

* **A)** Exclude source A (official FAQs) because monthly updates mean the information is stale for 30 days; real-time Slack threads (source B) provide more current information for customer queries. *(Distractor type: Common misconception — recency does not override authority and accuracy)*
* **B)** Exclude sources B and C — Slack threads contain informal, unverified, and potentially incorrect troubleshooting advice, and competitor reviews introduce off-topic and potentially misleading information into the knowledge base.
* **C)** Include all three sources to maximize knowledge breadth; the LLM will automatically disregard low-quality content from Slack threads and competitor reviews when generating answers for customer queries. *(Distractor type: Extreme statement — LLMs cannot reliably ignore retrieved context)*
* **D)** Exclude source A (official FAQs) and include only sources B and C because the chatbot needs to understand real-world customer language patterns, which Slack threads and public reviews provide more authentically. *(Distractor type: Common misconception — language patterns are a training concern, not a knowledge base concern)*

**Correct Answer:** B

**Why B is Correct:** Slack threads (B) contain informal, unverified advice — support agents may share workarounds, incorrect steps, or personal opinions that are not official guidance. Competitor product reviews (C) are entirely off-topic for a customer support chatbot. Only the official FAQs (A) provide verified, authoritative, on-topic content.

**Why A is Wrong:** Monthly-updated official FAQs are authoritative — even if 30 days old, they represent the current official guidance. Slack threads are NOT more reliable simply because they are more recent.

**Why C is Wrong:** LLMs cannot reliably "ignore" retrieved context that they are given.

**Why D is Wrong:** Understanding customer language patterns is a training-time concern for the LLM, not a knowledge base curation decision.

**Source:** Section 2: Data Preparation – Objective 5: Identify needed source documents

```json
{
  "id": "S2Q025",
  "source": "DB-GenAI-S2",
  "concept": "Knowledge Base Curation – Informal vs. Authoritative Sources",
  "dimension": "Best Practice",
  "difficulty": "Beginner",
  "question_type": "Scenario",
  "blueprint": "A",
  "taxonomy": "Evaluate",
  "answer": "B"
}
```

---

### Question 26
**Difficulty:** Intermediate
> **Blueprint:** B – Observed Metrics → Diagnosis
> **Concept:** Chunking Strategy – Minimum Chunk Size Filtering
> **Dimension:** Failure Mode

A developer uses recursive character text splitting on a 200-page technical manual. They set `chunk_size=400` tokens and `chunk_overlap=40` tokens. They observe that some chunks contain only 15–20 tokens (mostly section titles that appear alone after a split). What is the impact of these tiny chunks on the RAG pipeline, and what is the fix?

* **A)** Tiny chunks improve retrieval precision because the embedding model can produce highly focused embeddings for short, specific text; the developer should keep them and reduce `chunk_size` further. *(Distractor type: Common misconception — very short chunks are too low-information to be useful)*
* **B)** Tiny chunks create poor embeddings that are underrepresented in the vector space — their embedding captures only a heading with minimal semantic content, meaning they will consume a top-k retrieval slot while providing almost no useful context to the LLM. The fix is to set a `min_chunk_size` threshold to merge or discard chunks below a minimum token count.
* **C)** Tiny chunks only affect the storage cost of the Delta table since each row occupies a fixed storage overhead regardless of text length; they have no meaningful impact on retrieval quality or LLM answer generation. *(Distractor type: Common misconception — tiny chunks DO affect retrieval quality)*
* **D)** Tiny chunks cause the Vector Search index to fail during sync because the embedding model raises an error when it receives fewer than 50 tokens as input, rejecting the chunk and preventing it from being added to the index. *(Distractor type: Common misconception — embedding models accept any valid text string length)*

**Correct Answer:** B

**Why B is Correct:** A chunk containing only a section heading like "Chapter 4: Configuration" has minimal semantic content — its embedding is essentially a representation of a header phrase, not of any knowledge. When retrieved, it provides almost no useful context for the LLM, yet it occupies one of the precious top-k retrieval slots. The fix is to apply a `min_chunk_size` filter (e.g., 50 tokens) that either merges tiny chunks with the next chunk or discards them.

**Why A is Wrong:** There is a meaningful lower bound below which chunk size hurts quality rather than helping precision — a 15-token heading phrase simply lacks content.

**Why C is Wrong:** Tiny chunks do meaningfully impact retrieval quality by occupying retrieval slots with low-information-content embeddings.

**Why D is Wrong:** Embedding models accept input strings of any length down to a single token; they do not raise errors for short inputs.

**Source:** Section 2: Data Preparation – Objective 1: Apply a chunking strategy

```json
{
  "id": "S2Q026",
  "source": "DB-GenAI-S2",
  "concept": "Chunking Strategy – Minimum Chunk Size Filtering",
  "dimension": "Failure Mode",
  "difficulty": "Intermediate",
  "question_type": "Diagnosis",
  "blueprint": "B",
  "taxonomy": "Analyze",
  "answer": "B"
}
```

---

### Question 27
**Difficulty:** Intermediate
> **Blueprint:** B – Observed Metrics → Diagnosis
> **Concept:** Retrieval Metrics – Precision vs. Recall Priority
> **Dimension:** Trade-off

A team uses `mlflow.genai.evaluate()` to assess retrieval quality and gets `Precision@5 = 0.76` and `Recall@5 = 0.52`. The product manager asks which metric is more important for a customer-facing medical symptom checker chatbot. What is the correct reasoning?

* **A)** Precision@5 is more important because the medical chatbot must never return irrelevant information — a hallucinated medical fact from an off-topic chunk could cause the user to make a dangerous health decision. *(Distractor type: Partial truth — precision matters, but missing critical info is more dangerous)*
* **B)** Recall@5 is more important because missing a relevant medical document (e.g., a critical drug interaction warning) is more dangerous than retrieving a slightly off-topic chunk; the chatbot must ensure it surfaces all relevant medical information.
* **C)** Both metrics are equally important and must both reach 1.0 before a medical chatbot can be deployed; partial retrieval quality is not acceptable in any medical application context. *(Distractor type: Extreme statement — perfect scores are not achievable in real-world systems)*
* **D)** Neither metric is relevant for a medical chatbot; the correct metric is `AnswerCorrectness`, which measures whether the final LLM response is factually correct, not whether individual retrieved chunks are relevant. *(Distractor type: Common misconception — retrieval metrics and answer metrics measure different things and both matter)*

**Correct Answer:** B

**Why B is Correct:** In a medical context, missing relevant information (low recall) is the more dangerous failure mode. A missed drug interaction warning or contraindication could lead a user to make an unsafe decision. Retrieving a slightly off-topic chunk (lower precision) is less dangerous because the LLM is less likely to synthesize irrelevant text into a harmful answer. This is a classic recall vs. precision prioritization based on asymmetry of error consequences.

**Why A is Wrong:** While precision matters, the medical context prioritizes not missing critical information over not retrieving irrelevant information — the asymmetry of harm favors recall.

**Why C is Wrong:** Perfect scores (1.0) are not achievable in real-world RAG systems; setting 1.0 as a deployment criterion is impractical.

**Why D is Wrong:** Retrieval metrics and answer metrics both matter and measure different things; dismissing retrieval metrics is incorrect — poor retrieval directly causes poor answer quality.

**Source:** Section 2: Data Preparation – Objective 6: Use tools and metrics to evaluate retrieval performance

```json
{
  "id": "S2Q027",
  "source": "DB-GenAI-S2",
  "concept": "Retrieval Metrics – Precision vs. Recall Priority",
  "dimension": "Trade-off",
  "difficulty": "Intermediate",
  "question_type": "Scenario",
  "blueprint": "B",
  "taxonomy": "Evaluate",
  "answer": "B"
}
```

---

### Question 28
**Difficulty:** Intermediate
> **Blueprint:** C – Architecture Need → Choose Architecture
> **Concept:** Vector Search – CONTINUOUS Sync Prerequisite
> **Dimension:** Architecture

A developer wants to ensure that when the source Delta table `main.docs.policy_chunks` is updated with new policy documents, the changes propagate to the Vector Search index automatically without manual intervention. They configure the Vector Search index with `pipeline_type="CONTINUOUS"`. What prerequisite must be met on the source Delta table?

* **A)** The source Delta table must be partitioned by the `document_date` column so that the CONTINUOUS sync pipeline can efficiently identify which partitions contain new data during each micro-batch scan. *(Distractor type: Common misconception — partitioning is a query optimization, not a Vector Search sync prerequisite)*
* **B)** The source Delta table must have Change Data Feed enabled (`delta.enableChangeDataFeed = true`) so the CONTINUOUS sync pipeline can read the incremental change records and propagate only the new, updated, or deleted rows.
* **C)** The source Delta table must be registered in the Hive metastore (not Unity Catalog) because CONTINUOUS sync mode only supports Hive metastore tables. *(Distractor type: Common misconception — Unity Catalog is fully supported and recommended)*
* **D)** The source Delta table must be stored on Azure Data Lake Storage Gen2 or AWS S3, because CONTINUOUS sync mode requires a cloud object storage backend; local cluster storage (DBFS root) is not supported for real-time sync pipelines. *(Distractor type: Common misconception — the prerequisite is CDF, not storage backend)*

**Correct Answer:** B

**Why B is Correct:** Databricks Vector Search CONTINUOUS sync uses Change Data Feed to detect and propagate changes from the source Delta table in near-real-time. Without CDF enabled on the source table, the sync pipeline has no mechanism to detect incremental changes and will fail. CDF must be enabled before the Vector Search index is created.

**Why A is Wrong:** Partitioning by date is a query optimization for analytics, not a prerequisite for Vector Search sync.

**Why C is Wrong:** Databricks Vector Search fully supports Unity Catalog-managed Delta tables — Unity Catalog is in fact the recommended governance layer.

**Why D is Wrong:** CONTINUOUS sync requirements relate to CDF (a Delta Lake feature) and Unity Catalog governance, not to specific cloud storage backends.

**Source:** Section 2: Data Preparation – Objective 4: Define operations and sequence to write chunked text into Delta Lake

```json
{
  "id": "S2Q028",
  "source": "DB-GenAI-S2",
  "concept": "Vector Search – CONTINUOUS Sync Prerequisite",
  "dimension": "Architecture",
  "difficulty": "Intermediate",
  "question_type": "Scenario",
  "blueprint": "C",
  "taxonomy": "Apply",
  "answer": "B"
}
```

---

### Question 29
**Difficulty:** Intermediate
> **Blueprint:** A – Business Problem → Which Feature Solves It?
> **Concept:** Vector Search – Metadata Filtering for Domain Isolation
> **Dimension:** Best Practice

A developer is building a RAG pipeline for a company that sells both software products and hardware products. The knowledge base contains 50,000 chunks covering both product lines. Users sometimes ask software questions but retrieve hardware documentation and vice versa. What data preparation change best addresses this cross-contamination problem?

* **A)** Increase the Vector Search index `num_results` to 20 so the correct chunks from the right product line are more likely to appear somewhere in the retrieved set before passing them to the LLM. *(Distractor type: Common misconception — more results retrieves more from both product lines, worsening cross-contamination)*
* **B)** Add a `product_line` metadata column (`software` or `hardware`) to each chunk in the source Delta table, and apply metadata filtering at query time so each query only searches within the relevant product line's chunks.
* **C)** Train a custom fine-tuned embedding model on combined software and hardware documentation so the embedding space naturally separates the two product domains and reduces cross-domain retrieval confusion. *(Distractor type: Beginner mistake — expensive and imprecise when metadata filtering is available)*
* **D)** Create two separate Databricks workspaces — one for the software knowledge base and one for the hardware knowledge base — routing user queries to the appropriate workspace based on keyword matching. *(Distractor type: Beginner mistake — excessive engineering overhead)*

**Correct Answer:** B

**Why B is Correct:** Adding a `product_line` metadata filter is the most targeted and operationally efficient fix. Databricks Vector Search supports metadata filtering — you can add a column (e.g., `product_line: string`) to the source Delta table and pass a filter expression at query time to restrict the search to only relevant chunks. This eliminates cross-contamination without requiring model retraining or architectural changes.

**Why A is Wrong:** Increasing `num_results` retrieves more chunks but does not filter by product line — you'd get more chunks from both product lines.

**Why C is Wrong:** Fine-tuning a custom embedding model is an expensive, time-consuming process; metadata filtering achieves the same result with zero training cost.

**Why D is Wrong:** Splitting into two workspaces is extreme engineering overhead — separate Unity Catalog schemas or separate Vector Search indexes within one workspace achieve the same isolation far more efficiently.

**Source:** Section 2: Data Preparation – Objective 5: Identify needed source documents

```json
{
  "id": "S2Q029",
  "source": "DB-GenAI-S2",
  "concept": "Vector Search – Metadata Filtering for Domain Isolation",
  "dimension": "Best Practice",
  "difficulty": "Intermediate",
  "question_type": "Scenario",
  "blueprint": "A",
  "taxonomy": "Apply",
  "answer": "B"
}
```

---

### Question 30
**Difficulty:** Intermediate
> **Blueprint:** A – Business Problem → Which Feature Solves It?
> **Concept:** MLflow Tracing – RETRIEVER Span Content
> **Dimension:** Feature

A developer instruments their RAG retrieval function with `@mlflow.trace(span_type="RETRIEVER")`. When they inspect the captured trace in the MLflow UI, what information appears in this span?

* **A)** The span shows the LLM's generated response along with the confidence scores that the LLM internally assigned to each retrieved chunk when deciding how much weight to give each document. *(Distractor type: Common misconception — LLMs do not expose internal per-chunk confidence scores)*
* **B)** The span shows the query vector (the numerical embedding array) that was sent to the Vector Search index and the raw cosine similarity scores of the top-k matching embeddings. *(Distractor type: Common misconception — the span captures text-level inputs/outputs, not raw embedding vectors)*
* **C)** The span shows the input query string, the retrieved document chunks (text content and metadata), and timing information — allowing MLflow evaluators to assess what the retriever received and returned.
* **D)** The span shows the Delta table transaction log entries that were read during the retrieval, including the CDF records that indicate which rows were recently updated in the source table. *(Distractor type: Common misconception — the span captures application-level retrieval data, not database transaction logs)*

**Correct Answer:** C

**Why C is Correct:** The `RETRIEVER` span type in MLflow Tracing captures the inputs and outputs of the retrieval step as structured metadata in the trace tree. Specifically, it records the input (the user query string), the outputs (the retrieved document chunks, including their text content and metadata such as `doc_id`, `source`, similarity score), and timing information. MLflow's `RetrievalRelevance` scorer then reads these captured inputs/outputs from the span to perform evaluation.

**Why A is Wrong:** LLMs do not expose internal confidence scores per retrieved document.

**Why B is Wrong:** The `RETRIEVER` span captures the text-level inputs and outputs for evaluation purposes — it does not expose the raw numerical embedding vector or internal cosine similarity computations.

**Why D is Wrong:** The `RETRIEVER` span captures the RAG pipeline's retrieval step inputs/outputs, not the underlying Delta table transaction log.

**Source:** Section 2: Data Preparation – Objective 6: Use tools and metrics to evaluate retrieval performance

```json
{
  "id": "S2Q030",
  "source": "DB-GenAI-S2",
  "concept": "MLflow Tracing – RETRIEVER Span Content",
  "dimension": "Feature",
  "difficulty": "Intermediate",
  "question_type": "Concept",
  "blueprint": "A",
  "taxonomy": "Understand",
  "answer": "C"
}
```

---

### Question 31
**Difficulty:** Advanced
> **Blueprint:** C – Architecture Need → Choose Architecture
> **Concept:** Advanced Chunking – Two-Level Splitting for Oversized Sections
> **Dimension:** Architecture

A developer applies document-aware chunking to a Markdown knowledge base. Articles are split on `##` headers. One article's section titled "## Troubleshooting" contains 4,200 tokens — far exceeding the 512-token embedding model limit. What is the correct approach to handle this oversized section?

* **A)** Skip the "Troubleshooting" section entirely and exclude it from the knowledge base because sections exceeding the embedding model limit cannot be ingested without data loss. *(Distractor type: Common misconception — skipping loses potentially critical knowledge)*
* **B)** Apply a two-level chunking strategy: use header-based splitting at the `##` level first, then apply recursive character splitting on any resulting chunk that exceeds 512 tokens, preserving header-level structure where possible.
* **C)** Increase the embedding model's token limit by setting a `max_tokens=4200` parameter in the embedding model API call, which instructs the model to expand its context window for this specific oversized section. *(Distractor type: Common misconception — embedding model context windows are fixed by architecture)*
* **D)** Replace the document-aware chunker with a single global fixed-size chunker set to 4,200 tokens across the entire knowledge base so that the largest section fits within one chunk. *(Distractor type: Beginner mistake — breaks all other sections in the knowledge base)*

**Correct Answer:** B

**Why B is Correct:** A two-level approach handles this gracefully: first split on `##` headers to preserve section-level structure, then apply recursive character splitting to any section that exceeds the 512-token limit to bring it within bounds. This preserves as much semantic structure as possible while respecting the hard model constraint.

**Why A is Wrong:** Skipping entire sections means losing potentially critical knowledge — the troubleshooting section is likely highly relevant to user queries.

**Why C is Wrong:** Embedding model context windows are fixed by the model architecture; there is no `max_tokens` parameter that expands the model's capacity at inference time.

**Why D is Wrong:** Setting a 4,200-token chunk size breaks all other sections in the knowledge base and causes most sections to vastly exceed the 512-token embedding limit.

**Source:** Section 2: Data Preparation – Objective 1 & 7: Chunking strategy and advanced chunking

```json
{
  "id": "S2Q031",
  "source": "DB-GenAI-S2",
  "concept": "Advanced Chunking – Two-Level Splitting for Oversized Sections",
  "dimension": "Architecture",
  "difficulty": "Advanced",
  "question_type": "Scenario",
  "blueprint": "C",
  "taxonomy": "Apply",
  "answer": "B"
}
```

---

### Question 32
**Difficulty:** Advanced
> **Blueprint:** B – Observed Metrics → Diagnosis
> **Concept:** Advanced Chunking – Parent-Child Context Delivery Flaw
> **Dimension:** Failure Mode

A RAG evaluation shows `Precision@5 = 0.94` but the LLM is still generating answers with hallucinations and missing important details. The retrieved chunks are highly relevant but engineers discover the LLM context window only receives ~400 tokens per query (limited by the 5 small child chunks of ~80 tokens each in a Parent-Child setup). What is the architectural fix?

* **A)** Reduce the number of retrieved chunks from 5 to 2 to concentrate the LLM's attention on the most relevant content, which reduces hallucinations by minimizing the amount of context the LLM must process. *(Distractor type: Common misconception — reducing chunks further reduces context, exacerbating the problem)*
* **B)** Switch from Parent-Child chunking to pure small-chunk retrieval, removing the parent chunk fetching step to reduce context size and make the LLM rely more on its parametric knowledge for complete answers. *(Distractor type: Common misconception — removes the architectural benefit entirely)*
* **C)** The child chunks are correctly retrieved (high precision), but the LLM receives only child-level context (80 tokens each). The fix is to implement the Parent-Child fetch correctly — retrieve parent chunks (~500–1,000 tokens) corresponding to the matched children, providing richer context to the LLM.
* **D)** Add more Vector Search metadata filters to narrow the retrieval set further, which reduces the number of chunks from 5 to 1–2 and forces the LLM to focus exclusively on the single most relevant passage. *(Distractor type: Common misconception — further narrowing reduces coverage and context)*

**Correct Answer:** C

**Why C is Correct:** High Precision@5 confirms the right child chunks are being found. But if only the small child chunks (80 tokens) are passed to the LLM, the LLM lacks sufficient surrounding context for complete answers. The correct implementation fetches the parent chunk (500–1,000 tokens) corresponding to each matched child chunk and sends those parent chunks to the LLM instead.

**Why A is Wrong:** Reducing from 5 to 2 chunks reduces the amount of context even further, exacerbating the problem.

**Why B is Wrong:** Removing the parent chunk step means losing the architectural benefit entirely — without parent chunks, the LLM still only gets 80-token child chunks.

**Why D is Wrong:** Further narrowing to 1–2 chunks reduces context coverage and increases the risk of missing important details.

**Source:** Section 2: Data Preparation – Objective 7: Design retrieval systems using advanced chunking strategies

```json
{
  "id": "S2Q032",
  "source": "DB-GenAI-S2",
  "concept": "Advanced Chunking – Parent-Child Context Delivery Flaw",
  "dimension": "Failure Mode",
  "difficulty": "Advanced",
  "question_type": "Diagnosis",
  "blueprint": "B",
  "taxonomy": "Analyze",
  "answer": "C"
}
```

---

### Question 33
**Difficulty:** Advanced
> **Blueprint:** B – Observed Metrics → Diagnosis
> **Concept:** Retrieval Evaluation – RetrievalRelevance vs. Factual Accuracy
> **Dimension:** Definition

A developer runs `mlflow.genai.evaluate()` on a RAG pipeline and gets `RetrievalRelevance = 0.89`. They present this to a stakeholder who asks: "Does this mean 89% of our retrieved chunks are factually correct?" How should the developer respond?

* **A)** Yes — `RetrievalRelevance = 0.89` means that the LLM judge confirmed 89% of the retrieved chunks contain factually accurate information verified against an external truth source. *(Distractor type: Common misconception — RetrievalRelevance measures topical relevance, not factual accuracy)*
* **B)** No — `RetrievalRelevance` measures whether retrieved chunks are relevant to the user's query (topically related), not whether their content is factually correct. A chunk can be highly relevant (about the right topic) but contain outdated or incorrect facts.
* **C)** Yes — `RetrievalRelevance` uses an LLM judge that cross-references each retrieved chunk against a verified ground-truth database, so a score of 0.89 confirms 89% of chunks are both relevant and factually verified. *(Distractor type: Common misconception — no ground-truth database is consulted)*
* **D)** No — `RetrievalRelevance = 0.89` means that 89% of all the chunks in the Vector Search index (not just retrieved chunks) are relevant to the total set of queries in the evaluation dataset. *(Distractor type: Common misconception — RetrievalRelevance measures retrieved chunks for specific queries, not the entire index)*

**Correct Answer:** B

**Why B is Correct:** `RetrievalRelevance` is a topical relevance metric — the LLM judge assesses whether each retrieved chunk is about the right topic relative to the user's query. It does not verify factual accuracy. A chunk about "password reset procedures" is highly relevant to a "how do I reset my password?" query even if the reset steps described are outdated and incorrect. Factual correctness is measured by different metrics (e.g., `AnswerCorrectness` with ground truth, or `Groundedness`).

**Why A is Wrong:** `RetrievalRelevance` does not perform factual verification — it only assesses topical relevance using an LLM judge that has no access to an external ground-truth database.

**Why C is Wrong:** For the same reason as A — no ground-truth database is consulted during `RetrievalRelevance` scoring.

**Why D is Wrong:** `RetrievalRelevance` measures the quality of retrieved chunks for specific queries in the evaluation set, not the overall relevance of all chunks in the entire index.

**Source:** Section 2: Data Preparation – Objective 6: Use tools and metrics to evaluate retrieval performance

```json
{
  "id": "S2Q033",
  "source": "DB-GenAI-S2",
  "concept": "Retrieval Evaluation – RetrievalRelevance vs. Factual Accuracy",
  "dimension": "Definition",
  "difficulty": "Advanced",
  "question_type": "Concept",
  "blueprint": "B",
  "taxonomy": "Understand",
  "answer": "B"
}
```

---

### Question 34
**Difficulty:** Advanced
> **Blueprint:** B – Observed Metrics → Diagnosis
> **Concept:** Content Filtering – Over-Aggressive Tag Removal
> **Dimension:** Failure Mode

A developer filters extraneous content from HTML documents using BeautifulSoup. Their cleaning function removes all `<nav>`, `<footer>`, `<header>`, and `<aside>` tags. During evaluation, users report the chatbot cannot answer questions about table data from the source HTML pages. Investigation reveals the HTML tables are being stripped. What went wrong?

* **A)** BeautifulSoup's `get_text()` method automatically strips all HTML table content (`<table>`, `<tr>`, `<td>` tags) regardless of the developer's filter configuration, converting tables to empty strings. *(Distractor type: Common misconception — get_text() does extract table text; the issue is in custom filtering code)*
* **B)** The developer's filter is too broad — their code likely removes all tags rather than only the specified structural tags, stripping `<table>` elements along with the navigation and footer elements they intended to remove.
* **C)** HTML tables require a separate `pytesseract` OCR pass because BeautifulSoup cannot parse `<table>` tags in standard HTML; tables are treated as binary image elements by the HTML parser. *(Distractor type: Common misconception — BeautifulSoup is a full HTML parser and handles table tags)*
* **D)** The Vector Search embedding model does not support tabular data formats — when a chunk contains HTML table content, the embedding computation fails silently and the chunk is not indexed. *(Distractor type: Common misconception — embedding models accept any text string)*

**Correct Answer:** B

**Why B is Correct:** The most likely error is over-aggressive filtering. A common mistake is applying a filter like `for tag in soup.find_all(True): tag.decompose()` that removes ALL tags (including `<table>`, `<tr>`, `<td>`) instead of only the intended structural navigation elements. The developer should specifically target only `<nav>`, `<footer>`, `<header>`, `<aside>` tags for removal and explicitly preserve `<table>` content.

**Why A is Wrong:** BeautifulSoup's `get_text()` does extract text from table cells — it does not strip table content automatically; the issue is in the developer's custom filtering code.

**Why C is Wrong:** BeautifulSoup is a full HTML parser that handles `<table>` tags correctly; tables are not binary image elements.

**Why D is Wrong:** Vector Search embedding models accept any text string, including text extracted from tables.

**Source:** Section 2: Data Preparation – Objective 2: Filter extraneous content in source documents

```json
{
  "id": "S2Q034",
  "source": "DB-GenAI-S2",
  "concept": "Content Filtering – Over-Aggressive Tag Removal",
  "dimension": "Failure Mode",
  "difficulty": "Advanced",
  "question_type": "Diagnosis",
  "blueprint": "B",
  "taxonomy": "Analyze",
  "answer": "B"
}
```

---

### Question 35
**Difficulty:** Advanced
> **Blueprint:** C – Architecture Need → Choose Architecture
> **Concept:** Document Extraction – Multi-Format Tool Mapping
> **Dimension:** Architecture

A data engineer is preparing a RAG pipeline for a healthcare company. Source documents include: clinical trial reports (PDF), drug interaction databases (CSV exported to plain text), and patient intake forms (scanned paper forms as image PDFs). The engineer must select a different extraction tool for each category. What is the correct tool mapping?

* **A)** Clinical trial PDFs → `PyPDF2`; drug interaction CSV text → `unstructured`; scanned patient forms → `pytesseract`. *(Distractor type: Partial truth — PyPDF2 works for simple PDFs but unstructured is superior for complex clinical PDFs; using unstructured for CSVs adds unnecessary overhead)*
* **B)** Clinical trial PDFs → `beautifulsoup4`; drug interaction CSV text → `PyPDF2`; scanned patient forms → `unstructured`. *(Distractor type: Common misconception — beautifulsoup4 cannot parse PDFs; PyPDF2 cannot parse CSV)*
* **C)** Clinical trial PDFs → `pytesseract`; drug interaction CSV text → `pytesseract`; scanned patient forms → `pytesseract`. *(Distractor type: Extreme statement — pytesseract applied universally regardless of format need)*
* **D)** Clinical trial PDFs → `unstructured`; drug interaction CSV text → Python `csv` module or pandas `read_csv()`; scanned patient forms → `pytesseract`. Each tool is matched to the format's specific extraction requirement.

**Correct Answer:** D

**Why D is Correct:** The correct mapping uses the right tool for each document type: `unstructured` handles complex PDF clinical reports with mixed content (text, tables, headers); the Python `csv` module or pandas handles structured CSV plain-text data without needing an NLP library; `pytesseract` performs OCR on scanned image PDFs (patient intake forms) where no digital text layer exists.

**Why A is Wrong:** While `PyPDF2` can handle standard text-based PDFs, `unstructured` is superior for complex clinical PDFs with mixed content; using `unstructured` for CSV text adds unnecessary overhead.

**Why B is Wrong:** `beautifulsoup4` is an HTML parser that cannot parse PDF files; `PyPDF2` cannot parse CSV files.

**Why C is Wrong:** `pytesseract` is only appropriate for image/scanned documents; using it universally for digital PDFs and CSV text introduces unnecessary OCR processing and potential accuracy loss.

**Source:** Section 2: Data Preparation – Objective 3: Choose the appropriate Python package

```json
{
  "id": "S2Q035",
  "source": "DB-GenAI-S2",
  "concept": "Document Extraction – Multi-Format Tool Mapping",
  "dimension": "Architecture",
  "difficulty": "Advanced",
  "question_type": "Scenario",
  "blueprint": "C",
  "taxonomy": "Apply",
  "answer": "D"
}
```

---

### Question 36
**Difficulty:** Proficiency
> **Blueprint:** B – Observed Metrics → Diagnosis
> **Concept:** Retrieval Metrics – nDCG vs. Precision and Recall
> **Dimension:** Definition

A production RAG pipeline serves 50,000 queries per day. The Vector Search index has 2 million chunks. A data scientist runs a retrieval evaluation over a 500-query benchmark and reports `nDCG@10 = 0.61`. The engineering team lead asks: "Is this score good enough to ship, and what does nDCG@10 specifically measure that Precision@10 and Recall@10 do not?" Provide the technically complete answer.

* **A)** `nDCG@10 = 0.61` is always sufficient for production deployment; nDCG@10 measures the same thing as Precision@10 but averages it across queries, providing a more statistically stable metric with no additional ranking information. *(Distractor type: Extreme statement — no universal threshold exists; nDCG is NOT the same as averaged Precision@k)*
* **B)** Whether 0.61 is sufficient depends on the use case baseline; nDCG@10 measures position-weighted relevance — it rewards ranking highly relevant chunks first and penalizes placing them lower — capturing rank quality that neither Precision@10 (equal weight per rank) nor Recall@10 (coverage only) measures.
* **C)** `nDCG@10 = 0.61` is always insufficient for production; nDCG measures the fraction of queries where the first result is relevant, and 0.61 means 39% of queries have an irrelevant first result, which is unacceptable for production. *(Distractor type: Common misconception — that describes Precision@1 or MRR, not nDCG)*
* **D)** nDCG@10 measures the same thing as Recall@10 but normalized between 0 and 1; a score of 0.61 means 61% of all relevant chunks in the index appear somewhere in the top-10 results across all evaluated queries. *(Distractor type: Common misconception — that describes normalized recall, not nDCG)*

**Correct Answer:** B

**Why B is Correct:** nDCG (Normalized Discounted Cumulative Gain) at k measures position-weighted relevance: a highly relevant chunk at rank 1 contributes much more to the score than the same relevant chunk at rank 10. It also handles graded relevance. Neither Precision@10 (equal weight per position) nor Recall@10 (coverage only) captures ranking quality. Whether 0.61 is "good enough" depends on the use case, the baseline of the previous system, and the business requirements — there is no universal threshold.

**Why A is Wrong:** nDCG is NOT the same as averaged Precision@k — nDCG includes position discounting and handles graded relevance.

**Why C is Wrong:** nDCG is not the fraction of queries with a relevant first result — that is Precision@1 or a variation of MRR.

**Why D is Wrong:** That describes a version of normalized Recall, not nDCG; nDCG measures position-weighted cumulative gain, not binary coverage of relevant chunks.

**Source:** Section 2: Data Preparation – Objective 6: Use tools and metrics to evaluate retrieval performance

```json
{
  "id": "S2Q036",
  "source": "DB-GenAI-S2",
  "concept": "Retrieval Metrics – nDCG vs. Precision and Recall",
  "dimension": "Definition",
  "difficulty": "Proficiency",
  "question_type": "Concept",
  "blueprint": "B",
  "taxonomy": "Evaluate",
  "answer": "B"
}
```

---

### Question 37
**Difficulty:** Proficiency
> **Blueprint:** C – Architecture Need → Choose Architecture
> **Concept:** Advanced Chunking – Parent-Child for Structured Technical Documents
> **Dimension:** Architecture

A team is designing a RAG pipeline for a company's 10-year archive of engineering change orders (ECOs), each a 20–80 page PDF with structured sections (Summary, Affected Parts, Test Results, Approvals). They must choose between three chunking strategies: (A) fixed-size 512-token chunks, (B) section-aware chunking by ECO section headers, and (C) Parent-Child chunking with section headers as parent boundaries and 150-token sub-sections as children. What is the complete reasoning for selecting strategy C?

* **A)** Strategy C is the most complex and therefore always the best choice for production RAG pipelines — complexity in the chunking layer inversely correlates with hallucination rates in the LLM output. *(Distractor type: Extreme statement — complexity alone is never a selection criterion)*
* **B)** Strategy C is best because it combines section-aware structure preservation (parent boundaries align with ECO sections) with precise child-level embeddings for accurate retrieval, and full parent section delivery to the LLM for rich context — addressing all three requirements: structure, precision, and context.
* **C)** Strategy C should be avoided because the section headers (parent boundaries) in ECOs vary across 10 years of documents, making it impossible to reliably detect consistent header patterns for parent chunking. *(Distractor type: Common misconception — unstructured can detect headers from formatting cues even if text varies)*
* **D)** Strategy C is the best choice only if the ECOs are stored as Markdown files; for PDFs, parent-child chunking is not supported by any Databricks-compatible parsing library. *(Distractor type: Common misconception — Parent-Child is a logical strategy applicable to any text format)*

**Correct Answer:** B

**Why B is Correct:** For structured, long-form technical documents like ECOs, Parent-Child chunking optimally addresses three key requirements: (1) **Structure preservation** — parent boundaries align with ECO sections, keeping logically related content together. (2) **Retrieval precision** — small 150-token child chunks produce focused, precise embeddings that match specific query terms without semantic diffusion. (3) **Context richness** — the LLM receives the full parent section containing the matched child, providing sufficient context for complete answers.

**Why A is Wrong:** Complexity alone is never a selection criterion; the choice should be based on document structure, query patterns, and performance requirements.

**Why C is Wrong:** Even if header patterns vary across 10 years, the `unstructured` library and similar tools can detect section boundaries from formatting cues (font size, capitalization, whitespace).

**Why D is Wrong:** Parent-Child chunking is a logical strategy applied to any text, regardless of source format; `unstructured` parses PDFs into sections that can serve as parent boundaries.

**Source:** Section 2: Data Preparation – Objective 7: Design retrieval systems using advanced chunking strategies

```json
{
  "id": "S2Q037",
  "source": "DB-GenAI-S2",
  "concept": "Advanced Chunking – Parent-Child for Structured Technical Documents",
  "dimension": "Architecture",
  "difficulty": "Proficiency",
  "question_type": "Scenario",
  "blueprint": "C",
  "taxonomy": "Evaluate",
  "answer": "B"
}
```

---

### Question 38
**Difficulty:** Proficiency
> **Blueprint:** B – Observed Metrics → Diagnosis
> **Concept:** Re-ranking – Short Query Ambiguity and Query Expansion
> **Dimension:** Failure Mode

A Vector Search reranking stage uses a cross-encoder model hosted on a Databricks Model Serving endpoint. The initial Vector Search returns 50 candidates; the reranker scores and returns top-5. A developer observes that for very short, ambiguous queries like "error fix", the reranker consistently places a generic troubleshooting document first, while for detailed queries like "SSL certificate validation error in Python 3.11 requests library", the reranker performs excellently. Why does query length/specificity affect reranker performance, and what can be done to improve short-query performance?

* **A)** Short queries cause the cross-encoder model to time out on the Databricks Model Serving endpoint because the model requires a minimum input length to warm up its attention mechanism; padding short queries to 50 tokens fixes the timeout. *(Distractor type: Common misconception — cross-encoders have no minimum input length requirement)*
* **B)** Cross-encoders score query-document relevance jointly — with a short, ambiguous query, there is insufficient semantic signal to distinguish between the 50 candidate documents, so the reranker defaults to ranking by document length (longer documents first). The fix is query expansion using an LLM to rewrite short queries into more specific forms before retrieval.
* **C)** Cross-encoders perform poorly on short queries because they rely exclusively on BM25 keyword matching rather than semantic similarity; switching to a bi-encoder reranker resolves the short-query problem. *(Distractor type: Common misconception — cross-encoders use neural attention, not BM25)*
* **D)** Short queries produce empty vector embeddings in the Vector Search stage (vectors of all zeros), which causes all 50 retrieved candidates to have identical cosine similarity scores; the reranker then has no useful input and ranks randomly. *(Distractor type: Common misconception — short queries produce valid non-zero embeddings)*

**Correct Answer:** B

**Why B is Correct:** Cross-encoders jointly encode the query and each document together to produce a relevance score. With a rich, specific query, the cross-encoder has abundant signal to distinguish highly relevant chunks. With a vague query ("error fix"), all 50 candidates may seem roughly equally relevant, making it hard for the cross-encoder to produce discriminative scores. Query expansion (using an LLM to rewrite "error fix" into something more specific) provides the cross-encoder with richer semantic signal.

**Why A is Wrong:** Cross-encoders do not have minimum input length requirements and do not time out on short queries; the issue is semantic ambiguity, not a technical constraint.

**Why C is Wrong:** Cross-encoders use neural attention mechanisms for semantic matching, not BM25 keyword matching.

**Why D is Wrong:** Even a short query like "error fix" produces a meaningful (non-zero) vector embedding; embedding models do not produce all-zero vectors for valid text inputs.

**Source:** Section 2: Data Preparation – Objective 8: Explain the role of re-ranking in the information retrieval process

```json
{
  "id": "S2Q038",
  "source": "DB-GenAI-S2",
  "concept": "Re-ranking – Short Query Ambiguity and Query Expansion",
  "dimension": "Failure Mode",
  "difficulty": "Proficiency",
  "question_type": "Diagnosis",
  "blueprint": "B",
  "taxonomy": "Analyze",
  "answer": "B"
}
```

---

### Question 39
**Difficulty:** Proficiency
> **Blueprint:** C – Architecture Need → Choose Architecture
> **Concept:** Document Extraction – Table Integrity with Unstructured
> **Dimension:** Architecture

A developer prepares a chunking pipeline using `unstructured` to parse technical PDFs and classify elements as `Title`, `NarrativeText`, or `Table`. Their chunking strategy should preserve table integrity. When they implement the pipeline, they discover some tables are being split across chunks, resulting in partial table content in each chunk. What is the correct implementation fix?

* **A)** Set `max_characters=99999` in the `unstructured` chunking configuration, which forces all elements including tables to be treated as unsplittable atomic units regardless of size. *(Distractor type: Beginner mistake — creates chunks vastly exceeding the embedding model's token limit)*
* **B)** Use `unstructured`'s `chunk_by_title()` function with `combine_text_under_n_chars` configured, and apply additional logic to detect `Table` elements and force them to be treated as unsplittable atomic chunks that are never split across boundaries.
* **C)** Convert all tables to images using a PDF rendering library before running `unstructured`, then use `pytesseract` to re-extract the table text — the OCR process naturally preserves table row integrity. *(Distractor type: Beginner mistake — lossy and computationally expensive when unstructured already handles tables)*
* **D)** Split the pipeline into two separate paths: one for `NarrativeText` using fixed-size chunking, and one for `Table` elements using document-aware chunking, then merge the resulting chunks back into a single DataFrame before embedding. *(Distractor type: Common misconception — unnecessarily complex; unstructured is designed for multi-element pipelines)*

**Correct Answer:** B

**Why B is Correct:** `unstructured`'s chunking functions allow you to specify element-type-aware behavior. By treating `Table` elements as atomic/unsplittable units (configuring the chunker to never split a single `Table` element across chunk boundaries), you preserve table integrity. This can be achieved by detecting `Table` elements before chunking and either (1) skipping them through the splitter and adding them as fixed chunks, or (2) configuring `unstructured`'s chunking parameters to respect element type boundaries.

**Why A is Wrong:** Setting an extremely large `max_characters` value prevents any splitting but may create chunks vastly exceeding the embedding model's token limit for large tables or sections.

**Why C is Wrong:** Converting existing tables to images and re-running OCR introduces accuracy loss and is computationally expensive; `unstructured` already parses table structure from PDFs without needing OCR.

**Why D is Wrong:** Splitting into two separate pipelines based on element type is unnecessarily complex; `unstructured` is designed to handle multiple element types in a single unified pipeline.

**Source:** Section 2: Data Preparation – Objective 3 & 7: Python packages and advanced chunking

```json
{
  "id": "S2Q039",
  "source": "DB-GenAI-S2",
  "concept": "Document Extraction – Table Integrity with Unstructured",
  "dimension": "Architecture",
  "difficulty": "Proficiency",
  "question_type": "Scenario",
  "blueprint": "C",
  "taxonomy": "Apply",
  "answer": "B"
}
```

---

### Question 40
**Difficulty:** Proficiency
> **Blueprint:** A – Business Problem → Which Feature Solves It?
> **Concept:** Knowledge Base Lifecycle – Superseded Document Governance
> **Dimension:** Best Practice

A data platform team ingests legal briefs (PDF) into a RAG pipeline. After 6 months in production, they discover: (1) older briefs from 2019–2020 contain outdated legal precedents that have since been overruled, but (2) the Vector Search index shows these old chunks as frequently retrieved because they are semantically similar to modern queries. What is the most comprehensive data governance solution?

* **A)** Delete the entire Vector Search index and rebuild it from scratch using only 2022–2025 documents, permanently excluding all pre-2021 content from the knowledge base to eliminate the stale precedent problem. *(Distractor type: Beginner mistake — permanent deletion violates legal data retention requirements)*
* **B)** Add a `document_year` metadata column to the source Delta table, apply an update to mark pre-2021 documents with a `is_superseded = true` flag, and configure the RAG chain to apply a metadata filter `is_superseded = false` at query time — excluding stale chunks from retrieval while preserving them in the Delta table for audit purposes.
* **C)** Fine-tune the embedding model on 2022–2025 legal briefs only so that pre-2021 documents produce embedding vectors that are dissimilar to modern queries, naturally reducing their retrieval frequency without requiring any metadata changes. *(Distractor type: Beginner mistake — fine-tuning is expensive and imprecise for enforcing business rules)*
* **D)** Increase the Vector Search `num_results` from 5 to 50 and add a post-retrieval LLM filtering step that reads each chunk's embedded date metadata and removes any chunk dated before 2021 before passing context to the answer LLM. *(Distractor type: Common misconception — LLM filtering is expensive, fragile, and non-deterministic)*

**Correct Answer:** B

**Why B is Correct:** This is a data governance and knowledge base lifecycle management challenge. Adding a `is_superseded` boolean flag and filtering it out at query time is correct because it: (1) preserves the historical data in Delta Lake for audit and compliance purposes, (2) ensures stale content never reaches the retrieval results, (3) is easily reversible by flipping the flag, and (4) works with Vector Search metadata filtering without requiring index rebuilds.

**Why A is Wrong:** Permanently deleting data violates data retention requirements common in legal contexts.

**Why C is Wrong:** Fine-tuning an embedding model to produce dissimilar vectors for specific documents is an extremely expensive and imprecise approach; embedding distance is not a reliable mechanism for enforcing business rules about document validity.

**Why D is Wrong:** Adding an LLM filtering step for 50 retrieved chunks significantly increases latency and token cost, and relying on the LLM to filter by date is fragile and non-deterministic — metadata filtering at the Vector Search layer is more reliable and efficient.

**Source:** Section 2: Data Preparation – Objective 5: Identify needed source documents

```json
{
  "id": "S2Q040",
  "source": "DB-GenAI-S2",
  "concept": "Knowledge Base Lifecycle – Superseded Document Governance",
  "dimension": "Best Practice",
  "difficulty": "Proficiency",
  "question_type": "Scenario",
  "blueprint": "A",
  "taxonomy": "Evaluate",
  "answer": "B"
}
```

---

### Question 41
**Difficulty:** Beginner
> **Blueprint:** A – Business Problem → Which Feature Solves It?
> **Concept:** Chunking Strategy – Markdown Header Splitting
> **Dimension:** Feature

A developer needs to split a Markdown knowledge base article into chunks. The article uses `#` for the main title and `##` for major sections. They want each major section to be one chunk. Which chunking tool and split parameter should they use?

* **A)** Use Python's `str.split('\n\n')` to split on double newlines, which corresponds to paragraph boundaries in Markdown and keeps each paragraph as a separate chunk regardless of header level. *(Distractor type: Common misconception — paragraph splits produce many small chunks, not section-level chunks)*
* **B)** Use LangChain's `MarkdownHeaderTextSplitter` configured to split on `##` headers, which produces one chunk per major section while keeping the section content together and adding the section title as metadata.
* **C)** Use `PyPDF2`'s page-based splitter to create one chunk per page, which aligns well with Markdown structure since each major section typically occupies a full rendered page. *(Distractor type: Related technology — PyPDF2 is a PDF library, not a Markdown tool)*
* **D)** Use `pytesseract` to OCR-render the Markdown file as an image and then split on visual whitespace gaps between sections, which detects structural boundaries regardless of the underlying text format. *(Distractor type: Beginner mistake — applying OCR to machine-readable Markdown text is wasteful)*

**Correct Answer:** B

**Why B is Correct:** LangChain's `MarkdownHeaderTextSplitter` is designed exactly for this use case — it takes a list of header levels to split on (e.g., `[("##", "Section")]`) and produces one chunk per section, with the section title added as chunk metadata. This directly fulfills the requirement of one chunk per major section while preserving content integrity.

**Why A is Wrong:** Double-newline splitting creates paragraph-level chunks, not section-level chunks — a major section with multiple paragraphs would be split into multiple chunks.

**Why C is Wrong:** `PyPDF2` is a PDF parsing library, not a Markdown processing tool; Markdown files are plain text and do not have pages.

**Why D is Wrong:** `pytesseract` is an OCR tool for image-based text — applying it to a Markdown file (which is already machine-readable text) adds unnecessary complexity and accuracy loss.

**Source:** Section 2: Data Preparation – Objective 1: Apply a chunking strategy for a given document structure

```json
{
  "id": "S2Q041",
  "source": "DB-GenAI-S2",
  "concept": "Chunking Strategy – Markdown Header Splitting",
  "dimension": "Feature",
  "difficulty": "Beginner",
  "question_type": "Scenario",
  "blueprint": "A",
  "taxonomy": "Apply",
  "answer": "B"
}
```

---

### Question 42
**Difficulty:** Beginner
> **Blueprint:** A – Business Problem → Which Feature Solves It?
> **Concept:** Vector Search – Automatic Embedding Column
> **Dimension:** Feature

A developer writes a chunk to a Unity Catalog Delta table with the column `chunk_text`. When they create a Databricks Vector Search index on this table, what additional column is automatically added to the index and what does it represent?

* **A)** A `chunk_summary` column is automatically added by Vector Search, which stores a 1-sentence LLM-generated summary of each chunk for fast keyword matching during retrieval. *(Distractor type: Common misconception — no LLM processing occurs at index creation time)*
* **B)** A `vector` or embedding column is automatically computed and stored by the Vector Search service — it contains the high-dimensional numerical array (embedding) of each `chunk_text`, enabling semantic similarity search.
* **C)** A `relevance_score` column is automatically added, containing a pre-computed relevance score between 0 and 1 that the index uses to rank chunks at query time without performing real-time vector computation. *(Distractor type: Common misconception — relevance is computed dynamically at query time based on the specific query)*
* **D)** A `doc_hash` column is automatically added containing an MD5 hash of each `chunk_text`, which Vector Search uses as the primary deduplication key to prevent duplicate chunks from being stored in the index. *(Distractor type: Common misconception — deduplication is handled through the primary key id column provided by the developer)*

**Correct Answer:** B

**Why B is Correct:** When a Databricks Vector Search index is created on a Delta table containing a text column, the Vector Search service automatically computes and stores the vector embedding for each row's text using the configured embedding model. This embedding column is the foundation of semantic similarity search — at query time, the query is also embedded and compared against stored embeddings using approximate nearest neighbor algorithms.

**Why A is Wrong:** Vector Search does not automatically generate LLM summaries of chunks; no LLM processing occurs at index creation time.

**Why C is Wrong:** There is no pre-computed static relevance score — relevance is computed dynamically at query time by comparing the query vector against stored chunk vectors.

**Why D is Wrong:** While `id` is used for deduplication and change tracking, Vector Search does not automatically add an MD5 hash column.

**Source:** Section 2: Data Preparation – Objective 4: Define operations and sequence to write chunked text into Delta Lake

```json
{
  "id": "S2Q042",
  "source": "DB-GenAI-S2",
  "concept": "Vector Search – Automatic Embedding Column",
  "dimension": "Feature",
  "difficulty": "Beginner",
  "question_type": "Concept",
  "blueprint": "A",
  "taxonomy": "Understand",
  "answer": "B"
}
```

---

### Question 43
**Difficulty:** Beginner
> **Blueprint:** A – Business Problem → Which Feature Solves It?
> **Concept:** Document Extraction – Unified Multi-Format API
> **Dimension:** Feature

A developer has source documents as HTML files, PDFs, and plain `.txt` files. They want a unified extraction pipeline that handles all three formats without writing separate parsing code for each. Which library best satisfies this requirement?

* **A)** `PyPDF2` — because it is the most widely used document extraction library and implicitly supports HTML and TXT files as fallback formats when the primary PDF parsing mode does not detect PDF metadata. *(Distractor type: Common misconception — PyPDF2 is PDF-only)*
* **B)** `beautifulsoup4` — because its HTML parser can handle any file extension by reading the raw bytes of PDF and TXT files as if they were HTML documents, producing consistent text output across all three formats. *(Distractor type: Common misconception — beautifulsoup4 is HTML/XML only)*
* **C)** `unstructured` — because it is a multi-format document parsing library with native support for HTML, PDF, and plain text files, providing a unified API that auto-detects format and returns structured text elements.
* **D)** `pytesseract` — because it renders each file format to a JPEG image internally before performing OCR, producing consistent machine-readable text from any source format including HTML, PDF, and TXT. *(Distractor type: Common misconception — applying OCR to digital HTML and TXT files is lossy and unnecessary)*

**Correct Answer:** C

**Why C is Correct:** `unstructured` is the only library among the options that natively handles all three formats (HTML, PDF, plain text) through a unified `partition()` function that auto-detects file format and routes to the appropriate parser. This eliminates the need to write separate parsing code for each format.

**Why A is Wrong:** `PyPDF2` is a PDF-specific library — it cannot parse HTML or TXT files.

**Why B is Wrong:** `beautifulsoup4` is an HTML/XML parser only — it cannot meaningfully parse binary PDF files.

**Why D is Wrong:** `pytesseract` renders documents to images for OCR only when dealing with image-based content; applying OCR to digital HTML and TXT files would be lossy and slow.

**Source:** Section 2: Data Preparation – Objective 3: Choose the appropriate Python package

```json
{
  "id": "S2Q043",
  "source": "DB-GenAI-S2",
  "concept": "Document Extraction – Unified Multi-Format API",
  "dimension": "Feature",
  "difficulty": "Beginner",
  "question_type": "Scenario",
  "blueprint": "A",
  "taxonomy": "Apply",
  "answer": "C"
}
```

---

### Question 44
**Difficulty:** Beginner
> **Blueprint:** A – Business Problem → Which Feature Solves It?
> **Concept:** Chunking Strategy – Overlap Parameter Definition
> **Dimension:** Definition

What is the purpose of the `chunk_overlap` parameter in a fixed-size chunking configuration?

* **A)** `chunk_overlap` controls how many chunks from adjacent documents are combined together into one super-chunk, enabling the retriever to always return multi-document context to the LLM. *(Distractor type: Common misconception — overlap operates within a single document, not across documents)*
* **B)** `chunk_overlap` specifies the number of tokens that are duplicated between consecutive chunks, preserving context at chunk boundaries so that sentences or ideas split by the chunk boundary appear in both adjacent chunks.
* **C)** `chunk_overlap` sets the minimum number of meaningful tokens a chunk must contain before it is written to the Delta table; chunks with fewer tokens than the overlap value are automatically discarded. *(Distractor type: Common misconception — that describes min_chunk_size, not chunk_overlap)*
* **D)** `chunk_overlap` defines the maximum allowed similarity between two adjacent chunks — if their cosine similarity exceeds this value, one chunk is dropped to prevent the Vector Search index from storing near-duplicate embeddings. *(Distractor type: Common misconception — chunk_overlap is set before embedding; has nothing to do with cosine similarity)*

**Correct Answer:** B

**Why B is Correct:** `chunk_overlap` is the number of tokens shared between the end of one chunk and the beginning of the next chunk. For example, with `chunk_size=512` and `chunk_overlap=64`, the last 64 tokens of chunk N become the first 64 tokens of chunk N+1. This ensures that a sentence or concept that falls at the boundary between two chunks is fully represented in both, preventing context loss at chunk boundaries.

**Why A is Wrong:** `chunk_overlap` operates within a single document's chunking, not across different documents.

**Why C is Wrong:** `chunk_overlap` is about boundary token duplication, not a minimum token threshold for filtering.

**Why D is Wrong:** `chunk_overlap` is a text processing parameter set before embedding; it has nothing to do with cosine similarity or deduplication in the vector index.

**Source:** Section 2: Data Preparation – Objective 1: Apply a chunking strategy

```json
{
  "id": "S2Q044",
  "source": "DB-GenAI-S2",
  "concept": "Chunking Strategy – Overlap Parameter Definition",
  "dimension": "Definition",
  "difficulty": "Beginner",
  "question_type": "Concept",
  "blueprint": "A",
  "taxonomy": "Understand",
  "answer": "B"
}
```

---

### Question 45
**Difficulty:** Beginner
> **Blueprint:** C – Architecture Need → Choose Architecture
> **Concept:** Delta Lake – Volume-to-Vector-Search Pipeline
> **Dimension:** Architecture

A company stores its source documents in Databricks Volumes as PDF files. What is the correct pipeline sequence to make these documents searchable via a Databricks Vector Search index?

* **A)** Create the Vector Search index directly on the Volume path — Vector Search can automatically detect, parse, and embed PDF files stored in Volumes without any intermediate processing steps. *(Distractor type: Common misconception — Vector Search requires a Delta table as its source)*
* **B)** Extract text from PDFs using a parsing library (e.g., `unstructured`), chunk the extracted text, write the chunks to a Unity Catalog Delta table with CDF enabled, then create the Vector Search index on the Delta table.
* **C)** Upload the PDF files to Databricks Model Serving as binary artifacts, which automatically vectorizes and indexes them — then configure the Vector Search index to query the Model Serving artifact store. *(Distractor type: Common misconception — Model Serving is for deploying ML models, not for document indexing)*
* **D)** Convert the PDFs to Delta tables using the Databricks Auto Loader PDF connector, which automatically detects PDF structure and creates one Delta row per paragraph, ready for immediate Vector Search indexing. *(Distractor type: Common misconception — Auto Loader supports structured formats; there is no built-in PDF connector)*

**Correct Answer:** B

**Why B is Correct:** Databricks Vector Search requires a Delta Lake table as its data source — it cannot directly index files from Volumes. The correct pipeline is: (1) Use a parsing library to extract text from PDFs, (2) apply a chunking strategy to produce text chunks, (3) write chunks as rows to a Unity Catalog Delta table with CDF enabled, (4) create a Vector Search index on the Delta table.

**Why A is Wrong:** Vector Search does not have a native capability to directly read and parse PDF files from Volumes; it requires Delta tables as the source.

**Why C is Wrong:** Databricks Model Serving is for deploying ML models as REST APIs — it is not an artifact indexing service.

**Why D is Wrong:** Auto Loader is designed to ingest structured and semi-structured data (CSV, JSON, Parquet, Avro) — there is no built-in PDF connector.

**Source:** Section 2: Data Preparation – Objective 4: Define operations and sequence to write chunked text into Delta Lake

```json
{
  "id": "S2Q045",
  "source": "DB-GenAI-S2",
  "concept": "Delta Lake – Volume-to-Vector-Search Pipeline",
  "dimension": "Architecture",
  "difficulty": "Beginner",
  "question_type": "Scenario",
  "blueprint": "C",
  "taxonomy": "Apply",
  "answer": "B"
}
```

---

### Question 46
**Difficulty:** Intermediate
> **Blueprint:** B – Observed Metrics → Diagnosis
> **Concept:** Advanced Chunking – Cross-Section Query Problem
> **Dimension:** Failure Mode

A developer discovers that their RAG chatbot is returning wrong answers specifically for topics that span multiple sections of a long document. For example, "What are the steps to set up SSO?" returns incomplete steps because step 1 is in the "Prerequisites" section and steps 2–5 are in the "Configuration" section — split across multiple chunks. What chunking strategy best addresses this multi-section problem?

* **A)** Use smaller chunk sizes (e.g., 100 tokens) so that more chunks are retrieved in the top-k, increasing the probability that all prerequisite and configuration section chunks appear in the retrieved set simultaneously. *(Distractor type: Common misconception — smaller chunks create more fragmented context, not less)*
* **B)** Use document-aware chunking at a higher structural level (e.g., split only at the top-level `#` document header instead of `##` section headers), so that all sections of a single document remain in one larger chunk that the LLM can read end-to-end.
* **C)** Use a sliding window approach where every chunk overlaps by 90% of its length with the previous chunk, effectively creating near-duplicate chunks for every token position to ensure no cross-section content is missed. *(Distractor type: Beginner mistake — 90% overlap creates massive redundancy without solving the cross-section dependency)*
* **D)** Add a `related_sections` metadata column to each chunk that lists the section IDs of adjacent sections, and modify the retriever to automatically fetch adjacent sections when any section chunk is retrieved. *(Distractor type: Partial truth — valid concept but requires significant custom infrastructure)*

**Correct Answer:** B

**Why B is Correct:** When topics span multiple document sections, splitting at a lower granularity (e.g., `##` headers) creates inter-section dependency that no retriever can reliably bridge. The fix is to chunk at a higher structural level — splitting only on the document title (`#`) keeps all sections of one document together in a single (larger) chunk. This may require combining with a size-limiting second split if the document exceeds the token limit.

**Why A is Wrong:** Using smaller chunks (100 tokens) creates more fragmented chunks with even less context per chunk — more fragments does not solve the cross-section dependency problem.

**Why C is Wrong:** 90% overlap creates massive data redundancy (a 512-token chunk with 90% overlap produces chunks every 51 tokens), exploding storage and index size without meaningfully improving the multi-section retrieval problem.

**Why D is Wrong:** Adding related_sections metadata and modifying the retriever requires significant custom infrastructure code and is fragile.

**Source:** Section 2: Data Preparation – Objective 7: Design retrieval systems using advanced chunking strategies

```json
{
  "id": "S2Q046",
  "source": "DB-GenAI-S2",
  "concept": "Advanced Chunking – Cross-Section Query Problem",
  "dimension": "Failure Mode",
  "difficulty": "Intermediate",
  "question_type": "Diagnosis",
  "blueprint": "B",
  "taxonomy": "Analyze",
  "answer": "B"
}
```

---

### Question 47
**Difficulty:** Intermediate
> **Blueprint:** C – Architecture Need → Choose Architecture
> **Concept:** Delta Lake – CDF at Table Creation vs. ALTER TABLE
> **Dimension:** Architecture

A developer runs the following code to prepare a Vector Search source table:

```python
spark.sql("""
  CREATE TABLE IF NOT EXISTS main.docs.chunks 
  (id BIGINT, chunk_text STRING)
  TBLPROPERTIES (delta.enableChangeDataFeed = true)
""")
```

Is this approach correct for enabling CDF? Are there any risks with the `id BIGINT` column type?

* **A)** The code is incorrect — CDF must be enabled separately with `ALTER TABLE` after table creation; including it in `CREATE TABLE TBLPROPERTIES` silently fails and CDF is not actually enabled. *(Distractor type: Common misconception — CDF can be enabled at creation time via TBLPROPERTIES)*
* **B)** The code is correct — CDF can be enabled at table creation time via `TBLPROPERTIES`. However, `id BIGINT` risks column type conflicts if the source system generates string-format IDs (e.g., UUIDs), which must be cast to BIGINT or the pipeline will fail with type errors.
* **C)** The code is correct and the `id BIGINT` type is always appropriate since Vector Search requires integer primary keys; string-type IDs are not supported as primary key columns for Vector Search indexes. *(Distractor type: Common misconception — Vector Search supports both string and integer primary key types)*
* **D)** The code is incorrect — CDF requires the source table to use Delta Lake format v3 or higher; specifying `TBLPROPERTIES` at creation time only works with format v3, and Unity Catalog tables default to format v1. *(Distractor type: Common misconception — no format version prerequisite exists for CDF)*

**Correct Answer:** B

**Why B is Correct:** Including `delta.enableChangeDataFeed = true` in the `TBLPROPERTIES` at `CREATE TABLE` time is a fully valid and supported approach — CDF is activated from the first write. However, `id BIGINT` is a risk: if source document IDs are UUID strings, casting them to BIGINT would fail or produce incorrect values. The developer should use `id STRING` if the source IDs are not guaranteed to be integers. Databricks Vector Search supports both string and integer primary key column types.

**Why A is Wrong:** CDF can be enabled either at creation time (via `TBLPROPERTIES` in `CREATE TABLE`) or after creation (via `ALTER TABLE`); both approaches are valid.

**Why C is Wrong:** Databricks Vector Search supports string-type primary key columns — BIGINT is not the only accepted type.

**Why D is Wrong:** There is no "format version" prerequisite for CDF; CDF works with the default table format in Unity Catalog.

**Source:** Section 2: Data Preparation – Objective 4: Define operations and sequence to write chunked text into Delta Lake

```json
{
  "id": "S2Q047",
  "source": "DB-GenAI-S2",
  "concept": "Delta Lake – CDF at Table Creation vs. ALTER TABLE",
  "dimension": "Architecture",
  "difficulty": "Intermediate",
  "question_type": "Code",
  "blueprint": "C",
  "taxonomy": "Analyze",
  "answer": "B"
}
```

---

### Question 48
**Difficulty:** Intermediate
> **Blueprint:** C – Architecture Need → Choose Architecture
> **Concept:** Re-ranking – Cross-Encoder vs. Bi-Encoder Trade-off
> **Dimension:** Trade-off

A team is evaluating whether to use a cross-encoder reranker or a bi-encoder re-scoring step as stage 2 after Vector Search retrieval. The application serves 500 queries per second. Which technical trade-off determines the correct choice?

* **A)** Cross-encoders produce more accurate relevance scores but are computationally expensive (they process each query-document pair together); bi-encoder re-scoring is faster but less accurate (it scores query and documents independently). For 500 QPS, the latency cost of a cross-encoder on 50 candidates per query must be evaluated against the quality improvement.
* **B)** Cross-encoders are always faster than bi-encoders at scale because they use precomputed document representations; bi-encoders recompute document embeddings at query time, making them slower for high-volume applications. *(Distractor type: Common misconception — this reverses the actual trade-off)*
* **C)** Bi-encoders produce more accurate reranking than cross-encoders at high query volumes because bi-encoders can be parallelized across GPU cores, while cross-encoders run sequentially on CPU only. *(Distractor type: Common misconception — accuracy trade-off is reversed; cross-encoders consistently outperform bi-encoders)*
* **D)** Cross-encoders and bi-encoders produce identical reranking quality for queries longer than 50 tokens; the choice only matters for very short queries (under 10 tokens) where cross-encoders have a slight advantage. *(Distractor type: Common misconception — the accuracy gap is not determined by query token length)*

**Correct Answer:** A

**Why A is Correct:** This is the fundamental cross-encoder vs. bi-encoder trade-off: cross-encoders jointly encode query and document together for high accuracy, but at the cost of running a separate forward pass for each candidate pair. Bi-encoders encode query and documents separately (documents can be pre-encoded) and score by dot product — much faster but less precise. At 500 QPS with 50 candidates each, a cross-encoder must perform 25,000 inference calls per second, which may exceed latency targets. The team must benchmark latency and quality for their specific throughput requirement.

**Why B is Wrong:** This reverses the trade-off: bi-encoders use precomputed document embeddings and are faster; cross-encoders process query-document pairs jointly and are computationally more expensive.

**Why C is Wrong:** The accuracy trade-off is opposite — cross-encoders are more accurate than bi-encoder re-scoring because of their joint attention mechanism.

**Why D is Wrong:** The accuracy gap between cross-encoders and bi-encoders is not determined by query token length; cross-encoders consistently outperform bi-encoders across all query lengths.

**Source:** Section 2: Data Preparation – Objective 8: Explain the role of re-ranking

```json
{
  "id": "S2Q048",
  "source": "DB-GenAI-S2",
  "concept": "Re-ranking – Cross-Encoder vs. Bi-Encoder Trade-off",
  "dimension": "Trade-off",
  "difficulty": "Intermediate",
  "question_type": "Scenario",
  "blueprint": "C",
  "taxonomy": "Evaluate",
  "answer": "A"
}
```

---

### Question 49
**Difficulty:** Intermediate
> **Blueprint:** A – Business Problem → Which Feature Solves It?
> **Concept:** Vector Search – Metadata Columns and Embedding Computation
> **Dimension:** Architecture

A developer adds document metadata (title, author, publication_date) as additional columns to the source Delta table used by Vector Search. A colleague asks: "Do these metadata columns affect the embedding computation?" What is the technically correct answer?

* **A)** Yes — Vector Search automatically concatenates all string columns from the Delta table into the embedding input, so adding title and author columns increases the semantic richness of the embedding vector. *(Distractor type: Common misconception — only the designated source_column is embedded)*
* **B)** No — the embedding is computed only from the designated `chunk_text` column specified when creating the index. Metadata columns (title, author, publication_date) are stored in the index for filtering and retrieval but do not influence the embedding computation.
* **C)** Yes — but only the `title` column is automatically appended to `chunk_text` before embedding; other metadata columns (author, publication_date) are stored separately without affecting the embedding. *(Distractor type: Common misconception — no automatic title-appending behavior exists)*
* **D)** No — metadata columns are not stored in the Vector Search index at all; they remain only in the source Delta table and must be joined back after retrieval using the `id` column to access metadata in the application. *(Distractor type: Common misconception — metadata columns ARE stored in the Vector Search index for filtering)*

**Correct Answer:** B

**Why B is Correct:** When creating a Databricks Vector Search index, you specify which column contains the text to embed (e.g., `source_column="chunk_text"`). Only this designated column's text is passed to the embedding model. Metadata columns (title, author, date) are stored alongside the embedding in the index for use as retrieval filters or as returned metadata in results, but they do not contribute to the embedding vector itself.

**Why A is Wrong:** Vector Search does not automatically concatenate all string columns — only the explicitly designated `source_column` is embedded.

**Why C is Wrong:** There is no automatic title-appending behavior; embedding input is strictly limited to the designated source column.

**Why D is Wrong:** Metadata columns ARE stored in the Vector Search index alongside the embeddings — this is how metadata filtering works at query time without requiring a separate Delta table join.

**Source:** Section 2: Data Preparation – Objective 4: Define operations and sequence to write chunked text into Delta Lake

```json
{
  "id": "S2Q049",
  "source": "DB-GenAI-S2",
  "concept": "Vector Search – Metadata Columns and Embedding Computation",
  "dimension": "Architecture",
  "difficulty": "Intermediate",
  "question_type": "Concept",
  "blueprint": "A",
  "taxonomy": "Understand",
  "answer": "B"
}
```

---

### Question 50
**Difficulty:** Intermediate
> **Blueprint:** B – Observed Metrics → Diagnosis
> **Concept:** Retrieval Metrics – Coverage AND Ranking Quality
> **Dimension:** Best Practice

A developer is evaluating retrieval quality using a 200-question test set. For each question, they know the exact chunk IDs that should be returned. They want to measure both "are the right chunks being retrieved?" AND "are they being returned in the right order?" Which combination of metrics should they compute?

* **A)** `Precision@k` only — it captures both retrieval accuracy (whether right chunks are returned) and ranking quality (whether they are returned in the right order) in a single unified metric. *(Distractor type: Common misconception — Precision@k measures accuracy but not rank ordering)*
* **B)** `Recall@k` and `Precision@k` together — Recall@k measures whether all relevant chunks are found, and Precision@k measures what fraction of returned chunks are relevant; together they capture coverage and accuracy but not ranking. *(Distractor type: Partial truth — they capture coverage and accuracy but not ranking quality)*
* **C)** `Recall@k` and `nDCG@k` together — Recall@k measures whether all relevant chunks are found (coverage), and nDCG@k measures position-weighted relevance quality (ranking) — together they capture both retrieval completeness and ranking quality.
* **D)** `MRR` (Mean Reciprocal Rank) only — it directly measures both the fraction of correctly retrieved chunks AND their rank positions, making it the single comprehensive metric for evaluating both retrieval and ranking simultaneously. *(Distractor type: Common misconception — MRR only measures the rank of the FIRST relevant result, not coverage of all relevant results)*

**Correct Answer:** C

**Why C is Correct:** The question requires two distinct measurements: (1) "Are the right chunks being retrieved?" is answered by Recall@k — it measures coverage (what fraction of known-relevant chunks appear in the top-k). (2) "Are they being returned in the right order?" is answered by nDCG@k — it measures position-weighted relevance (giving more credit to relevant chunks at higher ranks). Together, Recall@k and nDCG@k comprehensively cover both retrieval completeness and ranking quality.

**Why A is Wrong:** Precision@k measures what fraction of returned chunks are relevant (accuracy) but does not measure ranking quality.

**Why B is Wrong:** While Recall@k and Precision@k together capture coverage and accuracy, they do not capture ranking quality — neither metric distinguishes whether relevant results appear at rank 1 or rank 10.

**Why D is Wrong:** MRR (Mean Reciprocal Rank) measures the rank of the FIRST relevant result only — it does not measure coverage (Recall) or the ordering of ALL relevant results.

**Source:** Section 2: Data Preparation – Objective 6: Use tools and metrics to evaluate retrieval performance

```json
{
  "id": "S2Q050",
  "source": "DB-GenAI-S2",
  "concept": "Retrieval Metrics – Coverage AND Ranking Quality",
  "dimension": "Best Practice",
  "difficulty": "Intermediate",
  "question_type": "Concept",
  "blueprint": "B",
  "taxonomy": "Apply",
  "answer": "C"
}
```

---

### Question 51
**Difficulty:** Advanced
> **Blueprint:** B – Observed Metrics → Diagnosis
> **Concept:** MLflow Tracing – Misapplied RETRIEVER Span
> **Dimension:** Failure Mode

A developer instructs a junior engineer: "Add `@mlflow.trace(span_type='RETRIEVER')` to the retrieval function before the evaluation run." The junior engineer adds it to the wrong function — they add it to the LLM call wrapper instead of the retrieval function. What will happen when `mlflow.genai.evaluate()` runs the `RetrievalRelevance` scorer?

* **A)** The scorer will raise a `SpanTypeConflict` exception because the `RETRIEVER` span type is exclusively reserved for Vector Search function calls; applying it to any other function violates MLflow's span type schema validation. *(Distractor type: Common misconception — MLflow does not enforce which Python function a span type can be applied to)*
* **B)** The scorer will not find a `RETRIEVER`-typed span in the expected location of the trace tree; it will look for retrieved documents in the span output and instead find the LLM's generated text, causing the scorer to fail or return null/nonsensical scores.
* **C)** The scorer will automatically detect that the decorated function is an LLM call (based on the input/output format) and switch to using `AnswerRelevance` scoring instead of `RetrievalRelevance` scoring, adapting to the span content. *(Distractor type: Common misconception — MLflow scorers do not auto-detect function types or switch scorer logic)*
* **D)** The scorer will work correctly because MLflow's `RetrievalRelevance` scorer reads all spans in the trace tree regardless of their type, averaging relevance scores across all captured inputs and outputs. *(Distractor type: Common misconception — RetrievalRelevance specifically requires a RETRIEVER-typed span)*

**Correct Answer:** B

**Why B is Correct:** MLflow's `RetrievalRelevance` scorer specifically looks for a span typed as `"RETRIEVER"` in the trace tree to find the retrieval inputs (the query) and outputs (the retrieved document chunks). If the `RETRIEVER` span type is applied to the LLM call wrapper instead, the span that MLflow finds will contain the LLM's generated text as its output rather than document chunks. The scorer will either fail to parse the LLM output as retrieved documents, return null scores, or produce meaningless scores based on misidentified data.

**Why A is Wrong:** MLflow does not enforce which Python function a span type can be applied to — the `RETRIEVER` type is a semantic label, not a technical enforcement mechanism.

**Why C is Wrong:** MLflow evaluation scorers do not automatically detect function types or switch scorer logic based on span content.

**Why D is Wrong:** `RetrievalRelevance` specifically requires a `RETRIEVER`-typed span; it does not aggregate across all span types in the trace.

**Source:** Section 2: Data Preparation – Objective 6: Use tools and metrics to evaluate retrieval performance

```json
{
  "id": "S2Q051",
  "source": "DB-GenAI-S2",
  "concept": "MLflow Tracing – Misapplied RETRIEVER Span",
  "dimension": "Failure Mode",
  "difficulty": "Advanced",
  "question_type": "Diagnosis",
  "blueprint": "B",
  "taxonomy": "Analyze",
  "answer": "B"
}
```

---

### Question 52
**Difficulty:** Advanced
> **Blueprint:** C – Architecture Need → Choose Architecture
> **Concept:** Advanced Chunking – Multi-Query Decomposition
> **Dimension:** Architecture

A production RAG pipeline uses fixed-size chunking with 512 tokens and retrieves top-5 chunks. Engineers discover that for complex, multi-part user queries (e.g., "Compare the warranty terms, return policy, and price-matching guarantee for Product X"), individual chunks only cover one aspect each, causing the LLM to receive incomplete context. They decide to increase `num_results` from 5 to 15 to capture all three aspects. What new problem does this introduce, and what is the more architecturally sound fix?

* **A)** Increasing `num_results` to 15 causes the Vector Search index query latency to increase by 3×, making the pipeline too slow for real-time use; the fix is to use a faster approximate nearest neighbor algorithm instead. *(Distractor type: Common misconception — Vector Search is highly optimized; increasing num_results has minimal latency impact)*
* **B)** Increasing `num_results` to 15 sends 15 chunks (potentially 7,680 tokens) to the LLM, which may exceed the LLM's context window limit and dilute the LLM's attention across more content — the sound fix is multi-query decomposition: split the compound question into 3 sub-queries, retrieve top-5 for each, and deduplicate before assembling context.
* **C)** Increasing `num_results` to 15 violates the Databricks Vector Search maximum results limit of 10 per query; the fix is to run two separate Vector Search queries with `num_results=7` and `num_results=8` and merge the results. *(Distractor type: Common misconception — Databricks Vector Search supports significantly more than 10 results per query)*
* **D)** Increasing `num_results` to 15 causes the MLflow `RetrievalRelevance` scorer to time out because it must run an LLM judge 15 times instead of 5 times per query, making evaluation computationally infeasible for production use. *(Distractor type: Common misconception — evaluation run time is a development concern, not a production concern)*

**Correct Answer:** B

**Why B is Correct:** Increasing `num_results` to 15 passes significantly more tokens (up to 15 × ~512 = 7,680 tokens) to the LLM. Modern LLMs can suffer from the "lost in the middle" phenomenon where information in the middle of very long contexts is attended to less carefully. The architecturally sound fix for multi-part queries is query decomposition: break the complex query into three focused sub-queries, retrieve top-5 for each, deduplicate overlapping chunks, and assemble a focused context set.

**Why A is Wrong:** Databricks Vector Search is highly optimized for fast approximate nearest neighbor search; increasing `num_results` from 5 to 15 has minimal impact on query latency.

**Why C is Wrong:** Databricks Vector Search supports retrieving significantly more than 10 results per query — there is no 10-result limit.

**Why D is Wrong:** Evaluation run time is a development/testing concern, not a production concern.

**Source:** Section 2: Data Preparation – Objective 7: Design retrieval systems using advanced chunking strategies

```json
{
  "id": "S2Q052",
  "source": "DB-GenAI-S2",
  "concept": "Advanced Chunking – Multi-Query Decomposition",
  "dimension": "Architecture",
  "difficulty": "Advanced",
  "question_type": "Scenario",
  "blueprint": "C",
  "taxonomy": "Evaluate",
  "answer": "B"
}
```

---

### Question 53
**Difficulty:** Advanced
> **Blueprint:** B – Observed Metrics → Diagnosis
> **Concept:** Re-ranking – Query-Dependence of Cross-Encoder Scores
> **Dimension:** Failure Mode

A developer's reranking stage uses a cross-encoder model to score 50 candidate chunks. The cross-encoder is deployed on a Databricks Model Serving CPU endpoint. Average reranker latency is 2.8 seconds per query. A performance engineer proposes: "We should use the cross-encoder's output scores as permanent metadata fields in the Vector Search index, so we don't need to run the reranker at query time." What is technically wrong with this proposal?

* **A)** Storing pre-computed reranker scores in the Vector Search index is a valid optimization; the engineer's proposal is correct and would eliminate all reranker latency at query time. *(Distractor type: Common misconception — the proposal is fundamentally flawed for the reason in B)*
* **B)** Pre-computed cross-encoder scores are query-independent (computed once at index creation time), but cross-encoders are designed to score query-document relevance jointly — the score is specific to a particular query. A score computed during index creation is meaningless for a different user query at runtime.
* **C)** Pre-computed scores would only work if stored in the Delta source table first, then synced to Vector Search; storing scores directly in the Vector Search index without going through the Delta source table violates the CDF sync architecture. *(Distractor type: Partial truth — the flaw is about the fundamental query-dependence of cross-encoder scores, not the data pipeline architecture)*
* **D)** The proposal fails because Databricks Vector Search metadata fields can only store string or integer values; floating-point relevance scores from a cross-encoder cannot be stored as index metadata. *(Distractor type: Common misconception — Vector Search metadata supports numeric float types)*

**Correct Answer:** B

**Why B is Correct:** This is the fundamental flaw in the proposal. A cross-encoder produces a relevance score for a specific (query, document) pair — the score changes with every different query. Pre-computing a score at index creation time would require knowing the query in advance, which is impossible for a live system serving diverse user queries. The scores computed at index time (without knowing the user's query) would be meaningless approximations. The reranker's value IS the query-dependent re-scoring.

**Why A is Wrong:** The proposal is technically flawed for the reason explained in B; it is not a valid optimization.

**Why C is Wrong:** The proposal's flaw is about the fundamental query-dependence of cross-encoder scores, not about the data pipeline architecture.

**Why D is Wrong:** Databricks Vector Search metadata supports numeric (float) types; the proposal's flaw is not about data type limitations.

**Source:** Section 2: Data Preparation – Objective 8: Explain the role of re-ranking

```json
{
  "id": "S2Q053",
  "source": "DB-GenAI-S2",
  "concept": "Re-ranking – Query-Dependence of Cross-Encoder Scores",
  "dimension": "Failure Mode",
  "difficulty": "Advanced",
  "question_type": "Diagnosis",
  "blueprint": "B",
  "taxonomy": "Analyze",
  "answer": "B"
}
```

---

### Question 54
**Difficulty:** Advanced
> **Blueprint:** B – Observed Metrics → Diagnosis
> **Concept:** Retrieval Metrics – Low Recall Architectural Cause
> **Dimension:** Architecture

A team discovers that their RAG pipeline has high `Precision@5` (0.91) but very low `Recall@5` (0.28). They have 8 million chunks in the Vector Search index covering 200,000 source documents. What is the most likely architectural cause, and what change addresses it?

* **A)** The embedding model is too large (7B parameters), making it overfit to training data and retrieve only chunks it "memorizes" from training — switching to a smaller 125M parameter embedding model improves generalization and recall. *(Distractor type: Common misconception — embedding model size does not directly cause low recall in this way)*
* **B)** The `num_results=5` setting is too low for a knowledge base of 8 million chunks — there may be 15–20 relevant chunks for complex queries, but only 5 are returned. Increasing `num_results` to 20–50, adding a reranker to select the best 5, improves recall while preserving precision.
* **C)** The Delta source table uses partitioning by document ID, which causes Vector Search to only search within the partition matching the query's document ID — adding an `id` metadata filter to query all partitions simultaneously fixes the recall problem. *(Distractor type: Common misconception — Vector Search performs global ANN search across the entire index)*
* **D)** The Vector Search index sync is in `TRIGGERED` mode with manual syncs every 30 days — 72% of relevant chunks were added in the last 30 days and are not yet indexed. Switching to `CONTINUOUS` sync immediately restores full recall. *(Distractor type: Common misconception — if chunks were missing, Precision@5 would also be low)*

**Correct Answer:** B

**Why B is Correct:** `Recall@5 = 0.28` with `Precision@5 = 0.91` indicates that the 5 retrieved chunks are relevant (good precision) but many other relevant chunks are missed (low recall). With 8 million chunks and complex queries potentially having 15–20 truly relevant chunks, retrieving only 5 means the system misses most of them. The architectural fix is to increase `num_results` to 20–50 (a larger retrieval pool), then apply a reranker to select the best 5 for the LLM — maintaining precision while dramatically improving recall.

**Why A is Wrong:** Embedding model size does not directly cause low recall in the way described.

**Why C is Wrong:** Vector Search performs global approximate nearest neighbor search across the entire index — it does not partition searches by document ID.

**Why D is Wrong:** If chunks are missing from the index due to sync lag, Precision@5 would also be low — the fact that precision is high (91%) confirms that indexed chunks are correct; the problem is retrieval coverage, not missing data.

**Source:** Section 2: Data Preparation – Objective 6 & 8: Retrieval metrics and re-ranking

```json
{
  "id": "S2Q054",
  "source": "DB-GenAI-S2",
  "concept": "Retrieval Metrics – Low Recall Architectural Cause",
  "dimension": "Architecture",
  "difficulty": "Advanced",
  "question_type": "Diagnosis",
  "blueprint": "B",
  "taxonomy": "Analyze",
  "answer": "B"
}
```

---

### Question 55
**Difficulty:** Advanced
> **Blueprint:** B – Observed Metrics → Diagnosis
> **Concept:** Document Extraction – Unstructured Table Detection Mode
> **Dimension:** Failure Mode

A developer applies `unstructured`'s `partition_pdf()` to a financial report PDF and observes that numeric data from tables is extracted as `NarrativeText` elements instead of `Table` elements. This causes table rows to be chunked as prose sentences, losing the tabular structure. What is the root cause and the fix?

* **A)** The financial report PDF uses non-standard fonts for table cells, which causes `unstructured`'s table detector to misclassify the cells as prose text. The fix is to convert the PDF to a standard font using a PDF editing tool before running `partition_pdf()`. *(Distractor type: Common misconception — font type does not affect unstructured's table detection)*
* **B)** The `partition_pdf()` function defaults to text-layer extraction without table structure detection; enabling the table inference mode (e.g., `infer_table_structure=True` and using the `hi_res` strategy) instructs `unstructured` to use a table detection model to correctly classify and extract tabular elements.
* **C)** `unstructured` cannot detect tables in financial PDFs because financial tables use merged cells and multi-column headers; the only fix is to manually export the PDF tables to CSV files and ingest them through a separate pipeline. *(Distractor type: Common misconception — unstructured with hi_res mode handles complex financial tables)*
* **D)** The PDF tables are using a `<div>`-based HTML table simulation instead of standard PDF table structures; switching to `beautifulsoup4` as the parser correctly identifies and extracts the table data. *(Distractor type: Common misconception — PDF files do not contain HTML div elements)*

**Correct Answer:** B

**Why B is Correct:** `unstructured`'s `partition_pdf()` function operates in two modes: a fast default mode (`strategy="fast"`) that uses the PDF text layer for extraction and may not detect table structures correctly, and a high-resolution mode (`strategy="hi_res"`, `infer_table_structure=True`) that uses a computer vision-based table detection model to identify table regions and extract them as structured `Table` elements. Enabling `hi_res` mode with table inference is the correct fix.

**Why A is Wrong:** Font type does not affect `unstructured`'s table detection — table detection in `hi_res` mode uses visual layout analysis, not font metadata.

**Why C is Wrong:** `unstructured` with `hi_res` mode and `infer_table_structure=True` is designed to handle complex financial tables with merged cells.

**Why D is Wrong:** PDF files do not contain HTML `<div>` elements — PDFs use a completely different internal format (PostScript-based), and `beautifulsoup4` cannot parse PDF binary content.

**Source:** Section 2: Data Preparation – Objective 3: Choose the appropriate Python package

```json
{
  "id": "S2Q055",
  "source": "DB-GenAI-S2",
  "concept": "Document Extraction – Unstructured Table Detection Mode",
  "dimension": "Failure Mode",
  "difficulty": "Advanced",
  "question_type": "Diagnosis",
  "blueprint": "B",
  "taxonomy": "Analyze",
  "answer": "B"
}
```

---

### Question 56
**Difficulty:** Proficiency
> **Blueprint:** C – Architecture Need → Choose Architecture
> **Concept:** Delta Lake – DLT Auto-CDF for Vector Search
> **Dimension:** Architecture

A data engineering team is building a production RAG data pipeline using Delta Live Tables (DLT). The pipeline must: (1) parse PDF documents from a Volume, (2) clean and filter content, (3) chunk text, and (4) write chunks to a Delta table with CDF enabled for Vector Search sync. What is the correct DLT implementation consideration that differs from a standard notebook pipeline?

* **A)** DLT pipelines automatically enable Change Data Feed on all output Delta tables they create; the developer does not need to run `ALTER TABLE ... SET TBLPROPERTIES (delta.enableChangeDataFeed = true)` — DLT manages CDF automatically.
* **B)** DLT pipelines cannot write to Unity Catalog Delta tables; the chunked output table must be written to the Hive metastore, and a separate job must copy it to Unity Catalog before Vector Search can index it. *(Distractor type: Common misconception — DLT fully supports Unity Catalog)*
* **C)** DLT requires all Python transformation logic (PDF parsing, chunking) to be implemented using only Spark DataFrame operations; using non-Spark Python libraries like `unstructured` or `PyPDF2` inside DLT Python decorators is not supported. *(Distractor type: Common misconception — DLT Python pipelines support arbitrary Python code within decorated functions)*
* **D)** DLT streaming tables cannot be configured with `TBLPROPERTIES` at table definition time; CDF must be enabled with `ALTER TABLE` after the first pipeline run completes and the table is physically created. *(Distractor type: Partial truth — DLT streaming tables DO support TBLPROPERTIES at definition time, and DLT also enables CDF automatically)*

**Correct Answer:** A

**Why A is Correct:** One of Delta Live Tables' key features for streaming use cases is that it automatically enables Change Data Feed on all managed output tables. This is because DLT is inherently incremental and uses CDF internally for its own incremental processing. For Vector Search integration, this means DLT output tables are CDF-ready by default — a significant advantage over standard notebook pipelines that require the developer to manually enable CDF with `ALTER TABLE`.

**Why B is Wrong:** DLT fully supports Unity Catalog as the output metastore; writing to `catalog.schema.table` with `@dlt.table(name="catalog.schema.chunks")` is supported and recommended.

**Why C is Wrong:** DLT Python pipelines support arbitrary Python code within `@dlt.table` decorated functions, including non-Spark libraries like `unstructured` and `PyPDF2` via UDFs or Spark's `mapInPandas`.

**Why D is Wrong:** DLT streaming tables do support `TBLPROPERTIES` at definition time via the `@dlt.table(table_properties={"delta.enableChangeDataFeed": "true"})` decorator argument — though DLT also enables CDF automatically.

**Source:** Section 2: Data Preparation – Objective 4: Define operations and sequence to write chunked text into Delta Lake

```json
{
  "id": "S2Q056",
  "source": "DB-GenAI-S2",
  "concept": "Delta Lake – DLT Auto-CDF for Vector Search",
  "dimension": "Architecture",
  "difficulty": "Proficiency",
  "question_type": "Scenario",
  "blueprint": "C",
  "taxonomy": "Apply",
  "answer": "A"
}
```

---

### Question 57
**Difficulty:** Proficiency
> **Blueprint:** B – Observed Metrics → Diagnosis
> **Concept:** Vector Search – Multilingual Embedding Model Selection
> **Dimension:** Failure Mode

An organization's RAG pipeline serves a global team, and source documents are in English, French, German, and Japanese. The Vector Search index uses the Databricks `databricks-bge-large-en` embedding model. Users report poor retrieval for French, German, and Japanese queries even when relevant documents exist in those languages. What is the complete diagnosis and remediation?

* **A)** The `databricks-bge-large-en` model is English-only; it produces low-quality embeddings for French, German, and Japanese text because it was trained on English data. The fix is to replace it with a multilingual embedding model (e.g., `text-embedding-3-large` or `paraphrase-multilingual-mpnet-base-v2`) that produces semantically aligned cross-lingual embeddings.
* **B)** The retrieval failure is caused by the Delta table character encoding — French, German, and Japanese characters are stored as UTF-16 in the Delta table, but the embedding model requires UTF-8; the fix is to convert the Delta table's encoding to UTF-8. *(Distractor type: Common misconception — Delta Lake stores strings as UTF-8 by default)*
* **C)** The multilingual retrieval failure is caused by the Vector Search index's approximate nearest neighbor algorithm (HNSW) which can only handle Latin character embeddings; switching to an exact nearest neighbor search resolves the language limitation. *(Distractor type: Common misconception — ANN algorithms operate on float vectors and have no awareness of original character encoding)*
* **D)** The fix is to add a language detection column to each chunk and apply a metadata filter at query time that restricts retrieval to chunks in the user's detected language, eliminating cross-language retrieval issues. *(Distractor type: Partial truth — prevents cross-lingual retrieval and doesn't fix the core embedding quality issue)*

**Correct Answer:** A

**Why A is Correct:** The `databricks-bge-large-en` model (BGE Large English) is trained on English text and produces high-quality embeddings for English. Its embedding space is not aligned with French, German, or Japanese text — non-English queries will not produce embedding vectors that are close to the corresponding non-English document embeddings, causing retrieval failure. The fix is a multilingual embedding model that maps text in different languages to a shared semantic embedding space.

**Why B is Wrong:** Delta Lake stores strings as UTF-8 by default in Parquet files, and embedding models accept Python strings; encoding is not the source of multilingual retrieval failure.

**Why C is Wrong:** The approximate nearest neighbor algorithm (HNSW or similar) operates on vectors of floating-point numbers — it has no awareness of the original character encoding or language; the language problem is in the embedding model, not the search algorithm.

**Why D is Wrong:** Language-based metadata filtering restricts users to retrieving documents in their own language — this prevents cross-lingual retrieval and does not address the core embedding quality issue.

**Source:** Section 2: Data Preparation – Objective 1 & 4: Chunking constraints and Delta Lake setup

```json
{
  "id": "S2Q057",
  "source": "DB-GenAI-S2",
  "concept": "Vector Search – Multilingual Embedding Model Selection",
  "dimension": "Failure Mode",
  "difficulty": "Proficiency",
  "question_type": "Diagnosis",
  "blueprint": "B",
  "taxonomy": "Analyze",
  "answer": "A"
}
```

---

### Question 58
**Difficulty:** Proficiency
> **Blueprint:** C – Architecture Need → Choose Architecture
> **Concept:** Advanced Chunking – Section-Aware for API Reference Docs
> **Dimension:** Architecture

A developer is designing the chunking strategy for a knowledge base of 10,000 API reference documents. Each document has a fixed structure: `Overview` (100–200 tokens), `Parameters` (50–500 tokens depending on API complexity), `Examples` (200–800 tokens), and `Error Codes` (100–300 tokens). Users query specific sections (e.g., "What parameters does the /users endpoint accept?"). What chunking design provides optimal retrieval precision?

* **A)** Apply fixed-size 512-token chunking across all sections of all documents, treating the entire document as flat text and relying on the embedding model to implicitly learn the section structure from repeated section header tokens. *(Distractor type: Common misconception — fixed-size chunking ignores document structure and mixes section content)*
* **B)** Apply section-aware chunking: use the document's section headers as split boundaries, creating separate chunks for `Overview`, `Parameters`, `Examples`, and `Error Codes` — each chunk prefixed with `[Document: /users API] [Section: Parameters]` metadata to enable targeted retrieval.
* **C)** Apply Parent-Child chunking where each full API document is the parent and each token within the document is the child chunk, enabling the retrieval of the exact token that matches the query. *(Distractor type: Beginner mistake — individual tokens as child chunks is computationally absurd and semantically meaningless)*
* **D)** Apply no chunking — store each entire API reference document as one chunk per document, relying on the LLM's 128K context window to process all 10,000 documents simultaneously for each user query. *(Distractor type: Extreme statement — passing all 10,000 documents is computationally impossible)*

**Correct Answer:** B

**Why B is Correct:** Given the consistent, predictable section structure of API reference documents and the highly targeted nature of user queries (users ask about specific sections, not entire documents), section-aware chunking is optimal. Each section becomes its own chunk, and the metadata prefix (`[Document: /users API] [Section: Parameters]`) enriches the embedding with contextual information that helps the retriever match section-specific queries with high precision.

**Why A is Wrong:** Fixed-size chunking ignores the document structure and mixes section content across chunks, reducing precision for section-specific queries.

**Why C is Wrong:** Using individual tokens as child chunks is computationally absurd and semantically meaningless; child chunks in Parent-Child should be semantically coherent (sentences or paragraphs), not individual tokens.

**Why D is Wrong:** Vector Search requires chunked text as rows in a Delta table; storing an entire document as one row would likely exceed the embedding model's token limit and reduce retrieval precision.

**Source:** Section 2: Data Preparation – Objective 1 & 7: Chunking strategy and advanced chunking

```json
{
  "id": "S2Q058",
  "source": "DB-GenAI-S2",
  "concept": "Advanced Chunking – Section-Aware for API Reference Docs",
  "dimension": "Architecture",
  "difficulty": "Proficiency",
  "question_type": "Scenario",
  "blueprint": "C",
  "taxonomy": "Evaluate",
  "answer": "B"
}
```

---

### Question 59
**Difficulty:** Proficiency
> **Blueprint:** B – Observed Metrics → Diagnosis
> **Concept:** Knowledge Base Lifecycle – Data Governance vs. Retrieval Quality
> **Dimension:** Best Practice

A RAG pipeline serves a compliance team that queries a knowledge base of 500,000 regulatory documents. A compliance officer reports: "The chatbot sometimes references documents that were superseded by newer regulations — it mixes old and new guidance." Retrieval metrics show `Precision@5 = 0.88` and `Recall@5 = 0.79`. What is the correct diagnosis — is this a retrieval quality problem or a data governance problem — and what is the right fix?

* **A)** This is a retrieval quality problem — `Precision@5 = 0.88` is below the 0.95 threshold required for regulatory use cases; improving the embedding model and adding a cross-encoder reranker will prevent outdated documents from being retrieved. *(Distractor type: Common misconception — 0.88 precision is healthy; this is a governance issue, not a retrieval quality issue)*
* **B)** This is a data governance problem, not a retrieval quality problem — the retrieval metrics are healthy (88% precision, 79% recall), meaning the retriever correctly finds the most semantically similar documents. The issue is that superseded documents are still present and active in the knowledge base. The fix is a data lifecycle process: add a `status` column (`active`/`superseded`) to the source Delta table, update superseded documents to `status='superseded'`, and apply a metadata filter `status='active'` at query time.
* **C)** This is a retrieval quality problem — `Recall@5 = 0.79` means 21% of relevant regulatory documents are missed per query; improving `num_results` to 25 and adding a reranker will surface all active regulations including the most recent ones. *(Distractor type: Common misconception — improving recall retrieves more superseded documents, worsening the problem)*
* **D)** This is a data governance problem that requires re-training the embedding model on only the current, active regulatory documents, so that embeddings for superseded documents become dissimilar to user queries and are naturally deprioritized by Vector Search. *(Distractor type: Beginner mistake — re-training is expensive and imprecise; metadata filtering is the correct, deterministic solution)*

**Correct Answer:** B

**Why B is Correct:** The retrieval metrics (Precision@5 = 0.88, Recall@5 = 0.79) indicate the retrieval system is performing well — it correctly surfaces the most semantically similar documents. The problem is that "semantically similar" includes superseded documents that are topically related to the query but contain outdated guidance. This is a data governance failure, not a retrieval failure. The correct fix is a data lifecycle management process: mark superseded documents with a `status='superseded'` flag and filter them out at query time.

**Why A is Wrong:** 0.88 precision is not the cause of the compliance issue — even perfect precision of 1.0 would not prevent semantically relevant but superseded documents from being retrieved if they remain active in the index.

**Why C is Wrong:** Improving recall retrieves more superseded documents, making the problem worse.

**Why D is Wrong:** Re-training the embedding model is expensive and imprecise; metadata filtering is the correct, deterministic, and maintainable governance solution.

**Source:** Section 2: Data Preparation – Objective 5 & 6: Identify source documents and evaluate retrieval

```json
{
  "id": "S2Q059",
  "source": "DB-GenAI-S2",
  "concept": "Knowledge Base Lifecycle – Data Governance vs. Retrieval Quality",
  "dimension": "Best Practice",
  "difficulty": "Proficiency",
  "question_type": "Diagnosis",
  "blueprint": "B",
  "taxonomy": "Evaluate",
  "answer": "B"
}
```

---

### Question 60
**Difficulty:** Proficiency
> **Blueprint:** C – Architecture Need → Choose Architecture
> **Concept:** Advanced Chunking – Hierarchical Section Chunking for Long Papers
> **Dimension:** Architecture

A team is building a RAG pipeline for 200,000 scientific papers in biology. Each paper averages 15,000 tokens. They use Parent-Child chunking: each paper's abstract (200–500 tokens) as child chunks for vector search, with the full paper as parent context. A researcher reports: "When I ask detailed methodology questions, the answers are missing key experimental details." Investigation confirms the relevant methodology section exists in the full paper (parent) but is 4,000–6,000 tokens into the paper. What is the flaw in this design, and what is the fix?

* **A)** The flaw is that the abstract (child chunk) correctly identifies the paper but the full paper (parent, ~15,000 tokens) exceeds most LLMs' useful context window — the LLM receives the full paper but loses the methodology section buried at 4,000–6,000 tokens in due to the "lost in the middle" phenomenon. The fix is to add methodology section chunks as additional child chunks, enabling direct retrieval of the methodology section as a focused child with the surrounding section (not full paper) as parent.
* **B)** The flaw is that biology papers use domain-specific terminology that the embedding model cannot encode accurately; the abstract's general language creates embedding vectors that don't match methodology-specific queries. The fix is to fine-tune the embedding model on biology paper abstracts. *(Distractor type: Common misconception — the issue is context position, not embedding model vocabulary)*
* **C)** The flaw is that parent chunks (full papers at 15,000 tokens) exceed the Vector Search maximum document size of 8,192 tokens per chunk; storing full papers in Vector Search raises an exception. The fix is to limit parent chunks to 8,192 tokens by truncating papers at that limit. *(Distractor type: Common misconception — parent chunks are stored in the Delta table, not in Vector Search; only child embeddings are vectorized)*
* **D)** The flaw is that the methodology section requires structured tabular data that the LLM cannot process from plain text; converting methodology sections to JSON structured format before storing in the Delta table enables the LLM to correctly interpret experimental parameters. *(Distractor type: Common misconception — the issue is context window positioning, not data format)*

**Correct Answer:** A

**Why A is Correct:** This is a nuanced Parent-Child design flaw. The abstract correctly retrieves the right paper (high recall at the paper level) but the parent context (full 15,000-token paper) overwhelms the LLM — methodology details buried at positions 4,000–6,000 in a 15,000-token paper are subject to the "lost in the middle" phenomenon where LLMs attend less to content in the middle of very long contexts. The fix is hierarchical chunking with multiple child types: embed both the abstract AND the individual section chunks (abstract, introduction, methods, results, conclusion) as children. A methodology query then retrieves the methods child chunk directly, and its parent context is the methods section (~1,500–2,000 tokens) rather than the entire 15,000-token paper.

**Why B is Wrong:** While domain-specific terminology is a real concern, the described problem (methodology details in the parent paper not being surfaced) is a context position problem, not an embedding model vocabulary problem.

**Why C is Wrong:** The parent chunks (full papers) are stored in the Delta table, not in Vector Search — only the child embeddings (abstracts) are stored as vectors in the Vector Search index.

**Why D is Wrong:** The issue is context window positioning, not data format; biology methodology sections in plain text are fully processable by LLMs.

**Source:** Section 2: Data Preparation – Objective 7: Design retrieval systems using advanced chunking strategies

```json
{
  "id": "S2Q060",
  "source": "DB-GenAI-S2",
  "concept": "Advanced Chunking – Hierarchical Section Chunking for Long Papers",
  "dimension": "Architecture",
  "difficulty": "Proficiency",
  "question_type": "Scenario",
  "blueprint": "C",
  "taxonomy": "Evaluate",
  "answer": "A"
}
```
