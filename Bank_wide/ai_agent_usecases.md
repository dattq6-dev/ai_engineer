# AI Agent Learning Use Cases — Fraud Dataset

**Purpose:** three candidate use cases for learning LangChain, LangGraph, RAG, deep agents, and MCP, built on the existing FC-Squad fraud dataset and analysis in this folder.

**Date:** 2026-09-09

---

## 0. What the data actually supports

| Fact | Value | Source |
|---|---|---|
| Transactions | 688,651 | `outputs/run_log.txt` |
| Customers | 8,021 | `outputs/run_log.txt` |
| Fraudsters | 299 (~3.7% of customers) | `04_brief2b_behavioural/brief2b_rules.csv` |
| Population fraud rate (user-level, GB) | 13,088 / 385,343 = 3.4% | `fin_crime_data.csv` |
| Engineered features | 46 columns; 38 usable for modeling | `outputs/run_log.txt` |
| Excluded features | 1 leaky (`KYC_CURRENT`), 3 banned (`NATIONALITY`, `BIRTH_YEAR`, `AGE`) | `outputs/run_log.txt` |
| Transaction schema | `TYPE, AMOUNT, CURRENCY, MERCHANT_COUNTRY_CLEAN, IS_OPAQUE, MC_DIRTY, IS_CRYPTO, ROUND_10, ROUND_100, AMT_ZERO, KYC, COUNTRY, AGE, IS_FRAUD` | `outputs/txn_sample_60k.csv` |

### Hard constraint: there is no timestamp column

`05_bonus_threat_score/bonus_dimensions.csv` states it directly — *"with no clock the closest honest evidence is…"* and *"Intensity — deliberately NOT called velocity: it is a count, not a rate."*

**Implication:** real-time streaming, velocity rules, and sequence models are **not honestly buildable** on this dataset. What it does support is *investigation*, *reasoning over evidence*, and *retrieval over the existing methodology corpus*. All three use cases below respect this.

### Assets available as agent inputs

- **Structured:** `customer_features.csv` (8,021 x 47), `outputs/txn_sample_60k.csv` (60k sample), `outputs/country_summary.csv`, `outputs/merchant_summary.csv`, `outputs/kyc_summary.csv`, ~40 result CSVs across stages 02–06.
- **Unstructured (RAG corpus):** `fc-squad-analysis-plan-v2.md`, `fc-squad-business-case-analysis.md`, `asumption.docx`, `hypothesis.docx`, `brief_plan.docx`, `07_deliverables/FC-Squad-Report.docx`.
- **Ground truth:** `IS_FRAUD` at customer level — every use case below can be *measured*, not just demoed.

### Baseline to beat

From `04_brief2b_behavioural/brief2b_rules.csv`:

| Rule | Flagged | TP | Precision | Recall | Lift |
|---|---|---|---|---|---|
| R1 cashout ratio > 0.8 | 1,185 | 153 | 0.129 | 0.588 | 3.47 |
| R4 single merchant country | 2,573 | 170 | 0.066 | 0.654 | 1.78 |
| R5 R1 AND R2 | 535 | 102 | 0.191 | 0.392 | 5.12 |
| **R6 R1 AND R3** | **248** | **62** | **0.250** | **0.238** | **6.72** |

Any agent that cannot beat *"flag everyone with cashout ratio > 0.8 and round-1e3 share > 60%"* is not earning its inference cost. Keep R6 as the scoreboard.

---

## Idea 1 — AML Alert Investigator (agentic triage)

**What it does.** Takes a flagged customer ID and produces an investigator-ready case file: which rules fired, how the customer compares to their peer cohort, contradicting evidence, and a recommended disposition (escalate / monitor / close) with confidence and reasoning.

**Technology mapping**

- **LangGraph — primary.** Investigation is a *cyclic* graph, not a chain:
  `triage -> gather evidence -> hypothesise -> check contradictions -> (loop if unresolved) -> write SAR-style narrative`.
  Teaches conditional edges, accumulating state, and `max_iterations` guards.
- **MCP — data access layer.** Expose the data as tools rather than hardcoding: `get_customer_features(id)`, `get_transactions(id)`, `peer_cohort_stats(country, currency)`, `run_rule(rule_id)`. This is the most transferable component: the same server later points at a real core-banking read replica.
- **RAG.** Index `asumption.docx`, `hypothesis.docx`, and the plan markdown so the agent cites *documented* assumptions (e.g. L12 no-dedupe, P7 banned features) instead of inventing policy.
- **Deep agent.** Planning plus sub-agents: a transaction analyst, a peer comparator, and a devil's advocate arguing the customer is legitimate. One scratchpad file per case.
- **LangChain.** Plumbing — LLM wrappers, Pydantic structured output for the case-file schema, retriever glue.

**Why start here.** Ground truth exists, so it is measurable on day one: run on 100 customers (stratified sample) and compare precision/recall against R6.

**Success criteria**
- Beat R6 precision (0.25) at comparable or better recall on a held-out customer set.
- Every claim in the case file traceable to a tool call or a cited document.
- Zero use of banned features (`NATIONALITY`, `BIRTH_YEAR`, `AGE`) or the leaky `KYC_CURRENT` in the *decision* path.

**Effort:** ~2–3 weeks part-time. **Difficulty:** medium. **Recommended first build.**

---

## Idea 2 — Fraud Analytics Copilot (text-to-analysis, RAG-heavy)

**What it does.** Answers natural-language questions ("which nationality cohorts have the worst D2 foreign ratio, and is it significant?") by either retrieving an existing result table or writing and running pandas/DuckDB against the raw data — returning the number *plus* the relevant caveat.

**Technology mapping**

- **RAG — primary.** Two indexes:
  1. **Semantic/schema layer** — what `OPAQUE_RATIO`, `MC_DIRTY`, `FOREIGN_RATIO_D2` actually mean.
  2. **Methodology corpus** — plans, assumptions, verification pass.
  Teaches the thing that genuinely breaks in production RAG: chunking a mixed corpus of tables and prose, and hybrid (keyword + vector) retrieval.
- **LangGraph.** A self-correcting loop — generate query -> execute -> on error or empty result, reflect and retry (cap 3). Plus a routing node: *is this a lookup of an existing result, or does it need fresh computation?*
- **MCP.** A sandboxed `duckdb_query` / `pandas_query` tool over `customer_features.csv` and `txn_sample_60k.csv`.
- **Deep agent.** For decomposable questions ("compare geographic vs behavioural signals and tell me which is more actionable") spanning several result tables.
- **LangChain.** SQL/pandas agent primitives, output parsers.

**Guardrail worth building.** `outputs/run_log.txt` warns that `txn_sample_60k` is a **random sample — must NOT be used to compute fraud rates.** Make the agent enforce this. Encoding a domain rule into a tool description plus a validation node is the single most useful lesson in this idea.

**Why.** Closest to what a bank actually asks an AI Engineer to deliver, and it sidesteps LLM arithmetic — code does the math, the model does routing and narration.

**Success criteria**
- 20-question benchmark set with known correct answers (derivable from the stage 02–06 CSVs); target >=90% exact-match on numbers.
- Refuses or corrects any fraud-rate question aimed at the 60k sample.

**Effort:** ~2 weeks part-time. **Difficulty:** medium-low to start, deep if hybrid retrieval is done properly.

---

## Idea 3 — Typology Discovery & Rule Proposal Lab (deep agent research loop)

**What it does.** An autonomous research agent hunts for new fraud typologies and proposes candidate rules; a separate adversarial agent tries to kill them.

**Technology mapping**

- **Deep agent — primary.** Long-horizon plan, a to-do file, sub-agents (Explorer -> Statistician -> Red Team -> Writer), findings written to disk across many steps.
- **LangGraph.** Orchestrates the propose/critique cycle with a human-in-the-loop `interrupt()` before any rule is accepted. Teaches checkpointing and interrupts — directly analogous to bank model-approval workflows.
- **RAG.** Over public typology literature (FATF, Wolfsberg red flags) so proposals are grounded in recognised typologies rather than pure data dredging.
- **MCP.** Statistical tooling: `chi2_test`, `information_value`, `holdout_evaluate`.
- **LangChain.** Agent scaffolding and memory.

**The feature that makes it worth building: an anti-p-hacking node.** `06_verification_pass/verify_stage2a_bh.csv` already applies Benjamini-Hochberg correction. Have the red-team agent apply BH and reject any rule that fails on a holdout split.

With only 299 fraudsters, an unsupervised agent **will** find beautiful garbage. Watching that happen, then building the guard, is the real lesson.

**Warning — existing signals are already suspicious.** `04_brief2b_behavioural/brief2b_information_value.csv` labels `CASHOUT_RATIO` (IV 1.03), `AMT_MEAN` (0.86), `ROUND_1E2_RATIO` (0.82) as *"suspiciously strong"*. An IV above ~0.5 usually indicates leakage or a labelling artefact. Any new typology must be checked against this before it is believed.

**Success criteria**
- At least one proposed rule survives BH correction *and* holdout validation with lift > R6's 6.72.
- Red-team agent successfully rejects at least one plausible-looking but non-replicating rule (log the rejection — this is the deliverable that proves the guard works).

**Effort:** ~3–4 weeks. **Difficulty:** high. **Build third.**

---

## Recommended sequence

Build **Idea 1**, but implement its data access as the **MCP server specified in Idea 2**. That one server then serves all three use cases, and Ideas 2 and 3 grow on top without rewriting the foundation. Idea 1 also provides a scoreboard from day one.

```
                 +---------------------------+
                 |  MCP server (shared)      |
                 |  get_customer_features    |
                 |  get_transactions         |
                 |  peer_cohort_stats        |
                 |  duckdb_query (sandboxed) |
                 |  run_rule / chi2 / IV     |
                 +------------+--------------+
                              |
        +---------------------+---------------------+
        |                     |                     |
   Idea 1                Idea 2                Idea 3
   Investigator          Copilot               Typology Lab
   (LangGraph loop)      (RAG + self-correct)  (deep agent + red team)
```

**Coverage check**

| Technology | Idea 1 | Idea 2 | Idea 3 |
|---|---|---|---|
| LangChain | glue / structured output | SQL agent, parsers | agent scaffolding |
| LangGraph | **core** — cyclic investigation | self-correcting retry loop | **core** — HITL interrupts |
| RAG | assumptions corpus | **core** — dual index, hybrid | external typology literature |
| Deep agent | sub-agents + scratchpad | question decomposition | **core** — long-horizon research |
| MCP | **core** — data tools | query tool + guardrail | statistical tools |

---

## Open questions to resolve before building

1. **Scope** — one runnable repo end-to-end with evaluation, or a shallower pass across all three to touch every technology quickly?
2. **Output language** — Vietnamese, English, or bilingual? The source docs are mixed, which forks the RAG embedding-model choice (multilingual vs English-only).
3. **LLM access** — which provider/model is available in the bank's environment? Affects whether tool-calling can be relied on natively or must be prompted.
4. **Holdout policy** — fix a customer-level train/holdout split *now*, before any agent sees the data, so Idea 3's validation is credible.

---

## Sources

All figures above are read from files in this folder:

- `outputs/run_log.txt` — row counts, feature counts, leaky/banned feature list, sample warning
- `customer_features.csv` — feature schema
- `outputs/txn_sample_60k.csv` — transaction schema
- `fin_crime_data.csv` — population fraud rate
- `04_brief2b_behavioural/brief2b_rules.csv` — R1–R8 baseline rule performance
- `04_brief2b_behavioural/brief2b_information_value.csv` — IV strengths
- `05_bonus_threat_score/bonus_dimensions.csv` — threat-score dimensions, no-timestamp constraint
- `06_verification_pass/` — BH correction, leakage checks, defect log
