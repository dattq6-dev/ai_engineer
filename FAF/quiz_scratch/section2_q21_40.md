### Question 21
**Difficulty:** Beginner

A developer needs to split a 50-page PDF user manual into chunks for a RAG pipeline. The manual is written in continuous plain prose with no consistent heading structure. Which chunking method is most reliable given this document structure?

A) Document-aware chunking using Markdown header boundaries — the splitter detects `#`, `##`, and `###` headers and uses them as split points to keep related sections together in each chunk.
B) Fixed-size chunking with an appropriate token limit and small overlap — it splits the text at a consistent token count with overlap to avoid losing context at boundaries, regardless of document structure.
C) Semantic chunking using a topic model — the chunker runs an LDA topic model on the full PDF and groups sentences by topic, placing all sentences with the same dominant topic into a single chunk.
D) Table-based chunking — the chunker detects table boundaries in the PDF and uses each table cell as a single chunk, which is appropriate for prose documents that lack explicit section headers.

**Correct Answer:** B
**Explanation:** B is correct. For a plain prose document with no consistent structural markers (no Markdown headers, no HTML tags, no section dividers), document-aware or header-based chunking cannot find split points. Fixed-size chunking with overlap is the reliable fallback — it splits at a consistent token count and uses overlap to prevent losing context at chunk boundaries. A is wrong because document-aware Markdown header chunking requires the document to actually have Markdown headers (`#`, `##`); a PDF with plain prose has no such headers and the splitter would find no split points or produce a single giant chunk. C is wrong because running an LDA topic model as a chunking strategy is extremely computationally expensive, slow, and non-standard for production RAG pipelines; topic modeling at inference time is not a supported chunking strategy on Databricks. D is wrong because table-based chunking is designed for documents with tabular data, not continuous prose; applying it to prose would produce incorrect and nonsensical splits.
**Source:** Section 2: Data Preparation – Objective 1: Apply a chunking strategy for a given document structure and model constraints — docs.databricks.com (search: "Data preparation for RAG applications")

---

### Question 22
**Difficulty:** Beginner

A developer is preparing a Delta table to serve as the source for a Databricks Vector Search index. They realize the table has no primary key column. Why is a unique `id` column required?

A) The Vector Search index uses the `id` column as the vector embedding storage key, mapping each unique ID to its corresponding high-dimensional vector in the FAISS index file.
B) The `id` column is required so that Vector Search can uniquely identify each chunk during delta sync operations — specifically to detect which chunks have been updated or deleted and apply those changes incrementally.
C) Unity Catalog enforces that all Delta tables used by AI services must have a primary key column for compliance auditing, so that the data lineage of each chunk can be traced back to its original document.
D) The `id` column is used by the LLM at inference time to cite the exact source document and chunk position in its response, enabling automatic footnote generation in the chatbot's answers.

**Correct Answer:** B
**Explanation:** B is correct. Databricks Vector Search uses the `id` column to uniquely identify each row (chunk) in the source Delta table. During incremental sync operations, the Vector Search pipeline uses Change Data Feed records alongside the `id` to determine which specific rows have been inserted, updated, or deleted — and applies those changes to the index precisely. Without a unique `id`, the index cannot correctly perform row-level updates or deletions. A is wrong because the `id` column is a logical identifier for the chunk in the Delta table, not the key used to store the embedding vector in the underlying vector storage; embeddings are stored internally by the Vector Search service. C is wrong because Unity Catalog does not require a primary key column for AI service compliance; the `id` requirement is a Vector Search operational requirement, not a governance policy. D is wrong because the LLM does not use the `id` column from the Delta table at inference time; citation is a separate application-level feature built on top of the retrieved chunk metadata, not an automatic behavior driven by the `id` column.
**Source:** Section 2: Data Preparation – Objective 4: Define operations and sequence to write chunked text into Delta Lake — docs.databricks.com (search: "Create a Mosaic AI Vector Search index")

---

### Question 23
**Difficulty:** Beginner

A developer uses `beautifulsoup4` to extract text from HTML pages. They run `soup.get_text()` and get back a string, but it contains many unwanted newlines, tab characters, and whitespace runs from the original HTML formatting. What should they do before writing this text to a Delta table for chunking?

A) Re-parse the HTML with `pytesseract` OCR after rendering the page to an image, which produces cleaner text by re-reading the visual characters rather than the raw HTML source text.
B) Apply string cleaning operations — strip leading/trailing whitespace, collapse multiple consecutive whitespace characters, and remove newlines from within sentences — to normalize the extracted text.
C) Write the raw uncleaned text to the Delta table and rely on the embedding model to normalize whitespace during the vectorization process, since embedding models ignore whitespace tokens.
D) Convert the HTML to PDF first using `pdfkit`, then use `PyPDF2` to extract clean text, which strips HTML formatting artifacts and produces uniform paragraph text automatically.

**Correct Answer:** B
**Explanation:** B is correct. After extracting raw text from HTML using `soup.get_text()`, the output typically contains formatting artifacts from the original HTML structure — excessive newlines (from `<br>`, `<p>` tags), tabs, and whitespace runs. Standard text cleaning (using Python's `str.strip()`, `re.sub(r'\s+', ' ', text)`, and similar operations) normalizes the text before it is chunked and embedded, ensuring cleaner, higher-quality chunks. A is wrong because converting a text-based HTML page to an image and running OCR is a wasteful, lossy approach; OCR introduces errors and is designed for image-based documents where digital text is unavailable. C is wrong because embedding models do NOT normalize whitespace — they tokenize the input as-is, and excessive whitespace tokens reduce the effective content density of the embedding. D is wrong because HTML → PDF → text extraction is a multi-step conversion that adds complexity and potential content loss; direct HTML text cleaning via BeautifulSoup is simpler, faster, and more reliable.
**Source:** Section 2: Data Preparation – Objective 2: Filter extraneous content in source documents — docs.databricks.com (search: "Generative AI data preparation")

---

### Question 24
**Difficulty:** Beginner

A team has a collection of `.docx` Word documents that they want to parse for a RAG pipeline. Which Python library is most appropriate for extracting text content from Word documents on Databricks?

A) `beautifulsoup4` — because Word documents are internally structured as ZIP archives containing XML files, and BeautifulSoup can parse XML to extract text from the document body elements.
B) `pytesseract` — because Word documents are often printed and scanned, making OCR the standard text extraction approach for this document format in enterprise pipelines.
C) `unstructured` — because it natively supports `.docx` Word document parsing, extracting text with structural awareness (distinguishing headings from body text) without requiring manual XML parsing.
D) `PyPDF2` — because Word documents and PDF files use the same underlying binary format, and PyPDF2's universal document reader handles both `.pdf` and `.docx` file extensions.

**Correct Answer:** C
**Explanation:** C is correct. The `unstructured` library is the recommended multi-format document parsing tool for RAG pipelines. It natively reads `.docx` files using the python-docx backend and returns structured elements (Title, NarrativeText, Table, etc.), making it easy to filter and process different content types from Word documents. A is wrong because while Word's `.docx` format is internally an XML structure, using `beautifulsoup4` for XML parsing requires significant manual handling of namespace prefixes and schema knowledge; `unstructured` abstracts this complexity. B is wrong because `.docx` files contain embedded digital text — OCR is only needed for scanned image files where no digital text layer exists. Using pytesseract on a standard Word document would be unnecessarily complex and lossy. D is wrong because Word and PDF are completely different binary formats with different internal structures; `PyPDF2` can only read PDF files and has no capability to parse `.docx` documents.
**Source:** Section 2: Data Preparation – Objective 3: Choose the appropriate Python package — docs.databricks.com (search: "RAG reference architecture data preparation")

---

### Question 25
**Difficulty:** Beginner

A developer is curating documents for a customer support RAG chatbot. They have access to: (A) official product FAQs updated monthly, (B) internal Slack message threads from the support team, and (C) competitor product reviews from public websites. Which documents should be excluded, and why?

A) Exclude source A (official FAQs) because monthly updates mean the information is stale for 30 days; real-time Slack threads (source B) provide more current information for customer queries.
B) Exclude sources B and C — Slack threads contain informal, unverified, and potentially incorrect troubleshooting advice, and competitor reviews introduce off-topic and potentially misleading information into the knowledge base.
C) Include all three sources to maximize knowledge breadth; the LLM will automatically disregard low-quality content from Slack threads and competitor reviews when generating answers for customer queries.
D) Exclude source A (official FAQs) and include only sources B and C because the chatbot needs to understand real-world customer language patterns, which Slack threads and public reviews provide more authentically.

**Correct Answer:** B
**Explanation:** B is correct. Slack threads (B) contain informal, unverified advice — support agents may share workarounds, incorrect steps, or personal opinions that are not official guidance. Including these pollutes the knowledge base with potentially incorrect information. Competitor product reviews (C) are entirely off-topic for a customer support chatbot — they would cause the retriever to surface competitor product information in response to customer queries, which is harmful and potentially embarrassing. Only the official FAQs (A) provide verified, authoritative, on-topic content. A is wrong because monthly-updated official FAQs are authoritative — even if 30 days old, they represent the current official guidance. Slack threads are NOT more reliable simply because they are more recent. C is wrong because LLMs cannot reliably "ignore" retrieved context that they are given; if the retriever returns incorrect Slack advice, the LLM is likely to incorporate it into the answer. D is wrong because understanding customer language patterns is a training-time concern for the LLM, not a knowledge base curation decision; the knowledge base should contain only authoritative, accurate information.
**Source:** Section 2: Data Preparation – Objective 5: Identify needed source documents — docs.databricks.com (search: "Generative AI data preparation best practices")

---

### Question 26
**Difficulty:** Intermediate

A developer uses recursive character text splitting on a 200-page technical manual. They set `chunk_size=400` tokens and `chunk_overlap=40` tokens. They observe that some chunks contain only 15–20 tokens (mostly section titles that appear alone after a split). What is the impact of these tiny chunks on the RAG pipeline, and what is the fix?

A) Tiny chunks improve retrieval precision because the embedding model can produce highly focused embeddings for short, specific text; the developer should keep them and reduce `chunk_size` further to create more fine-grained chunks.
B) Tiny chunks create poor embeddings that are underrepresented in the vector space — their embedding captures only a heading with minimal semantic content, meaning they will consume a top-k retrieval slot while providing almost no useful context to the LLM. The fix is to set a `min_chunk_size` threshold to merge or discard chunks below a minimum token count.
C) Tiny chunks only affect the storage cost of the Delta table since each row occupies a fixed storage overhead regardless of text length; they have no meaningful impact on retrieval quality or LLM answer generation.
D) Tiny chunks cause the Vector Search index to fail during sync because the embedding model raises an error when it receives fewer than 50 tokens as input, rejecting the chunk and preventing it from being added to the index.

**Correct Answer:** B
**Explanation:** B is correct. A chunk containing only a section heading like "Chapter 4: Configuration" has minimal semantic content — its embedding is essentially a representation of a header phrase, not of any knowledge. When retrieved, it provides almost no useful context for the LLM to generate an answer, yet it occupies one of the precious top-k retrieval slots. The fix is to apply a `min_chunk_size` filter (e.g., 50 tokens) that either merges tiny chunks with the next chunk or discards them entirely. A is wrong because there is a meaningful lower bound below which chunk size hurts quality rather than helping precision — a 15-token heading phrase does not benefit from a focused embedding; it simply lacks content. C is wrong because tiny chunks do meaningfully impact retrieval quality by occupying retrieval slots with low-information-content embeddings, degrading the quality of context passed to the LLM. D is wrong because embedding models accept input strings of any length down to a single token; they do not raise errors for short inputs, though the quality of very short-text embeddings is poor.
**Source:** Section 2: Data Preparation – Objective 1: Apply a chunking strategy — docs.databricks.com (search: "Data preparation for RAG applications")

---

### Question 27
**Difficulty:** Intermediate

A team uses `mlflow.genai.evaluate()` to assess retrieval quality and gets `Precision@5 = 0.76` and `Recall@5 = 0.52`. The product manager asks which metric is more important for a customer-facing medical symptom checker chatbot. What is the correct reasoning?

A) Precision@5 is more important because the medical chatbot must never return irrelevant information — a hallucinated medical fact from an off-topic chunk could cause the user to make a dangerous health decision.
B) Recall@5 is more important because missing a relevant medical document (e.g., a critical drug interaction warning) is more dangerous than retrieving a slightly off-topic chunk; the chatbot must ensure it surfaces all relevant medical information.
C) Both metrics are equally important and must both reach 1.0 before a medical chatbot can be deployed; partial retrieval quality is not acceptable in any medical application context.
D) Neither metric is relevant for a medical chatbot; the correct metric is `AnswerCorrectness`, which measures whether the final LLM response is factually correct, not whether individual retrieved chunks are relevant.

**Correct Answer:** B
**Explanation:** B is correct. In a medical context, missing relevant information (low recall) is the more dangerous failure mode. A missed drug interaction warning or contraindication could lead a user to make an unsafe decision. Retrieving a slightly off-topic chunk (lower precision) is less dangerous because the LLM is less likely to synthesize irrelevant text into a harmful answer. This is a classic recall vs. precision prioritization decision based on the asymmetry of error consequences. A is wrong because while precision matters, the medical context prioritizes not missing critical information over not retrieving irrelevant information — the asymmetry of harm favors recall. C is wrong because perfect scores (1.0) are not achievable in real-world RAG systems due to query-document semantic gaps and retrieval model limitations; setting 1.0 as a deployment criterion is impractical. D is wrong because retrieval metrics (Precision@k, Recall@k) and answer metrics (AnswerCorrectness) both matter and measure different things; dismissing retrieval metrics is incorrect — poor retrieval directly causes poor answer quality.
**Source:** Section 2: Data Preparation – Objective 6: Use tools and metrics to evaluate retrieval performance — docs.databricks.com (search: "MLflow evaluate for RAG")

---

### Question 28
**Difficulty:** Intermediate

A developer wants to ensure that when the source Delta table `main.docs.policy_chunks` is updated with new policy documents, the changes propagate to the Vector Search index automatically without manual intervention. They configure the Vector Search index with `pipeline_type="CONTINUOUS"`. What prerequisite must be met on the source Delta table?

A) The source Delta table must be partitioned by the `document_date` column so that the CONTINUOUS sync pipeline can efficiently identify which partitions contain new data during each micro-batch scan.
B) The source Delta table must have Change Data Feed enabled (`delta.enableChangeDataFeed = true`) so the CONTINUOUS sync pipeline can read the incremental change records and propagate only the new, updated, or deleted rows.
C) The source Delta table must be registered in the Hive metastore (not Unity Catalog) because CONTINUOUS sync mode only supports Hive metastore tables, not Unity Catalog-managed tables with governance policies.
D) The source Delta table must be stored on Azure Data Lake Storage Gen2 or AWS S3, because CONTINUOUS sync mode requires a cloud object storage backend; local cluster storage (DBFS root) is not supported for real-time sync pipelines.

**Correct Answer:** B
**Explanation:** B is correct. Databricks Vector Search CONTINUOUS sync uses Change Data Feed to detect and propagate changes from the source Delta table in near-real-time. Without CDF enabled on the source table, the sync pipeline has no mechanism to detect incremental changes and will fail. CDF must be enabled before the Vector Search index is created (using `ALTER TABLE ... SET TBLPROPERTIES (delta.enableChangeDataFeed = true)`). A is wrong because partitioning by date is a query optimization for analytics, not a prerequisite for Vector Search sync; CONTINUOUS mode reads CDF records regardless of partition structure. C is wrong because Databricks Vector Search fully supports Unity Catalog-managed Delta tables — Unity Catalog is in fact the recommended governance layer for Vector Search source tables. D is wrong because CONTINUOUS sync requirements relate to CDF (a Delta Lake feature) and Unity Catalog governance, not to specific cloud storage backends; DBFS root tables can also be used, though Unity Catalog-managed tables are preferred.
**Source:** Section 2: Data Preparation – Objective 4: Define operations and sequence to write chunked text into Delta Lake — docs.databricks.com (search: "Create a Mosaic AI Vector Search index")

---

### Question 29
**Difficulty:** Intermediate

A developer is building a RAG pipeline for a company that sells both software products and hardware products. The knowledge base contains 50,000 chunks covering both product lines. Users sometimes ask software questions but retrieve hardware documentation and vice versa. What data preparation change best addresses this cross-contamination problem?

A) Increase the Vector Search index `num_results` to 20 so the correct chunks from the right product line are more likely to appear somewhere in the retrieved set before passing them to the LLM.
B) Add a `product_line` metadata column (`software` or `hardware`) to each chunk in the source Delta table, and apply metadata filtering at query time so each query only searches within the relevant product line's chunks.
C) Train a custom fine-tuned embedding model on combined software and hardware documentation so the embedding space naturally separates the two product domains and reduces cross-domain retrieval confusion.
D) Create two separate Databricks workspaces — one for the software knowledge base and one for the hardware knowledge base — routing user queries to the appropriate workspace based on keyword matching.

**Correct Answer:** B
**Explanation:** B is correct. Adding a `product_line` metadata filter is the most targeted and operationally efficient fix. Databricks Vector Search supports metadata filtering — you can add a column (e.g., `product_line: string`) to the source Delta table and pass a filter expression at query time (e.g., `filters_json='{"product_line": "software"}'`) to restrict the search to only relevant chunks. This eliminates cross-contamination at the retrieval layer without requiring model retraining or architectural changes. A is wrong because increasing `num_results` retrieves more chunks but does not filter by product line — you'd get more chunks from both product lines, making the cross-contamination problem potentially worse as more off-topic chunks are passed to the LLM. C is wrong because fine-tuning a custom embedding model is an expensive, time-consuming process that requires labeled training data; metadata filtering achieves the same result with zero training cost. D is wrong because splitting into two workspaces is extreme engineering overhead — separate Unity Catalog schemas or separate Vector Search indexes within one workspace achieve the same isolation far more efficiently.
**Source:** Section 2: Data Preparation – Objective 5: Identify needed source documents — docs.databricks.com (search: "Mosaic AI Vector Search index" and "Generative AI data preparation best practices")

---

### Question 30
**Difficulty:** Intermediate

A developer instruments their RAG retrieval function with `@mlflow.trace(span_type="RETRIEVER")`. When they inspect the captured trace in the MLflow UI, what information appears in this span?

A) The span shows the LLM's generated response along with the confidence scores that the LLM internally assigned to each retrieved chunk when deciding how much weight to give each document.
B) The span shows the query vector (the numerical embedding array) that was sent to the Vector Search index and the raw cosine similarity scores of the top-k matching embeddings.
C) The span shows the input query string, the retrieved document chunks (text content and metadata), and timing information — allowing MLflow evaluators to assess what the retriever received and returned.
D) The span shows the Delta table transaction log entries that were read during the retrieval, including the CDF records that indicate which rows were recently updated in the source table.

**Correct Answer:** C
**Explanation:** C is correct. The `RETRIEVER` span type in MLflow Tracing captures the inputs and outputs of the retrieval step as structured metadata in the trace tree. Specifically, it records the input (the user query string), the outputs (the retrieved document chunks, including their text content and metadata such as `doc_id`, `source`, similarity score), and timing information. MLflow's `RetrievalRelevance` scorer then reads these captured inputs/outputs from the span to perform LLM-judge-based relevance evaluation. A is wrong because LLMs do not expose internal confidence scores per retrieved document — the LLM processes the assembled prompt without providing per-chunk weighting metadata back to the application. B is wrong because the `RETRIEVER` span captures the text-level inputs and outputs for evaluation purposes — it does not expose the raw numerical embedding vector or internal cosine similarity computations from the Vector Search service. D is wrong because the `RETRIEVER` span captures the RAG pipeline's retrieval step inputs/outputs, not the underlying Delta table transaction log; CDF records are an internal sync mechanism, not exposed in the retrieval trace.
**Source:** Section 2: Data Preparation – Objective 6: Use tools and metrics to evaluate retrieval performance — docs.databricks.com (search: "MLflow Tracing")

---

### Question 31
**Difficulty:** Advanced

A developer applies document-aware chunking to a Markdown knowledge base. Articles are split on `##` headers. One article's section titled "## Troubleshooting" contains 4,200 tokens — far exceeding the 512-token embedding model limit. What is the correct approach to handle this oversized section?

A) Skip the "Troubleshooting" section entirely and exclude it from the knowledge base because sections exceeding the embedding model limit cannot be ingested without data loss.
B) Apply a two-level chunking strategy: use header-based splitting at the `##` level first, then apply recursive character splitting on any resulting chunk that exceeds 512 tokens, preserving header-level structure where possible.
C) Increase the embedding model's token limit by setting a `max_tokens=4200` parameter in the embedding model API call, which instructs the model to expand its context window for this specific oversized section.
D) Replace the document-aware chunker with a single global fixed-size chunker set to 4,200 tokens across the entire knowledge base so that the largest section fits within one chunk without being split.

**Correct Answer:** B
**Explanation:** B is correct. A two-level approach handles this gracefully: first split on `##` headers to preserve section-level structure (which is the goal of document-aware chunking), then apply recursive character splitting to any section that exceeds the 512-token limit to bring it within bounds. This preserves as much semantic structure as possible while respecting the hard model constraint. A is wrong because skipping entire sections means losing potentially critical knowledge — the troubleshooting section is likely highly relevant to user queries and should not be excluded. C is wrong because embedding model context windows are fixed by the model architecture; there is no `max_tokens` parameter that expands the model's capacity at inference time. D is wrong because setting a 4,200-token chunk size breaks all other sections in the knowledge base — short sections would become tiny chunks, and most sections would vastly exceed the 512-token embedding limit, degrading the entire pipeline for the sake of one outlier section.
**Source:** Section 2: Data Preparation – Objective 1 & 7: Chunking strategy and advanced chunking — docs.databricks.com (search: "Advanced chunking strategies RAG")

---

### Question 32
**Difficulty:** Advanced

A RAG evaluation shows `Precision@5 = 0.94` but the LLM is still generating answers with hallucinations and missing important details. The retrieved chunks are highly relevant but engineers discover the LLM context window only receives ~400 tokens per query (limited by the 5 small child chunks of ~80 tokens each in a Parent-Child setup). What is the architectural fix?

A) Reduce the number of retrieved chunks from 5 to 2 to concentrate the LLM's attention on the most relevant content, which reduces hallucinations by minimizing the amount of context the LLM must process.
B) Switch from Parent-Child chunking to pure small-chunk retrieval, removing the parent chunk fetching step to reduce context size and make the LLM rely more on its parametric knowledge for complete answers.
C) The child chunks are correctly retrieved (high precision), but the LLM receives only child-level context (80 tokens each). The fix is to implement the Parent-Child fetch correctly — retrieve parent chunks (~500–1,000 tokens) corresponding to the matched children, providing richer context to the LLM.
D) Add more Vector Search metadata filters to narrow the retrieval set further, which reduces the number of chunks from 5 to 1–2 and forces the LLM to focus exclusively on the single most relevant passage.

**Correct Answer:** C
**Explanation:** C is correct. This is exactly the problem Parent-Child chunking is designed to solve — and the description reveals it's not being implemented correctly. High Precision@5 confirms the right child chunks are being found. But if only the small child chunks (80 tokens) are passed to the LLM, the LLM lacks sufficient surrounding context for complete answers. The correct implementation fetches the parent chunk (the larger parent section, e.g., 500–1,000 tokens) corresponding to each matched child chunk and sends those parent chunks to the LLM instead. This provides rich context while maintaining precise retrieval. A is wrong because reducing from 5 to 2 chunks reduces the amount of context even further, exacerbating the problem. B is wrong because removing the parent chunk step means losing the architectural benefit entirely — without parent chunks, the LLM still only gets 80-token child chunks, which is the exact problem. D is wrong because further narrowing to 1–2 chunks reduces context coverage and increases the risk of missing important details rather than fixing the hallucination caused by insufficient context.
**Source:** Section 2: Data Preparation – Objective 7: Design retrieval systems using advanced chunking strategies — docs.databricks.com (search: "Advanced chunking strategies RAG")

---

### Question 33
**Difficulty:** Advanced

A developer runs `mlflow.genai.evaluate()` on a RAG pipeline and gets `RetrievalRelevance = 0.89`. They present this to a stakeholder who asks: "Does this mean 89% of our retrieved chunks are factually correct?" How should the developer respond?

A) Yes — `RetrievalRelevance = 0.89` means that the LLM judge confirmed 89% of the retrieved chunks contain factually accurate information verified against an external truth source.
B) No — `RetrievalRelevance` measures whether retrieved chunks are relevant to the user's query (topically related), not whether their content is factually correct. A chunk can be highly relevant (about the right topic) but contain outdated or incorrect facts.
C) Yes — `RetrievalRelevance` uses an LLM judge that cross-references each retrieved chunk against a verified ground-truth database, so a score of 0.89 confirms 89% of chunks are both relevant and factually verified.
D) No — `RetrievalRelevance = 0.89` means that 89% of all the chunks in the Vector Search index (not just retrieved chunks) are relevant to the total set of queries in the evaluation dataset, measuring overall index coverage.

**Correct Answer:** B
**Explanation:** B is correct. `RetrievalRelevance` is a topical relevance metric — the LLM judge assesses whether each retrieved chunk is about the right topic relative to the user's query. It does not verify factual accuracy. A chunk about "password reset procedures" is highly relevant to a "how do I reset my password?" query even if the reset steps described are outdated and incorrect. Factual correctness is measured by a different set of metrics (e.g., `AnswerCorrectness` with ground truth, or `Groundedness` for answer-context consistency). A is wrong because `RetrievalRelevance` does not perform factual verification — it only assesses topical relevance using an LLM judge that has no access to an external ground-truth database. C is wrong for the same reason as A — no ground-truth database is consulted during `RetrievalRelevance` scoring. D is wrong because `RetrievalRelevance` measures the quality of retrieved chunks for specific queries in the evaluation set, not the overall relevance of all chunks in the entire index.
**Source:** Section 2: Data Preparation – Objective 6: Use tools and metrics to evaluate retrieval performance — docs.databricks.com (search: "MLflow evaluate for RAG")

---

### Question 34
**Difficulty:** Advanced

A developer filters extraneous content from HTML documents using BeautifulSoup. Their cleaning function removes all `<nav>`, `<footer>`, `<header>`, and `<aside>` tags. During evaluation, users report the chatbot cannot answer questions about table data from the source HTML pages. Investigation reveals the HTML tables are being stripped. What went wrong?

A) BeautifulSoup's `get_text()` method automatically strips all HTML table content (`<table>`, `<tr>`, `<td>` tags) regardless of the developer's filter configuration, converting tables to empty strings.
B) The developer's filter is too broad — their code likely removes all tags rather than only the specified structural tags, stripping `<table>` elements along with the navigation and footer elements they intended to remove.
C) HTML tables require a separate `pytesseract` OCR pass because BeautifulSoup cannot parse `<table>` tags in standard HTML; tables are treated as binary image elements by the HTML parser.
D) The Vector Search embedding model does not support tabular data formats — when a chunk contains HTML table content, the embedding computation fails silently and the chunk is not indexed.

**Correct Answer:** B
**Explanation:** B is correct. The most likely error is over-aggressive filtering. A common mistake is using `soup.get_text()` directly after removing specific tags, or applying a filter like `for tag in soup.find_all(True): tag.decompose()` that removes ALL tags (including `<table>`, `<tr>`, `<td>`) instead of only the intended structural navigation elements. The developer should specifically target only `<nav>`, `<footer>`, `<header>`, `<aside>` tags for removal and explicitly preserve `<table>` content. Using `unstructured` instead of raw BeautifulSoup would handle table extraction as a separate element type automatically. A is wrong because BeautifulSoup's `get_text()` does extract text from table cells — it does not strip table content automatically; the issue is in the developer's custom filtering code. C is wrong because BeautifulSoup is a full HTML parser that handles `<table>` tags correctly; tables are not binary image elements and do not require OCR. D is wrong because Vector Search embedding models accept any text string, including text extracted from tables; there is no special failure mode for tabular content.
**Source:** Section 2: Data Preparation – Objective 2: Filter extraneous content in source documents — docs.databricks.com (search: "Generative AI data preparation")

---

### Question 35
**Difficulty:** Advanced

A data engineer is preparing a RAG pipeline for a healthcare company. Source documents include: clinical trial reports (PDF), drug interaction databases (CSV exported to plain text), and patient intake forms (scanned paper forms as image PDFs). The engineer must select a different extraction tool for each category. What is the correct tool mapping?

A) Clinical trial PDFs → `PyPDF2`; drug interaction CSV text → `unstructured`; scanned patient forms → `pytesseract`. This mapping applies the appropriate tool to each format's specific characteristics.
B) Clinical trial PDFs → `beautifulsoup4`; drug interaction CSV text → `PyPDF2`; scanned patient forms → `unstructured`. BeautifulSoup handles all PDF types and PyPDF2 is for CSV formats.
C) Clinical trial PDFs → `pytesseract`; drug interaction CSV text → `pytesseract`; scanned patient forms → `pytesseract`. Pytesseract is the universal extraction tool for all healthcare document formats.
D) Clinical trial PDFs → `unstructured`; drug interaction CSV text → Python `csv` module or pandas `read_csv()`; scanned patient forms → `pytesseract`. Each tool is matched to the format's specific extraction requirement.

**Correct Answer:** D
**Explanation:** D is correct. The correct mapping uses the right tool for each document type: `unstructured` handles complex PDF clinical reports with mixed content (text, tables, headers); the Python `csv` module or pandas handles structured CSV plain-text data without needing an NLP library; `pytesseract` performs OCR on scanned image PDFs (patient intake forms) where no digital text layer exists. A is wrong because while `PyPDF2` can handle standard text-based PDFs, `unstructured` is superior for complex clinical PDFs with mixed content; using `unstructured` for CSV text adds unnecessary overhead when native CSV parsers are available. B is wrong because `beautifulsoup4` is an HTML parser that cannot parse PDF files; `PyPDF2` cannot parse CSV files. C is wrong because `pytesseract` is only appropriate for image/scanned documents; using it universally for digital PDFs and CSV text introduces unnecessary OCR processing and potential accuracy loss.
**Source:** Section 2: Data Preparation – Objective 3: Choose the appropriate Python package — docs.databricks.com (search: "RAG reference architecture data preparation")

---

### Question 36
**Difficulty:** Proficiency

A production RAG pipeline serves 50,000 queries per day. The Vector Search index has 2 million chunks. A data scientist runs a retrieval evaluation over a 500-query benchmark and reports `nDCG@10 = 0.61`. The engineering team lead asks: "Is this score good enough to ship, and what does nDCG@10 specifically measure that Precision@10 and Recall@10 do not?" Provide the technically complete answer.

A) `nDCG@10 = 0.61` is always sufficient for production deployment; nDCG@10 measures the same thing as Precision@10 but averages it across queries, providing a more statistically stable metric with no additional ranking information.
B) Whether 0.61 is sufficient depends on the use case baseline; nDCG@10 measures position-weighted relevance — it rewards ranking highly relevant chunks first and penalizes placing them lower — capturing rank quality that neither Precision@10 (equal weight per rank) nor Recall@10 (coverage only) measures.
C) `nDCG@10 = 0.61` is always insufficient for production; nDCG measures the fraction of queries where the first result is relevant, and 0.61 means 39% of queries have an irrelevant first result, which is unacceptable for production.
D) nDCG@10 measures the same thing as Recall@10 but normalized between 0 and 1; a score of 0.61 means 61% of all relevant chunks in the index appear somewhere in the top-10 results across all evaluated queries.

**Correct Answer:** B
**Explanation:** B is correct. nDCG (Normalized Discounted Cumulative Gain) at k measures position-weighted relevance: a highly relevant chunk at rank 1 contributes much more to the score than the same relevant chunk at rank 10. It also handles graded relevance (a chunk can be more or less relevant, not just binary). Neither Precision@10 (fraction of top-10 that are relevant — equal weight per position) nor Recall@10 (fraction of all relevant chunks found in top-10) captures the ranking quality — they don't distinguish between finding the best chunk at rank 1 vs. rank 10. Whether 0.61 is "good enough" depends on the use case, the baseline of the previous system, and the business requirements — there is no universal threshold. A is wrong because nDCG is NOT the same as averaged Precision@k — nDCG includes position discounting and handles graded relevance, providing additional ranking quality information. C is wrong because nDCG is not the fraction of queries with a relevant first result — that is Precision@1 or a variation of MRR. D is wrong because that describes a version of normalized Recall, not nDCG; nDCG measures position-weighted cumulative gain, not binary coverage of relevant chunks.
**Source:** Section 2: Data Preparation – Objective 6: Use tools and metrics to evaluate retrieval performance — docs.databricks.com (search: "MLflow evaluate for RAG")

---

### Question 37
**Difficulty:** Proficiency

A team is designing a RAG pipeline for a company's 10-year archive of engineering change orders (ECOs), each a 20–80 page PDF with structured sections (Summary, Affected Parts, Test Results, Approvals). They must choose between three chunking strategies: (A) fixed-size 512-token chunks, (B) section-aware chunking by ECO section headers, and (C) Parent-Child chunking with section headers as parent boundaries and 150-token sub-sections as children. What is the complete reasoning for selecting strategy C?

A) Strategy C is the most complex and therefore always the best choice for production RAG pipelines — complexity in the chunking layer inversely correlates with hallucination rates in the LLM output.
B) Strategy C is best because it combines section-aware structure preservation (parent boundaries align with ECO sections) with precise child-level embeddings for accurate retrieval, and full parent section delivery to the LLM for rich context — addressing all three requirements: structure, precision, and context.
C) Strategy C should be avoided because the section headers (parent boundaries) in ECOs vary across 10 years of documents, making it impossible to reliably detect consistent header patterns for parent chunking.
D) Strategy C is the best choice only if the ECOs are stored as Markdown files; for PDFs, parent-child chunking is not supported by any Databricks-compatible parsing library.

**Correct Answer:** B
**Explanation:** B is correct. For structured, long-form technical documents like ECOs, Parent-Child chunking optimally addresses the three key requirements: (1) **Structure preservation** — parent boundaries align with ECO sections (Summary, Affected Parts, etc.), keeping logically related content together at the parent level. (2) **Retrieval precision** — small 150-token child chunks produce focused, precise embeddings that match specific query terms (e.g., "test results for part #XYZ") without the semantic diffusion of large chunks. (3) **Context richness** — the LLM receives the full parent section (potentially 500–2,000 tokens) containing the matched child, providing sufficient context for complete, well-grounded answers. A is wrong because complexity alone is never a selection criterion; the choice should be based on document structure, query patterns, and performance requirements. C is wrong because even if header patterns vary across 10 years, the `unstructured` library and similar tools can detect section boundaries from formatting cues (font size, capitalization, whitespace), and variable headers can be normalized during pre-processing. D is wrong because Parent-Child chunking is a logical strategy applied to any text, regardless of source format; `unstructured` parses PDFs into sections that can serve as parent boundaries.
**Source:** Section 2: Data Preparation – Objective 7: Design retrieval systems using advanced chunking strategies — docs.databricks.com (search: "Advanced chunking strategies RAG")

---

### Question 38
**Difficulty:** Proficiency

A Vector Search reranking stage uses a cross-encoder model hosted on a Databricks Model Serving endpoint. The initial Vector Search returns 50 candidates; the reranker scores and returns top-5. A developer observes that for very short, ambiguous queries like "error fix", the reranker consistently places a generic troubleshooting document first, while for detailed queries like "SSL certificate validation error in Python 3.11 requests library", the reranker performs excellently. Why does query length/specificity affect reranker performance, and what can be done to improve short-query performance?

A) Short queries cause the cross-encoder model to time out on the Databricks Model Serving endpoint because the model requires a minimum input length to warm up its attention mechanism; padding short queries to 50 tokens fixes the timeout.
B) Cross-encoders score query-document relevance jointly — with a short, ambiguous query, there is insufficient semantic signal to distinguish between the 50 candidate documents, so the reranker defaults to ranking by document length (longer documents first). The fix is query expansion using an LLM to rewrite short queries into more specific forms before retrieval.
C) Cross-encoders perform poorly on short queries because they rely exclusively on BM25 keyword matching rather than semantic similarity; switching to a bi-encoder reranker resolves the short-query problem.
D) Short queries produce empty vector embeddings in the Vector Search stage (vectors of all zeros), which causes all 50 retrieved candidates to have identical cosine similarity scores; the reranker then has no useful input and ranks randomly.

**Correct Answer:** B
**Explanation:** B is correct. Cross-encoders jointly encode the query and each document together to produce a relevance score. With a rich, specific query ("SSL certificate validation error in Python 3.11 requests library"), the cross-encoder has abundant signal to distinguish highly relevant chunks from tangentially related ones. With a vague query ("error fix"), all 50 candidates may seem roughly equally relevant, making it hard for the cross-encoder to produce discriminative scores — resulting in near-arbitrary rankings. Query expansion (using an LLM to rewrite "error fix" into something like "common application error troubleshooting and debugging approaches") provides the cross-encoder with richer semantic signal. A is wrong because cross-encoders do not have minimum input length requirements and do not time out on short queries; the issue is semantic ambiguity, not a technical constraint. C is wrong because cross-encoders use neural attention mechanisms for semantic matching, not BM25 keyword matching; bi-encoders (not cross-encoders) are the vector-based approach. D is wrong because even a short query like "error fix" produces a meaningful (non-zero) vector embedding; embedding models do not produce all-zero vectors for valid text inputs.
**Source:** Section 2: Data Preparation – Objective 8: Explain the role of re-ranking in the information retrieval process — docs.databricks.com (search: "Databricks Vector Search reranking" and "Foundation Model APIs cross-encoders")

---

### Question 39
**Difficulty:** Proficiency

A developer prepares a chunking pipeline using `unstructured` to parse technical PDFs and classify elements as `Title`, `NarrativeText`, or `Table`. Their chunking strategy should preserve table integrity. When they implement the pipeline, they discover some tables are being split across chunks, resulting in partial table content in each chunk. What is the correct implementation fix?

A) Set `max_characters=99999` in the `unstructured` chunking configuration, which forces all elements including tables to be treated as unsplittable atomic units regardless of size.
B) Use `unstructured`'s `chunk_by_title()` function with `combine_text_under_n_chars` configured, and apply additional logic to detect `Table` elements and force them to be treated as unsplittable atomic chunks that are never split across boundaries.
C) Convert all tables to images using a PDF rendering library before running `unstructured`, then use `pytesseract` to re-extract the table text — the OCR process naturally preserves table row integrity.
D) Split the pipeline into two separate paths: one for `NarrativeText` using fixed-size chunking, and one for `Table` elements using document-aware chunking, then merge the resulting chunks back into a single DataFrame before embedding.

**Correct Answer:** B
**Explanation:** B is correct. `unstructured`'s chunking functions allow you to specify element-type-aware behavior. By treating `Table` elements as atomic/unsplittable units (configuring the chunker to never split a single `Table` element across chunk boundaries), you preserve table integrity. This can be achieved by detecting `Table` elements before chunking and either (1) skipping them through the splitter and adding them as fixed chunks, or (2) configuring `unstructured`'s chunking parameters to respect element type boundaries. A is wrong because setting an extremely large `max_characters` value prevents any splitting but may create chunks vastly exceeding the embedding model's token limit for large tables or sections, causing different problems. C is wrong because converting existing tables to images and re-running OCR introduces accuracy loss and is computationally expensive; `unstructured` already parses table structure from PDFs without needing OCR. D is wrong because splitting into two separate pipelines based on element type is unnecessarily complex; `unstructured` is designed to handle multiple element types in a single unified pipeline with appropriate configuration.
**Source:** Section 2: Data Preparation – Objective 3 & 7: Python packages and advanced chunking — docs.databricks.com (search: "RAG reference architecture data preparation" and "Advanced chunking strategies RAG")

---

### Question 40
**Difficulty:** Proficiency

A data platform team ingests legal briefs (PDF) into a RAG pipeline. After 6 months in production, they discover: (1) older briefs from 2019–2020 contain outdated legal precedents that have since been overruled, but (2) the Vector Search index shows these old chunks as frequently retrieved because they are semantically similar to modern queries. What is the most comprehensive data governance solution?

A) Delete the entire Vector Search index and rebuild it from scratch using only 2022–2025 documents, permanently excluding all pre-2021 content from the knowledge base to eliminate the stale precedent problem.
B) Add a `document_year` metadata column to the source Delta table, apply an update to mark pre-2021 documents with a `is_superseded = true` flag, and configure the RAG chain to apply a metadata filter `is_superseded = false` at query time — excluding stale chunks from retrieval while preserving them in the Delta table for audit purposes.
C) Fine-tune the embedding model on 2022–2025 legal briefs only so that pre-2021 documents produce embedding vectors that are dissimilar to modern queries, naturally reducing their retrieval frequency without requiring any metadata changes.
D) Increase the Vector Search `num_results` from 5 to 50 and add a post-retrieval LLM filtering step that reads each chunk's embedded date metadata and removes any chunk dated before 2021 before passing context to the answer LLM.

**Correct Answer:** B
**Explanation:** B is correct. This is a data governance and knowledge base lifecycle management challenge. Adding a `is_superseded` boolean flag to the source Delta table and filtering it out at query time is the correct approach because it: (1) preserves the historical data in Delta Lake for audit and compliance purposes, (2) ensures stale content never reaches the retrieval results, (3) is easily reversible (unsupersede a document by flipping the flag), and (4) works with Vector Search metadata filtering without requiring index rebuilds. A is wrong because permanently deleting data violates data retention requirements common in legal contexts, and the Vector Search index sync (CDF) would propagate the deletions to the index — but the underlying data would be lost. C is wrong because fine-tuning an embedding model to produce dissimilar vectors for specific documents is an extremely expensive and imprecise approach; embedding distance is not a reliable mechanism for enforcing business rules about document validity. D is wrong because adding an LLM filtering step for 50 retrieved chunks significantly increases latency and token cost, and relying on the LLM to filter by date is fragile and non-deterministic — metadata filtering at the Vector Search layer is more reliable and efficient.
**Source:** Section 2: Data Preparation – Objective 5: Identify needed source documents — docs.databricks.com (search: "Generative AI data preparation best practices" and "Mosaic AI Vector Search index")
