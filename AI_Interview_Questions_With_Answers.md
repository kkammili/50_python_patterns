# Fidelity Plan Sponsor WebStation (PSW)

Fidelity Plan Sponsor WebStation (PSW) is a secure, web-based application that Fidelity Investments provides to employers ("plan sponsors") who administer 401(k) or other retirement plans through Fidelity. It gives plan administrators — a single point of access to current plan and participant information, including account balances, contribution activity, and historical data. Beyond just viewing data, PSW serves as the operational hub for day-to-day plan management: extensive reporting (including up to 150 data points across categories like participant activity, stock plan grants, and purchase enrollments), investment performance tracking, and role-based access controls that let organizations provision and manage which employees can view or act on plan data.

PSW is also where sponsors resolve operational issues directly with Fidelity through structured service requests — for example, correcting a missed or inaccurate contribution, fixing a loan repayment error, stopping`` and reissuing a distribution check, or adjusting a participant's account due to a vesting error. Each request type follows a specific template designed to capture the exact information Fidelity needs, which reduces back-and-forth and speeds resolution. PSW is used by the organization managing the retirement plan, not by individual employees contributing to it.

# Fidelity PSW Compliance & Service-Request Assistant — Interview Narrative

## Project Summary

At Fidelity, I built and deployed a RAG-based Compliance & Service-Request Assistant for Plan Sponsor WebStation (PSW), the platform employers use to administer their retirement plans. Plan admins were spending significant time each week manually locating the correct service-request template and required fields for compliance-sensitive tasks — correcting missed contributions, fixing loan repayment errors across scattered documentation and the fiduciary compliance calendar.

Because the system handled compliance-sensitive plan and participant data, using a public LLM API directly wasn't viable — it would mean sensitive data leaving Fidelity's controlled environment. So I built the pipeline on AWS Bedrock, accessed through Fidelity's own AWS account via a VPC endpoint, with Bedrock's contractual no-retention/no-training terms on inputs and outputs. That satisfied data governance requirements without data ever leaving Fidelity's network boundary, and without the operational overhead of managing our own GPU infrastructure — Bedrock just exposes the model as a managed API within our own VPC.

For generation, I used Claude (via Bedrock) — Anthropic's strong instruction-following made it reliable at sticking to "answer only from retrieved context, cite the source, don't guess," which mattered given the compliance stakes. For embeddings, I used Amazon Titan Text Embeddings V2 through Bedrock, at 1024 dimensions. Embeddings were L2-normalized at ingestion, so retrieval could run as an inner-product search in pgvector rather than the more expensive cosine-distance operator.

The corpus was chunked by service-request category — contributions, withdrawals, loans — rather than fixed-token splitting, so each retrieved chunk represented a complete, self-contained procedure instead of an arbitrary fragment. Chunks were tagged with metadata for category-filtered retrieval. The pipeline itself was built with LangGraph and FastAPI: classify the admin's question into a request category, retrieve the matching procedure filtered by that category, and generate a cited answer pointing to the specific template and required fields — so an admin asking "how do I correct a missed employer match contribution" got the exact steps and data points Fidelity needed, not a generic response.

The core design decision I'd defend is retrieval-with-citation over an ungrounded or fine-tuned model — in a compliance context, a hallucinated field or missed deadline has real operational consequences, like a late 5500 filing or a misrouted service request. Traceability to a source document was non-negotiable, and that's what shaped the entire architecture, from chunking strategy to the private-VPC deployment choice.

---

## Technical Specifics (keep consistent across all follow-ups)

| Component | Choice |
|---|---|
| **LLM** | Claude, via AWS Bedrock, accessed through Fidelity's AWS account/VPC endpoint |
| **Embeddings** | Amazon Titan Text Embeddings V2 (Bedrock), 1024 dimensions |
| **Normalization** | L2-normalized at ingestion → inner-product search in pgvector |
| **Vector store** | Amazon RDS for PostgreSQL + pgvector (inside Fidelity's VPC) |
| **Chunking** | Category-based (contributions / withdrawals / loans), not fixed-token |
| **Orchestration** | LangGraph (classify → retrieve → generate) |
| **Serving** | FastAPI backend |
| **Data governance** | Bedrock in Fidelity's own AWS VPC, no-retention/no-training terms — no data left Fidelity's environment |

---

## Anticipated Follow-Up Questions

### "What was the impact/adoption?"
- How many plan admins/organizations used it?
- What was support ticket volume before vs. after?
- Any measurable time saved per request resolution?

### "Who else was involved?"
- Solo project, or with a compliance/product team?
- Who reviewed retrieved-content accuracy before launch?

### "How did you handle hallucination risk?"
- How did you validate retrieval accuracy (eval set, human review, spot-checks)?
- What happened when the model couldn't find a confident answer — refuse/escalate?

### Embedding model choice
- Why Titan V2 over an alternative (e.g., OpenAI, Cohere)?
- Why 1024 dims — storage vs. recall tradeoff?
- Did you truncate a larger native embedding, or use native dimensionality?

### Normalization & indexing
- Why normalize at ingestion instead of query time?
- pgvector index type — IVFFlat or HNSW — and why?
- How did index choice affect recall vs. query latency at your corpus size?

### Chunking strategy
- What chunk size, and why category-based instead of fixed-token?
- Any overlap between chunks? Why or why not?
- How did you handle documents where a fix spans multiple sections (e.g., a full amendment)?

### Retrieval mechanics
- Pure vector similarity, or hybrid (BM25 + vector)?
- How many chunks (top-k) retrieved per query, and why that number?
- Did you use a reranker after initial retrieval?

### Pipeline architecture depth
- Walk through exactly how a request flows through the LangGraph nodes.
- What happens on a classification failure or low-confidence retrieval — human fallback, or answer anyway?
- Any retry/quality-check loop (similar to the resume-tailoring project's retry loop)?

### Evaluation & maintenance
- How did you evaluate retrieval quality — precision@k, human-labeled eval set, something else?
- How do you keep the corpus current as PSW procedures/templates change?
- Did you version embeddings when source documents were updated?

### "Why not Bedrock Knowledge Bases?" (AWS's managed RAG offering)
- Answer: wanted more control over category-based chunking and the LangGraph classify-then-retrieve flow than the managed offering provides — a deliberate build-vs-buy decision.

# AI Engineer Interview Question Bank — With Answers

Consolidated from five sources (listed at the end) and cut down to what an **applied** AI engineer actually gets asked, answered at "crisp enough to say out loud in an interview" length. Where a question is a design prompt rather than a fact, the answer gives the structure a strong candidate would use rather than a single right response.

---

## How this bank is organized

Cut down from 20 textbook topics to what an **applied** AI engineer actually gets asked. Classical search algorithms, knowledge representation, decision theory, classical reinforcement learning, and the machine-learning / deep-learning / natural-language-processing fundamentals chapters are all gone — you will not be asked to derive a gradient for a job where you ship retrieval pipelines. The alignment material survived, because it explains *why models behave the way they do*, which you do have to engineer around.

**Tier 1 (§1–§10)** is your day job. Every one of these hangs off the PSW project above, so each section opens with a **PSW anchor** — the sentence that turns a memorized fact into a story you already own. Answer from the anchor first, then generalize.

**Tier 2 (§11–§14)** you need the shape of, not the derivation. Compressed accordingly.

**How to use it:** don't read it front to back. Cover the answers, say yours *out loud*, and start every Tier 1 answer with "In the PSW assistant we…". The gap between "I recognize this" and "I can explain this in 45 seconds with a trade-off attached" is the whole interview. Any abbreviation you hit is expanded in the glossary immediately below.

---

## Glossary — every abbreviation in this document

Look things up here rather than memorizing them. Grouped by where they show up, not alphabetically, so related terms sit together.

**The core four**
- **LLM** — Large Language Model. The model itself (Claude, GPT, Llama).
- **RAG** — Retrieval-Augmented Generation. Fetch relevant documents first, then have the model answer from them. Your PSW project.
- **API** — Application Programming Interface. How your code calls someone else's service over the network.
- **PSW** — Plan Sponsor WebStation. Fidelity's platform for employers administering retirement plans — the subject of your project.

**Retrieval and search**
- **ANN** — Approximate Nearest Neighbour. Search that finds *almost* the closest vectors, trading a little accuracy for enormous speed.
- **HNSW** — Hierarchical Navigable Small World. The most common ANN index type: a multi-layer graph you walk downward to find neighbours. Fast, high accuracy, uses a lot of memory.
- **IVF** — Inverted File index. Splits vectors into clusters and searches only the nearest few clusters.
- **PQ** — Product Quantization. Compresses vectors into short codes to save memory. **IVF-PQ** combines both.
- **FAISS** — Facebook AI Similarity Search. An open-source library for vector search.
- **BM25** — the standard keyword-matching ranking formula used by search engines like Elasticsearch. The "lexical" half of hybrid search.
- **MTEB** — Massive Text Embedding Benchmark. The public leaderboard for comparing embedding models.
- **MIPS** — Maximum Inner Product Search. Finding the vector with the highest dot product.
- **ACL** — Access Control List. Who is allowed to see a given document.
- **OCR** — Optical Character Recognition. Turning a scanned image of text into actual text.

**Measuring quality**
- **Recall@k / Precision@k** — of the top k results you retrieved, how many of the right ones did you find (recall) and how many of what you returned was actually relevant (precision).
- **MRR** — Mean Reciprocal Rank. How high up the list the first correct result appears, averaged over all queries.
- **NDCG** — Normalized Discounted Cumulative Gain. A ranking score that rewards putting the most relevant results nearest the top.
- **NLI** — Natural Language Inference. A model that judges whether statement B is supported by passage A. Used to check whether an answer is actually backed by its cited source.
- **RAGAS** — an open-source library of standard RAG evaluation metrics.
- **BLEU / ROUGE / BERTScore** — older text-generation scores that compare output against a reference answer. Mostly historical.
- **G-Eval** — a published method for using a strong model as a grader with an explicit rubric.
- **CI** — Continuous Integration. The automated checks that run on every code change before it merges.
- **SWE-bench** — a benchmark of real GitHub issues used to score coding agents.
- **CSAT** — Customer Satisfaction score.
- **ROI** — Return On Investment. Did the feature pay for itself.

**Serving and infrastructure**
- **GPU** — Graphics Processing Unit. The hardware that runs model inference. **VRAM** is the memory on it.
- **KV cache** — Key-Value cache. Stored intermediate attention values so the model doesn't recompute the whole conversation for every new token. The main consumer of GPU memory during generation.
- **TTFT** — Time To First Token. How long the user waits before seeing anything.
- **ITL** — Inter-Token Latency. How fast tokens stream out after that.
- **QPS** — Queries Per Second.
- **SLA** — Service Level Agreement. The latency or uptime you've promised.
- **SSE** — Server-Sent Events. The simple one-way streaming protocol used to push tokens to a browser.
- **TTL** — Time To Live. How long a cached entry stays valid.
- **vLLM / TGI** — two popular open-source serving engines. TGI is Text Generation Inference.
- **AWS** — Amazon Web Services. **Bedrock** is its managed service for calling models like Claude.
- **VPC** — Virtual Private Cloud. Your own isolated network inside AWS. A **VPC endpoint** lets you reach an AWS service without traffic crossing the public internet — the crux of your governance story.
- **FSDP / ZeRO** — techniques for splitting a model across multiple GPUs during training.
- **LSP** — Language Server Protocol. What gives an editor "go to definition"; useful to a coding agent.
- **AST** — Abstract Syntax Tree. The parsed structure of source code.
- **MCP** — Model Context Protocol. An open standard for connecting models to tools and data sources.
- **LLMOps / MLOps** — the operational practice of deploying and monitoring language models / machine-learning models.

**Transformer internals**
- **FFN** — Feed-Forward Network. The per-token processing layer inside each transformer block, where much of the model's knowledge lives.
- **MoE** — Mixture of Experts. Many FFNs plus a router that activates only a few per token.
- **Q, K, V** — Query, Key, Value. The three projections of each token that attention is computed from.
- **MHA / MQA / GQA** — Multi-Head, Multi-Query, and Grouped-Query Attention. Three ways to share key/value data across attention heads; GQA is the middle ground and the modern standard because it shrinks the KV cache.
- **RoPE** — Rotary Position Embedding. How modern models encode word order.
- **NTK / YaRN** — methods for stretching RoPE so a model handles longer inputs than it was trained on.
- **BPE** — Byte-Pair Encoding. The standard algorithm for splitting text into tokens.
- **SLM / LRM** — Small Language Model / Large Reasoning Model.

**Training and fine-tuning**
- **FT** — Fine-Tuning. Further training of an existing model on your own examples.
- **PEFT** — Parameter-Efficient Fine-Tuning. Training a tiny number of added parameters instead of all of them.
- **LoRA / QLoRA** — Low-Rank Adaptation. The dominant PEFT method; QLoRA is the memory-efficient quantized version.
- **GPTQ / AWQ** — two algorithms for quantizing (shrinking) a model with minimal quality loss.
- **RL** — Reinforcement Learning. Training by reward rather than by labelled examples.
- **RLHF** — Reinforcement Learning from Human Feedback. How models are taught to be helpful and safe using human preference comparisons.
- **RLAIF** — the same thing with an AI generating the preferences instead of people.
- **PPO / DPO / GRPO** — three optimization algorithms used for that preference training. DPO (Direct Preference Optimization) is the simple modern default.
- **KL penalty** — Kullback-Leibler. A mathematical leash keeping the tuned model from drifting too far from the original.
- **MSE** — Mean Squared Error. A standard regression loss.

**Governance and safety**
- **PII** — Personally Identifiable Information. Names, account numbers, anything identifying a person.
- **GDPR / CCPA** — the European and Californian data-privacy laws.
- **DPIA** — Data Protection Impact Assessment. The written risk analysis GDPR requires for high-risk processing.
- **EU AI Act** — the European Union's risk-tiered AI regulation.
- **NIST** — the US National Institute of Standards and Technology; publishes the AI Risk Management Framework.
- **OECD** — Organisation for Economic Co-operation and Development; publishes a set of AI principles.
- **LIME / SHAP** — two methods for explaining why a model made a particular prediction.
- **DP-SGD** — Differentially Private Stochastic Gradient Descent. Training with mathematically bounded privacy leakage.

**Interview shorthand**
- **STAR** — Situation, Task, Action, Result. The structure for answering behavioural questions.
- **PM** — Product Manager.
- **UX** — User Experience.

---

# TIER 1 — Own these

## 1. Retrieval-Augmented Generation

> **PSW anchor:** You built a four-stage pipeline — chunk PSW procedure docs by service-request category, embed with Titan V2, retrieve filtered by the classified category, generate with mandatory citations. Every RAG question below is a question about a decision you already made.

**Explain how RAG works end-to-end.**
Four stages. Ingest: chunk source documents and embed each chunk into a vector store with metadata. Retrieve: embed the query and run a similarity search for the top-k chunks (usually hybrid + rerank). Augment: insert those chunks into the prompt with an instruction to answer only from the provided context. Generate: produce the answer with citations. The reason to use it over fine-tuning is freshness — you update knowledge by re-indexing, not retraining. The thing interviewers listen for: retrieval and generation fail independently, so you evaluate and debug them separately.
*PSW:* classify → retrieve (category-filtered) → generate-with-citation, as three LangGraph nodes.

**Compare RAG, fine-tuning, and prompting — how do you decide?**
Prompting changes behavior with zero infrastructure; try it first. RAG gives the model *facts* it doesn't have, keeps them current, and provides citations — use it when the answer depends on your proprietary, changing, or auditable knowledge. Fine-tuning teaches *behavior*, style, format adherence, or a domain's vocabulary, and can cut cost by letting a small model do a narrow job — use it when the issue isn't missing facts but wrong manner. They compose: fine-tune for form, retrieve for content.
*PSW:* the one-liner you should have ready — "in a compliance context a hallucinated field or missed deadline has real operational consequences, so traceability to a source document was non-negotiable. A fine-tuned model can't cite."

**What are chunking strategies, and how do you choose a chunk size?**
Fixed-size (with overlap) is simple and predictable but slices through semantic boundaries. Recursive character splitting respects paragraph/sentence hierarchy and is the sensible default. Semantic chunking splits where embedding similarity drops, producing coherent units at higher preprocessing cost. Document-structure-aware chunking (by heading, section, table, or code function) is usually best when the format allows. Choose size empirically against a retrieval eval set: too small loses context and forces multi-hop; too large dilutes the embedding and wastes context budget. Roughly 200–500 tokens with 10–20% overlap is a reasonable starting point, then tune.
*PSW:* you chose document-structure-aware — category-based (contributions / withdrawals / loans) — so a retrieved chunk is a *complete self-contained procedure*, not an arbitrary fragment. That's the strongest version of this answer, and it's yours. Be ready for "what about a fix that spans sections?"

**Which vector database would you pick, and why?**
Match to constraints, and say why out loud. pgvector if the data already lives in Postgres and scale is moderate — one fewer system, transactional consistency, easy metadata filtering. Chroma or FAISS for prototypes and embedded use. Qdrant or Weaviate for self-hosted production with good hybrid search and filtering. Pinecone or a managed service when you'd rather not operate it. OpenSearch/Elasticsearch when you already run it and need strong lexical search alongside vectors. The deciding factors are scale, filtering and multi-tenancy needs, hybrid search quality, update/delete patterns, and operational appetite — not benchmark QPS.
*PSW:* RDS Postgres with the pgvector extension, because the corpus was moderate, you needed metadata filtering by category, and Postgres was already an approved, backed-up, in-VPC service — one fewer system to get through security review. Be ready for "why not Chroma?": Chroma is the prototype tier (you used it locally); the production argument is governance approval, relational metadata filtering composed into the same query, transactional re-ingestion so retrieval never sees a half-updated procedure, and mature backup/DR. The honest concession: at much larger scale or with a hard hybrid-search requirement, the real alternative was Qdrant, not Chroma.

**What is hybrid search and why does it beat pure vector search?**
Hybrid runs lexical retrieval — keyword matching, usually the BM25 ranking formula — alongside dense vector retrieval and fuses the results, typically with Reciprocal Rank Fusion (interleave the two ranked lists so items ranked highly by either one rise to the top). Dense retrieval captures paraphrase and semantic similarity but reliably fails on exact identifiers, error codes, product SKUs, rare proper nouns, and domain jargon it never saw in training; lexical search nails exactly those. Together they cover each other's blind spots, which is why hybrid + rerank is the default production configuration.
*PSW:* highly relevant — form numbers and plan codes ("5500", "402(g)") are exactly what dense retrieval fumbles. If you didn't run hybrid, say so and say why (category pre-filter already narrowed the candidate set), rather than pretending.

**What is re-ranking and how does it help?**
A reranker is a cross-encoder that scores each (query, chunk) pair jointly, rather than comparing two independently computed vectors — far more accurate but far too slow to run over the whole corpus. So you use the vector/hybrid stage as a cheap high-recall filter (retrieve top 50–100) and the reranker as an expensive high-precision filter (keep top 3–5). This is usually the single highest-leverage improvement to a mediocre RAG system, and it also lets you shrink the context you pass to the LLM.

**How do you evaluate a RAG system?**
Evaluate the two halves separately. Retrieval: recall@k and precision@k (did the right chunk appear in the top k, and how much of what you returned was relevant), plus ranking scores like MRR and NDCG, against a labeled query-to-chunk set, plus context relevance. Generation: faithfulness/groundedness (is every claim supported by the retrieved context?), answer relevance, and citation correctness. The RAG triad (context relevance, faithfulness, answer relevance — the RAGAS framing) is the standard vocabulary. Add end-to-end task accuracy on a golden set, and online signals like thumbs-down rate and escalation rate. The diagnostic value is in the split: bad retrieval and bad generation need completely different fixes.
*PSW:* this is the question you're most likely to get caught on. Have a real answer about your eval set — how many labeled admin questions, who reviewed them, what precision@k you hit.

**How do you implement citations and source attribution?**
Attach stable chunk IDs and metadata (document, section, URL, version, date) to everything you retrieve, and require the model to emit those IDs inline with each claim via a structured output schema. Then *verify* post-hoc: check that each cited ID was actually in context and, for high-stakes use, run an entailment check — a model that judges whether the claim is actually supported by the passage — or an LLM-as-judge check that the claim is supported by the cited chunk. Render citations as deep links so users can audit — which is both a trust feature and your best hallucination-detection signal in production.
*PSW:* citations point to the specific service-request template and its required fields. That's the whole product.

**How do you keep a RAG knowledge base fresh, versioned, and non-contradictory?**
Ingest incrementally with content hashing so only changed documents are re-embedded, and use deterministic chunk IDs so updates replace rather than duplicate. Carry `effective_date`, `version`, and `status` metadata, filter to current documents by default, and hard-delete or tombstone superseded content instead of leaving both versions retrievable. For contradictions: prefer recency and source authority via metadata-weighted ranking, and when conflicting sources both surface, have the model surface the conflict with both citations rather than silently picking one — in regulated domains that's the required behavior anyway.
*PSW:* PSW templates and the fiduciary compliance calendar change. "How do you keep the corpus current?" is a near-certain follow-up.

**How do you implement per-user access control on retrieved documents?**
Enforce at retrieval time with metadata pre-filtering — attach ACLs/tenant IDs to each chunk and filter *before* similarity search, never post-filter (post-filtering both leaks via ranking side channels and silently returns too few results). Derive permissions from the caller's verified identity, not from anything in the prompt. For strict isolation, use per-tenant collections or namespaces. And re-check permissions at serve time rather than trusting a stale index, since document permissions change more often than documents do.
*PSW:* PSW itself is role-based multi-tenant — plan sponsors must never see each other's data. Same mechanism as your category filter, different stakes.

**How would you debug a RAG system that hallucinates despite correct retrieval?**
First confirm the premise by logging the exact context passed to the model — "correct retrieval" is often wrong, with the right chunk ranked 8th and truncated out. If the context genuinely contains the answer: check for lost-in-the-middle positioning, tighten the prompt to instruct answering *only* from context and to say "I don't know" when unsupported, add few-shot examples of correct abstention, require citations (which sharply reduces unsupported claims), and consider a smaller, more focused context — more chunks often means more distraction. Then add a verification pass (an entailment model or a judge model checking groundedness) that flags or blocks unsupported claims before they ship, and measure the change on your faithfulness eval rather than eyeballing it.

**How do you handle multi-hop questions?**
Standard top-k retrieval fails because no single chunk contains the answer. Options: query decomposition (break the question into sub-questions, retrieve for each, then synthesize), iterative/agentic retrieval (retrieve, reason about what's still missing, retrieve again — the ReAct loop applied to search), GraphRAG for relationship traversal, and increasing k plus a strong reranker. Also flag it in evaluation, because a single-hop eval set will hide this failure entirely.

**What is query transformation (HyDE, decomposition, step-back)?**
Real user queries are short, vague, and lexically unlike the documents that answer them. HyDE has the LLM write a *hypothetical answer* and embeds that instead of the question, since a fake answer lives closer to real answers in embedding space. Query decomposition splits a compound question into retrievable parts. Step-back prompting asks a more general question first to retrieve broader context. Also useful: multi-query expansion (generate several paraphrases, retrieve for each, fuse) and conversational query rewriting to resolve pronouns from chat history.

**How do you migrate embeddings when the model changes, without downtime?**
Never overwrite in place. Build the new index alongside the old one (dual-write for new content, backfill the history in batches), because vectors from different models are not comparable and a partially migrated index silently returns garbage. Then shadow-evaluate the new index against a golden retrieval set, roll traffic over gradually behind a flag with both indexes live, monitor retrieval metrics, and keep the old index until you're confident. Budget for the re-embedding cost up front — it's the reason to think hard about the embedding model choice on day one.

**How do you scale RAG retrieval to millions or billions of documents?**
Use an approximate-nearest-neighbour index (HNSW — a navigable graph index — when latency matters, IVF-PQ — clustering plus compression — when memory does) rather than exact search, shard by tenant or domain so each query searches a fraction of the corpus, and compress vectors with product or binary quantization (binary quantization plus a rescoring pass over the top candidates gives ~30x memory savings with small recall loss). Add metadata pre-filtering to cut the candidate set, cache hot queries semantically, and keep the expensive reranker on a small candidate list. Route queries to the right shard/collection with a cheap classifier rather than fanning out to all of them.

**How do you handle tables and SQL databases in a RAG pipeline?**
Don't embed tables as prose. For structured databases, use text-to-SQL: retrieve the relevant schema (embed table/column descriptions), generate a read-only query against a restricted view, execute it, and let the LLM narrate the result set — with query validation and row limits. For tables inside documents, extract them with a layout-aware parser, serialize each row into a self-contained sentence or keep the table intact with a generated natural-language summary that gets embedded as the retrieval handle. Hybrid routing between the two paths, chosen by a classifier, is the usual production shape.

**What are Self-RAG and GraphRAG, and when would you reach for them?**
Self-RAG trains the model to emit control tokens deciding *whether* retrieval is needed, then to critique retrieved passages and its own output for support — the research-grade version of what production approximates with a cheap router in front of retrieval. GraphRAG extracts entities and relationships into a knowledge graph and pre-summarizes communities, so retrieval can traverse relationships and answer corpus-level questions ("what are the themes across all incident reports?") that top-k similarity structurally cannot. Both cost real complexity; reach for them only when standard RAG demonstrably fails.

---

## 2. Embeddings & Vector Search

> **PSW anchor:** Titan Text Embeddings V2 at 1024 dimensions, L2-normalized at ingestion so retrieval runs as an inner-product search in pgvector instead of the more expensive cosine operator. That one sentence answers four of the questions below.

**What is an embedding, and what does semantic similarity mean?**
An embedding maps text (or an image, or audio) to a dense vector such that semantically related inputs land near each other geometrically. "Cancel my plan" and "how do I unsubscribe" share almost no words but sit close in embedding space — that's the whole point, and it's why vector retrieval finds paraphrases that keyword search misses. Modern text embeddings come from encoder models trained with contrastive objectives on paired data.

**Compare cosine similarity, dot product, and Euclidean distance.**
Cosine measures the angle only, ignoring magnitude — the default for text, since document length shouldn't dominate similarity. Dot product accounts for both angle and magnitude, so it can favor "larger" vectors; some models (and MIPS-optimized indexes) are trained for it specifically. Euclidean distance measures straight-line distance and is common for image/spatial embeddings. Key practical point: **on L2-normalized vectors, cosine, dot product, and Euclidean rank identically** — so use whatever metric your embedding model was trained with, and normalize consistently.
*PSW:* this is exactly why you normalize at ingestion. You get cosine's semantics at inner-product cost, computed once at write time instead of on every query. Say it in that order and the follow-up ("why not normalize at query time?") answers itself.

**How does approximate nearest-neighbour search work, and why not exact search?**
Exact k-NN is O(n) per query, which is fine for thousands of vectors and hopeless for hundreds of millions. Approximate nearest-neighbour search trades a small amount of recall for orders-of-magnitude speed: HNSW builds a navigable multi-layer graph and greedily descends it (fast, high recall, memory-hungry); IVF partitions the space into clusters and searches only the nearest few (tunable via nprobe); PQ compresses vectors into subquantized codes (huge memory savings, some accuracy loss). Real systems combine them (IVF-PQ, HNSW+PQ) and tune the recall/latency knob against a labeled set.
*PSW:* know which pgvector index you used — HNSW or IVFFlat — and the recall/latency reason. "At our corpus size exact search was fine" is a legitimate answer if it's true; say the size.

**How do you choose and benchmark an embedding model?**
Start from MTEB — the public embedding-model leaderboard — as a shortlist, then benchmark on *your* data with your own labeled query-to-document pairs — public leaderboards routinely mispredict domain performance. Weigh dimensionality (cost and memory), max sequence length (does it fit your chunks?), multilingual coverage, licensing and self-host vs. API, and inference cost at your ingestion volume. Measure recall@k and NDCG on your set, and remember that switching later means re-embedding everything.
*PSW:* Titan V2 because it was available *inside Bedrock*, i.e. inside the VPC boundary — governance, not leaderboard rank, was the binding constraint. That's a strong answer: it names a real constraint instead of a benchmark. Be ready for "why 1024 dims?" (storage/recall trade-off; Titan V2 supports 1024/512/256).

**What is embedding drift and how do you handle it?**
Two senses. Model drift: you change the embedding model and old vectors are no longer comparable — handled by full re-indexing with dual indexes, never a partial swap. Data drift: your corpus or query distribution moves away from what the model handles well (new jargon, new product names), degrading retrieval silently. Monitor retrieval quality on a fixed golden set continuously, alert on score distribution shifts, and periodically refresh the golden set to reflect current traffic.

**What's the role of metadata filtering?**
Metadata (tenant, date, document type, permissions, language, version) turns a fuzzy semantic search into a scoped one, which improves precision, enforces access control, and lets you retire stale content without deleting it. Prefer pre-filtering (constrain the candidate set before or during ANN traversal) over post-filtering, which can return fewer results than requested and leak information via ranking. Design the metadata schema before ingesting — retrofitting it means re-indexing.
*PSW:* your category tags are this. The classifier node picks the category, the filter enforces it, and retrieval never has to distinguish a loan procedure from a contribution procedure by vector distance alone.

**How do you reduce vector-database memory and storage cost?**
Reduce dimensionality (Matryoshka-style embeddings let you truncate to 256–512 dims with modest loss), quantize vectors (scalar/int8 for ~4x, product quantization for more, binary quantization for ~32x with a rescoring pass to recover accuracy), and offload cold partitions to disk-based indexes while keeping hot ones in RAM. Also prune the corpus: deduplicate near-identical chunks and drop boilerplate. Always measure recall before and after — memory savings that quietly cost you 10 points of recall are not savings.

**What are multi-modal embeddings?**
Models like CLIP train image and text encoders jointly with a contrastive objective so that matching image-text pairs land close in a *shared* space. That enables cross-modal retrieval — search images with text, find captions for images — with no OCR or tagging step. In multimodal RAG they let you index figures, screenshots, and slides in the same store as text.

---

## 3. Prompt Engineering

> **PSW anchor:** "Answer only from retrieved context, cite the source, don't guess." You picked Claude specifically because its instruction-following made that constraint stick under compliance stakes. Every prompting question is a variation on how you made that hold.

**What is prompt engineering and why does it matter in production?**
It's the practice of structuring input — instructions, context, examples, output format, constraints — to reliably get the behavior you want from a fixed model. It matters because it's the cheapest, fastest lever available: no training run, deploys in seconds, and often closes most of the gap to fine-tuning. In production it stops being ad-hoc wording and becomes versioned, tested, and evaluated artifacts.

**How do you design a robust system prompt?**
State the role and scope, the rules and refusal boundaries, the output format, and the tone — in that priority order, with the highest-stakes constraints at the top **and repeated at the very end** (models weight the edges of context most). Include a few negative examples of what *not* to do, define explicit behavior for out-of-scope and ambiguous inputs rather than leaving it to chance, and separate untrusted user content from instructions with clear delimiters. Then version it and test it against an adversarial suite, because a system prompt is code.
*PSW:* your grounding instruction sat at both edges, with retrieved chunks delimited in between. If you also defined explicit "I couldn't find a procedure for that — here's how to open a manual service request" behavior, lead with it; abstention design is what separates a compliance-grade prompt from a demo.

**Compare zero-shot, one-shot, and few-shot prompting.**
Zero-shot gives instructions only — cheapest, and increasingly sufficient for strong instruction-tuned models. One-shot adds a single worked example; few-shot adds several, which mainly teaches *format and edge-case handling* rather than new knowledge. Use few-shot when output structure matters, the task is unusual, or class boundaries are subtle; be aware examples consume context, add latency and cost, and can bias the model toward their surface patterns.

**What is chain-of-thought prompting, and when does it help?**
CoT asks the model to produce intermediate reasoning steps before the final answer, which allocates more computation to the problem and makes errors visible. It helps on multi-step arithmetic, logic, and planning; it does little or nothing for retrieval-style factual lookup or classification, where it can even hurt by rationalizing a wrong answer. If CoT isn't improving accuracy, the usual causes are that the bottleneck is knowledge rather than reasoning, the reasoning isn't actually being conditioned on (fix with self-consistency or verification), or you should be using a reasoning-trained model instead.
*PSW-relevant:* worth saying that you *didn't* need CoT for retrieval-grounded lookup — knowing when not to reach for a technique scores well.

**Explain self-consistency, tree-of-thought, and ReAct.**
Self-consistency samples multiple independent chains at nonzero temperature and takes the majority answer — wrong reasoning paths disagree, correct ones converge; big accuracy gains for linear cost. Tree-of-thought branches into multiple partial reasoning states, scores them, and searches the tree — powerful for puzzles, rarely survives a production latency budget. ReAct interleaves Thought → Action → Observation, grounding each reasoning step in real tool output, which substantially reduces hallucination versus pure CoT and produces a legible debugging trace. ReAct is the foundational agent loop most frameworks implement.

**How do you get reliable structured output?**
Best to worst: constrained decoding / grammar or JSON-schema-enforced generation (the provider guarantees valid syntax), then native structured-output or function-calling APIs, then a schema in the prompt plus few-shot examples. Regardless of method, validate the parse against your schema on receipt and have a repair path — a retry with the validation error appended usually fixes it in one shot. Also prefer flat, shallow schemas with explicit enums; deeply nested optional structures are where models break.
*PSW:* your classification node is a structured-output problem — a closed enum of request categories, validated before it reaches the retriever.

**What is prompt injection and how do you defend?**
Prompt injection is untrusted content overriding your instructions. Direct injection comes from the user ("ignore previous instructions"); indirect injection is far nastier — malicious instructions hidden in a retrieved document, web page, email, or code comment that the model reads as part of its context. There is no single fix; you layer: treat all retrieved and tool-returned content as data with clear delimiting, never grant an agent authority based on text it read, keep tool permissions least-privilege with human approval on irreversible actions, run input/output classifiers, and design so that a successful injection still can't do real damage.
*PSW:* the honest framing is that your corpus was internal and curated, so indirect injection risk was low — but the moment a sponsor-uploaded document enters the index, it isn't. Naming that unprompted is a strong move.

**What is jailbreaking?**
Attempts to get a model to violate its safety training — via roleplay/persona framing, hypothetical wrappers, incremental escalation across turns, encoding or obfuscation, low-resource languages, or many-shot conditioning. Defenses are layered too: alignment training, system-prompt reinforcement, input and output classifiers, per-user rate limiting and abuse monitoring, and red-teaming before launch. Assume it's an arms race, not a solved problem — the design goal is bounding the blast radius.

**What does temperature control? Compare top-k and top-p.**
Temperature divides the logits before softmax: low T sharpens toward the argmax (deterministic, repetitive), high T flattens (diverse, more error-prone). Top-k truncates to the k highest-probability tokens — simple, but badly calibrated when the distribution is very peaked or very flat. Top-p (nucleus) keeps the smallest set whose cumulative probability exceeds p, so the candidate pool adapts to the model's confidence at each step. Worth saying out loud: **temperature 0 gives you consistency, not correctness.**

**How do you make outputs more deterministic?**
Temperature 0 (or top-k=1), fixed seed where supported, constrained/grammar-based decoding for structure, and a pinned model version so the provider can't swap the model under you. Then cache: identical input → cached output is the only true determinism. Be honest with stakeholders that even at temperature 0, batching, hardware, and floating-point nondeterminism mean bitwise-identical output isn't guaranteed — what you can promise is *semantic* stability plus a snapshot test suite.

**How do you design and version a production prompt template?**
Treat it like source: parameterized template with typed variables, stored in version control (not pasted in application code), with an ID and semantic version emitted in every log line so you can attribute a bad output to a specific prompt version. Gate changes behind evals and A/B tests, keep the previous version hot for instant rollback, and separate the immutable system portion from the per-request variable portion.

**How do you evaluate and iterate on prompt quality, and catch regressions?**
Build a golden dataset of representative and adversarial inputs with expected properties *before* you start tuning — otherwise you're optimizing on vibes. Score with a mix of deterministic checks (schema validity, required citations, refusal on out-of-scope), LLM-as-judge with a rubric validated against human labels, and a small human-reviewed slice. Run that suite in CI on every prompt or model change, track per-category scores rather than one average (that's how you catch a regression on a small critical slice), and pair offline evals with online metrics.

**How do you optimize prompts for cost and latency?**
Cut the prompt to what actually changes behavior (ablate instructions and measure), move stable content to the front so provider prefix caching can hit it, retrieve tighter top-k instead of stuffing context, and cap output length explicitly. Then route: send easy traffic to a small model and reserve the frontier model for hard cases, and add semantic caching for repeated queries. Measure the whole thing in dollars per thousand requests, not tokens — that's the number a manager cares about.

**Prompt engineering vs. prompt tuning?**
Prompt engineering writes natural-language text; nothing about the model changes and you iterate in seconds. Prompt tuning (soft prompts / prefix tuning) learns continuous embedding vectors prepended to the input via gradient descent with base weights frozen — a PEFT method, needing training data and model access, producing prompts humans can't read or edit.

**How would you stop a system prompt containing proprietary logic from being leaked?**
Accept that anything in the context can be extracted, and design accordingly: keep genuinely sensitive business logic out of the prompt and behind a tool/API call the model invokes but can't read. Beyond that, add an output filter that blocks responses resembling the system prompt, instruct refusal on meta-questions about instructions, and monitor for extraction patterns. The real answer in an interview is "I'd treat the system prompt as public and move the secret out of it."

---

## 4. Agents & Agentic Systems

> **PSW anchor:** LangGraph classify → retrieve → generate is a *pipeline*, not an agent — the control flow is yours, not the model's. Saying that distinction out loud, unprompted, scores better than claiming you built an agent. Then: "here's what would have had to change to make it genuinely agentic, and why it wasn't worth it."

**What is an AI agent, and how is it different from a single LLM call?**
An agent uses an LLM in a loop with tools, memory, and a goal: it decides what to do next based on the results of what it just did, rather than emitting one response to one prompt. The defining property is that the *model* controls the control flow — how many steps, which tools, when to stop — instead of a developer-written pipeline. That's also what makes agents powerful and dangerous: nondeterministic step counts mean nondeterministic cost, latency, and blast radius.

**Explain ReAct and Plan-and-Execute.**
ReAct interleaves reasoning and action step by step: Thought → Action → Observation → Thought, adapting after every tool result. It's flexible and self-correcting, but it can wander, and each step is a fresh LLM call. Plan-and-Execute generates the full plan up front with a strong model and then executes steps (often with a cheaper model), which is more predictable, cheaper, more parallelizable, and easier to audit or approve — at the cost of adapting poorly when reality diverges from the plan. Hybrid replanning is what most production systems land on.

**What is tool use / function calling?**
The model is given a schema of available functions (name, description, typed parameters) and, instead of answering, emits a structured call; your code executes it and returns the result into the conversation. This is what connects an LLM to the world and turns a text generator into something that can act. Reliability depends far more on the quality of tool descriptions and parameter schemas than on the model.

**Compare single-agent and multi-agent systems.**
A single agent with many tools is simpler, cheaper, easier to debug, and correct for most problems — start there. Multi-agent designs (supervisor/worker, or peer specialists) help when subtasks need genuinely different tools, prompts, or models, when you want parallelism across independent subtasks, or when context windows would otherwise overflow. The costs are real: inter-agent communication is lossy, token consumption multiplies, failures cascade, and debugging becomes distributed-systems debugging. Justify the extra agents or don't add them.

**What is the Model Context Protocol?**
MCP is an open standard for connecting models to tools and data sources — an MCP server exposes tools, resources, and prompts over a defined protocol, and any MCP-compatible client can use them. It replaces the N×M problem of bespoke integrations per model per tool with a single interface, so a connector written once works across clients. Practically, tool integrations become reusable infrastructure rather than application code.

**What types of agent memory exist, and how do you keep context from bloating?**
Working/short-term memory is the current conversation in context. Long-term semantic memory is facts about the user or domain, stored externally (usually a vector store) and retrieved on demand. Episodic memory is records of past interactions and outcomes. Procedural memory is learned skills or instructions. Manage the budget with a sliding window over recent turns, running summarization of older turns, retrieval of only relevant long-term memories, and explicit eviction policies. The rule of thumb: keep the working set small and retrieve the rest — a bloated context is both expensive and *less* accurate.

**What is the agent loop and how does it know when to stop?**
Observe state → LLM decides next action → execute tool → append result → repeat. Termination should be multi-layered rather than trusting the model: an explicit "final answer"/done tool, a hard max-iteration cap, a token and dollar budget per task, a wall-clock timeout, and a no-progress detector (repeated identical actions or unchanging state). Always define what happens on each termination path — a partial result with an explanation beats a silent stall.

**How do you detect and break an agent stuck in an infinite loop?**
Detect by hashing (action, arguments) tuples and flagging repeats, by watching for unchanged observations across steps, and by step/cost counters. Break it by escalating: inject a message naming the repetition and asking for a different approach, then force a different tool or a replanning step, then terminate with a partial answer and hand off to a human. Prevention matters more — keep a scratchpad of what's been tried in context, make tool errors informative rather than generic, and cap iterations.

**How do you fix an agent that picks the wrong tool, or the right tool with wrong parameters?**
Tool selection: rewrite descriptions to say when *not* to use each tool as well as when to, eliminate overlapping tools (most wrong-tool errors are actually ambiguous tool design), cut the tool list per task via retrieval over tools, and add few-shot examples of correct selection. Parameter extraction: tighten JSON schemas with enums, formats, and required fields; validate before executing and return a specific error the model can act on; add examples of correct calls. Build an eval set of tool-selection cases so you can measure the fix instead of guessing.

**How do you control token and cost consumption in long-running agents?**
Set an explicit budget per task and track spend as a first-class metric. Levers: compact/summarize history instead of carrying full transcripts, return trimmed tool outputs (a 50k-token API response should be filtered before it enters context), route simple steps to a cheaper model, cache prefixes and semantically similar calls, prune the tool list per task, and parallelize independent subtasks. Then alert on cost-per-task percentiles, since the tail is where budget disasters live.

**What guardrails prevent an agent from taking irreversible destructive actions?**
Design so the dangerous action isn't reachable by the model alone: least-privilege credentials scoped per agent, read-only by default, and separate write tools requiring explicit human approval. Add soft-delete and reversibility, dry-run/preview modes showing the diff before applying, blast-radius limits (row caps, rate limits), and sandboxed execution with no production network access. And critically — **never let authority come from text the agent read**, since retrieved content is an injection vector.
*PSW:* your assistant was read-and-advise, not act — it told the admin which template and fields to use rather than filing the service request itself. That's a deliberate blast-radius decision in a compliance system, so say it as one.

**What is the human-in-the-loop pattern and when is it required?**
The agent proposes and a human approves before the consequential step executes. Required when actions are irreversible, financially or legally material, above a confidence or dollar threshold, or when a regulation requires human accountability. Design it as a first-class state (durable pause, clear diff shown to the reviewer, timeout behavior, audit log of who approved what) — bolting it on later is much harder.

**Code-generating agents vs. tool-calling agents?**
Tool-calling agents pick from a fixed set of predefined functions — predictable, easy to permission and audit, but limited to what you anticipated and inefficient for multi-step composition. Code-generating agents write and execute code, so they can compose arbitrary logic, loop, and process data in one step — far more expressive and often fewer tokens, but they need a hardened sandbox and are much harder to constrain. Common production shape: tool-calling for sensitive actions, sandboxed code execution for data manipulation.

**Design an agentic customer-support system with escalation.**
Scope: input is a user message plus account context; output is a resolution, an action taken, or a handoff — with a target containment rate and CSAT floor. Architecture: intent classification/routing → retrieval over help center and policy docs → agent with scoped tools (order lookup, refund within limits, subscription change) → response with citations. Guardrails are the substance: hard policy limits encoded as code not prompt (refunds above $X never auto-execute), out-of-scope refusal, output validation, and escalation triggers — low confidence, detected frustration or a vulnerable-user signal, repeated failed attempts, explicit human request, or any high-value action. Handoff must carry full context. Evaluate containment rate, resolution accuracy, escalation precision, and cost per conversation; log every action for audit.
*PSW:* this is structurally your system with write actions added. Answer it as "we built the read-only version of exactly this, and here's what I'd add."

**Design an insurance-claims agent using RAG while controlling token cost.**
Scope first: input is a claim plus supporting documents, output is approve / deny / escalate with a written reason and citations. Pipeline: index policy documents and claim history; per claim, retrieve the governing policy clauses; pass claim plus clauses to the model with a structured-output schema. Three things this is really testing. Guardrails: the model proposes, but anything above a confidence or dollar threshold routes to a human, because a wrong auto-approval is expensive and a wrong denial is a regulatory problem. Cost control: cache embeddings, retrieve a tight top-k rather than the whole policy, route simple claims to a small model, cap tokens per call, state the token budget per claim as an explicit SLA. Evaluation: measure retrieval (did we surface the right clause?) and decision accuracy separately against an audited set, and log every decision with citations so it can be appealed. Treating cost and guardrails as design constraints rather than afterthoughts is the strong move.

---

## 5. LLM & Transformer Fundamentals

> **PSW anchor:** You don't need this to build PSW, but you need it the moment an interviewer asks "why was the first token slow?" or "why did long contexts degrade?" Learn the ones with an operational consequence — marked ★ — and treat the rest as recognition-level.

**★ What is a context window, why is it limited, and what is "lost in the middle"?**
The context window is the maximum number of tokens the model can attend over — its working memory. It's limited because attention is O(n²) in compute and the KV cache grows linearly in memory with sequence length, and because models generalize poorly beyond their trained positional range. "Lost in the middle" is the empirical finding that models attend most reliably to the beginning and end of long contexts and degrade on material buried in the middle — so put critical instructions and the most relevant retrieved chunks at the edges, and rerank hard rather than stuffing.
*PSW:* the direct justification for tight top-k and category filtering over dumping the corpus in.

**★ Why is the first token slower (prefill vs. decode)?**
Prefill processes the entire prompt in one parallel pass to build the KV cache — compute-bound, cost grows with prompt length, and it *is* your time-to-first-token (TTFT). Decode then generates one token at a time, each step reading the whole KV cache and model weights; it's memory-bandwidth-bound and roughly constant per token. That's why time-to-first-token and inter-token latency are separate metrics with separate fixes: prefix caching and shorter prompts help TTFT; batching, quantization, and speculative decoding help decode.

**★ What is the KV cache, and what is Paged Attention?**
During autoregressive generation, keys and values for all previous tokens would be recomputed every step unless cached; the KV cache stores them so each new token costs O(n) attention instead of O(n²) recomputation. The problem is memory: the cache grows with sequence length × batch × layers × heads, and naive contiguous allocation wastes most of it to fragmentation and over-reservation. Paged Attention (introduced by the vLLM serving engine) borrows operating-system virtual-memory ideas — fixed-size non-contiguous blocks with a lookup table — which nearly eliminates waste and enables prefix sharing across requests.

**★ What is quantization, and what's the trade-off?**
Quantization stores weights (and sometimes activations) at lower precision — BF16/FP16 for training, INT8/INT4/FP8 for inference — shrinking memory and increasing throughput since inference is memory-bandwidth-bound. Post-training quantization is fast but lossier; quantization-aware training preserves more quality at higher cost; GPTQ and AWQ selectively protect salient weights. Degradation shows up unevenly, hitting long-tail knowledge and multi-step reasoning first, so always re-run your evals rather than trusting the average benchmark.

**★ Compare open-source and closed-source LLMs.**
Closed APIs give you frontier quality with no infrastructure, fast iteration, and managed safety — at per-token cost, rate limits, vendor lock-in, and data-residency questions. Open weights give control, on-prem/air-gapped deployment, fine-tunability, fixed infrastructure cost that amortizes at high volume, and no silent model swaps — at the price of running GPUs, owning the serving stack, and typically a quality gap on the hardest tasks. Decide on data sensitivity, volume economics, latency requirements, and how much you need behavior frozen.
*PSW:* your answer is the third path people forget — a closed frontier model deployed *inside your own network boundary* via Bedrock, with contractual no-retention terms. That got you frontier quality and data governance without running GPUs. Lead with that; it's a genuinely good architecture answer.

**★ What is tokenization? Explain BPE, WordPiece, SentencePiece.**
Tokenization splits text into the discrete units the model actually sees — usually subwords, balancing vocabulary size against sequence length. BPE starts from characters and greedily merges the most frequent adjacent pair until it hits the target vocab size. WordPiece picks merges maximizing training-data likelihood rather than raw frequency. SentencePiece treats the raw byte/character stream (spaces included) as input so it needs no pre-tokenization and works for languages without whitespace. Practical consequence: token count drives both cost and context consumption, and non-English text and code tokenize far less efficiently.

**★ What are SLMs and LRMs?**
Small Language Models (roughly 1–10B, often distilled and quantized) trade breadth for cheap, low-latency, on-device or high-volume inference, and are frequently better than a frontier model for one narrow well-defined task. Large Reasoning Models are trained (usually with RL on verifiable outcomes) to spend extra inference-time compute on explicit chain of thought before answering, buying big gains on math, code, and multi-step logic at the cost of latency and tokens. Engineering upshot: route by task difficulty rather than defaulting every request to the largest model.

**Explain the Transformer architecture and its key components.**
A stack of identical blocks, each containing multi-head self-attention (tokens attend to other tokens, mixing information across positions) and a position-wise feed-forward network (per-token nonlinear transformation, where much of the model's knowledge lives). Each sublayer is wrapped in a residual connection and layer normalization, which is what makes very deep stacks trainable. Inputs are token embeddings plus positional information; the output projects to a vocabulary-sized logit vector.

**Explain Q, K, V and self-attention; why scale by √dₖ; what is causal masking?**
Each token is projected into a query (what am I looking for), a key (what do I offer), and a value (what I contribute). Attention is softmax(QKᵀ/√d_k)·V — a weighted average of other tokens' values. Self-attention draws Q, K, V from the same sequence; cross-attention draws Q from the decoder and K, V from the encoder, which is how translation and vision-language models condition on another modality. The √d_k divisor renormalizes score variance so softmax doesn't saturate into a near-one-hot regime with vanishing gradients. Causal masking sets future-position scores to −∞ before the softmax, enforcing autoregression while still allowing parallel training over all positions.

**What is positional encoding, and how does RoPE differ from learned embeddings?**
Self-attention is permutation-invariant, so without positional information "dog bites man" and "man bites dog" are identical. The original Transformer added fixed sinusoidal vectors; learned absolute embeddings add a trainable vector per position and don't extrapolate past the trained length. RoPE instead *rotates* query and key vectors by an angle proportional to position, so the attention dot product depends on relative distance — it extrapolates better, adds no parameters, and is why almost every modern model uses it (with NTK/YaRN scaling to extend context).

**What are multi-head attention and Grouped-Query Attention?**
Multi-head attention runs several attention operations in parallel on lower-dimensional projections and concatenates them, so heads can specialize instead of averaging everything into one relationship. GQA reduces inference memory by having multiple query heads share a single key/value head — plain multi-head attention gives every query head its own key/value head, multi-query attention shares a single one across all of them, and grouped-query attention sits between. It shrinks the KV cache substantially with minimal quality loss, which is why it's standard in serving-oriented models.

**Compare encoder-only, decoder-only, and encoder-decoder architectures.**
Encoder-only (BERT) uses bidirectional attention with masked language modeling — best for classification, NER, retrieval embeddings; it can't generate freely. Decoder-only (GPT, Llama, Claude) uses causal attention and next-token prediction — best for generation, and it dominates because it scales and generalizes to every task via prompting. Encoder-decoder (T5, BART) encodes bidirectionally and generates with cross-attention — still strong for translation, summarization, and seq2seq with a clear input/output split.

**Six more terms, recognition-level only.** You will not be asked to build any of these. You just need to not go blank if someone says the word.

- **Mixture of Experts.** Instead of one feed-forward layer per block, the model has many, plus a router that switches on only a couple per token. So the model can have enormous total size while each token only pays for a small slice of it. The costs: all the experts still have to sit in memory, the routing can be unstable during training, and fine-tuning is harder.
- **Flash Attention.** A faster way of computing exactly the same attention result. It works in tiles that fit in the chip's fast on-die memory and never builds the full n×n attention matrix in slower memory. Big real-world speedups, no change in output.
- **Cross-entropy loss.** The number a language model is trained to minimize: the negative log of the probability it assigned to the token that actually came next. Average it and exponentiate, and you get perplexity.
- **Knowledge distillation.** Training a small "student" model to copy a big "teacher" model's full probability distribution, not just its final answers. Students usually match the teacher on ordinary inputs and fall apart on hard reasoning.
- **Logits.** The model's raw scores over every possible next token, before they're turned into probabilities. Temperature, top-k, top-p, repetition penalties, and grammar constraints all operate on these.
- **Foundation model.** A model pretrained broadly once, then adapted by prompting, retrieval, or light fine-tuning rather than trained from scratch per task. That shift is why this job is retrieval, evaluation, orchestration, latency, and cost rather than model training.
---

## 6. LLM Serving, Inference & Infrastructure

> **PSW anchor:** FastAPI in front of Bedrock via a VPC endpoint. You didn't run GPUs — say so plainly and pivot to the decision: "Bedrock exposed the model as a managed API inside our own network boundary, so we got governance without owning a serving stack." Then answer the GPU questions as design knowledge, not as lived experience. Claiming vLLM tuning you didn't do is how these interviews go wrong.

**Design an inference batching system for a single GPU with synchronous users.**
The tension is throughput versus latency: bigger batches use the GPU better but make early-arriving requests wait. Use dynamic batching with two triggers — a max batch size (say 100) and a max wait window (5–20ms) — firing whenever either hits. Requests land in a queue; a scheduler pulls up to the cap, buckets them by sequence length so padding doesn't dominate, runs one forward pass, and scatters results back. Call out the knobs explicitly: the wait window is the latency/throughput dial, length bucketing controls padding waste, and backpressure (queue depth limits, shedding or 429s on overflow) keeps tail latency bounded. For token generation, mention continuous batching — finished sequences leave the batch and new ones join mid-generation. Interviewers want the trade-off made explicit plus at least one production detail.

**Dynamic vs. continuous batching?**
Dynamic (static) batching assembles a batch, runs it to completion, then accepts new work — so the whole batch waits on its longest sequence and the GPU idles on finished rows. Continuous (in-flight) batching schedules at the *iteration* level: after each decoding step, completed sequences are evicted and queued ones join immediately. That typically yields several-fold throughput improvement for generation and is the core innovation in vLLM and TGI.

**What is speculative decoding?**
A small fast draft model proposes k tokens ahead; the large model verifies them all in a single forward pass and accepts the longest correct prefix. Because decode is memory-bandwidth-bound, verifying k tokens costs nearly the same as generating one, so you get roughly 2–3x speedup with *identical* output distribution — it's lossless, which is what makes it attractive. Variants avoid the separate draft model: Medusa adds extra prediction heads, and n-gram/prompt lookup drafts from the context itself, which works remarkably well when output repeats input.

**How do you route requests across models by complexity and cost?**
Put a cheap router in front — a small classifier, embedding-similarity match, or heuristic on task type and prompt length — sending easy traffic to a small model and hard traffic to a frontier model. A cascade is the safer variant: always try the small model, score the output with a cheap verifier, and escalate only on low confidence, which caps quality loss at the cost of occasional double inference. Measure the router itself (escalation rate, per-tier accuracy, blended cost per request), and keep an override list for critical paths.
*PSW:* your classifier node is a router. If you ran classification on a cheaper model than generation, that's exactly this answer with a real example attached.

**What monitoring metrics matter for LLM serving?**
Latency split into time-to-first-token (prefill and queueing) and inter-token latency, or tokens per second (decode), at p50/p95/p99 — averages hide everything. Throughput in tokens/sec and requests/sec, queue depth and time-in-queue, GPU utilization and memory (KV cache occupancy), batch size distribution, error and timeout rates, cache hit rate, and cost per request. On the quality side: refusal rate, output length distribution, guardrail trigger rate, and user thumbs-down — quality regressions show up here before anyone files a bug.

**How does token streaming work and why does it matter?**
The server sends tokens as generated over Server-Sent Events or a WebSocket instead of buffering the full response. It transforms perceived latency — users start reading in a few hundred milliseconds — even though total generation time is unchanged. Implementation concerns: incremental parsing when output is structured, applying output guardrails to a stream (buffer to a safe boundary, since you can't unsay a token), handling client disconnects so you stop billing for abandoned generations, and proxies that buffer and silently break streaming.

**How do you survive a provider outage or rate limit?**
Design for it: an abstraction layer over providers so switching is config not code, at least two providers with prompts validated against both (outputs differ, so you need evals per provider), automatic failover with circuit breakers and exponential backoff with jitter, and request queuing for non-interactive work. Add graceful degradation — cached responses, a smaller model, or a clearly communicated reduced-functionality mode — because a degraded answer beats a 500. Track per-provider error rates and latency so failover triggers on real signal.

**How do you design backpressure and overflow handling?**
Bound every queue explicitly and decide overflow behavior up front: reject with 429 plus Retry-After, shed low-priority traffic, or degrade to a cheaper model. Use admission control based on estimated cost (prompt length, max tokens) rather than request count, separate queues by priority class with fairness guarantees, and set per-request timeouts. Monitor queue depth and time-in-queue as leading indicators — by the time p99 spikes, you're already failing.

**How do you implement semantic caching?**
Embed the incoming query, search a cache of previous query embeddings, and if similarity exceeds a threshold, return the stored response. It catches paraphrases an exact-match cache misses, which matters for support and FAQ traffic. The hard parts: threshold tuning (too loose returns confidently wrong answers to subtly different questions), scoping the key to include user/tenant/permissions, and TTL/invalidation when the underlying knowledge changes. Log cache hits with similarity scores so you can audit false hits — and don't semantically cache anything personalized or time-sensitive.
*PSW:* tempting for a corpus of ~150 recurring admin questions, and dangerous for the same reason — "how do I correct a missed employer match" and "how do I correct a missed employee deferral" are semantically close and procedurally different. Good answer if you name that risk.

**How do you version prompts and models, and roll back safely?**
Everything that affects output — prompt text, model ID and version, temperature and sampling params, retrieval config, tool definitions — is a versioned artifact in source control, bundled as one "config version" and logged with every request. Deploy behind flags with canary rollout, keep the previous version warm for instant rollback, and pin provider model versions rather than floating aliases so the vendor can't upgrade you mid-quarter. Rollback should be a config change, not a redeploy.

**LLMOps vs. traditional MLOps?**
Shared: versioning, CI/CD, monitoring, rollback. Different: the "model" is usually a third-party API you don't control and that changes under you; prompts become a first-class deployable artifact; evaluation is subjective and often needs LLM-as-judge plus human review rather than accuracy on a labeled set; cost is per-token and variable rather than fixed infrastructure; latency is user-visible and streaming; and new failure modes (hallucination, prompt injection, jailbreaks, nondeterminism) have no MLOps analogue. Practically, the eval harness plays the role the test suite plays in normal software.

**How would you design an org-wide AI gateway?**
A single proxy in front of all providers owning: authentication and per-team keys, routing and failover, per-team quotas and rate limits, cost attribution and chargeback, centralized logging/tracing, PII redaction and guardrails applied uniformly, caching, and a model allowlist for compliance. The value is that policy, cost visibility, and safety get enforced once instead of re-implemented by every team. Decide deliberately whether it fails open or fails fast, and keep added latency in the low single-digit milliseconds or teams route around it.
*PSW:* a large financial institution almost certainly has one. If Fidelity's Bedrock access went through a central platform team, that's the answer — describe it honestly as consuming a gateway rather than building one.

**Infrastructure, recognition-level only.**

- *Three ways to split a model across GPUs.* Data parallelism puts a full copy of the model on each GPU and splits the batch between them — simplest, but the model has to fit on one GPU. Tensor parallelism splits the matrices *inside* a layer across GPUs, so it needs a very fast link between them (NVLink, within a single machine). Pipeline parallelism gives different GPUs different layers, which tolerates slower links but leaves GPUs idling between stages. Large deployments combine all three.
- *Choosing a GPU.* For inference the binding constraint is memory size and memory bandwidth, not raw arithmetic speed — you need enough memory for the weights plus a healthy key-value cache, and bandwidth per dollar. For training it's memory (weights, gradients, optimizer state, and activations all at once), arithmetic throughput, and the interconnect between GPUs.
- *Reusing the key-value cache.* Paged Attention with copy-on-write so several requests sharing the same prefix share its cache, prefix caching across requests, grouped-query attention to shrink the cache, and quantizing the cache itself when memory is still the binding constraint.

---

## 7. Evaluation, Testing & Observability

> **PSW anchor:** This is the single most likely place to get caught, because compliance systems live or die on evaluation and "I spot-checked it" is a losing answer. Have real numbers: how many labeled questions, who reviewed them, what precision@k, and what the assistant did when it wasn't confident.

**How do you evaluate an LLM feature with no single correct answer?**
Decompose "good" into checkable properties and score those instead of chasing exact match: groundedness, instruction/format compliance, relevance, safety, tone, and absence of specific failure modes. Use a layered stack — deterministic assertions where possible (schema valid, citations present and real, no PII, length in range), LLM-as-judge with an explicit rubric for subjective dimensions, pairwise comparison against a baseline (easier and more reliable than absolute scoring), and a human-reviewed sample to calibrate the judge. Then define one decision metric so you can actually ship or not ship.

**How do you separate retrieval evaluation from generation evaluation?**
Score retrieval on its own with labeled query→relevant-chunk pairs: recall@k, precision@k, MRR/NDCG. Then score generation *given known-good context* — if you hand the model the correct passage and it still gets the answer wrong, the problem is generation, not search. Running both isolates the failure: low retrieval recall means fix chunking, embeddings, hybrid search, or reranking; good retrieval with poor faithfulness means fix the prompt, context ordering, or model. Teams that only measure end-to-end accuracy spend weeks tuning the wrong component.
*PSW:* say this one almost verbatim. It's the highest-signal sentence in the whole bank for a RAG candidate.

**What is LLM-as-a-judge / G-Eval, and what are its failure modes?**
Use a strong model with an explicit rubric (and in G-Eval, chain-of-thought plus probability-weighted scoring) to grade outputs at a fraction of human cost. Known biases: position bias (favoring first or second — randomize order and average both), verbosity bias (longer scores higher), self-preference bias (judges favor their own model family's style), poor calibration on fine-grained numeric scales, and leniency on subtle factual errors in unfamiliar domains. Mitigate by validating the judge against human labels and *reporting that agreement*, preferring pairwise to absolute scoring, using a coarse scale, using a different model family than the one under test, and keeping a human-reviewed slice.

**How do you detect and measure hallucination in production?**
Offline: a labeled set with known-correct answers, plus groundedness scoring (entailment scoring or a judge model) checking each claim against the provided context. Online, where ground truth is absent: citation verification (does the cited source exist and support the claim?), self-consistency across multiple samples (disagreement correlates with fabrication), retrieval-grounding checks, and token-probability/uncertainty signals. Track a hallucination rate on a sampled, human-reviewed slice as the ground-truth metric — everything else is a proxy — and segment it by query type, because the aggregate rate hides the categories that matter.
*PSW:* segmenting matters enormously here. A 2% hallucination rate that's concentrated entirely in loan-correction procedures is a different product than one spread evenly.

**How do you build a regression suite so a prompt or model change doesn't break quality?**
Curate a versioned golden dataset spanning core cases, edge cases, adversarial inputs, and every past production bug (every incident becomes a permanent test). Run it automatically in CI on any change to a prompt, model version, retrieval config, or tool definition; block the merge on threshold failures. Report per-category scores rather than a single average — an average hides a total collapse on a small but critical slice. Refresh the set periodically from real traffic so it doesn't drift from what users actually do.

**What is red teaming and how do you structure it before launch?**
Adversarial testing to find harmful, policy-violating, or embarrassing behavior before users do. Structure it: define a threat model and harm taxonomy for your specific product, assemble a mixed team (engineers, domain experts, trust and safety, ideally outsiders), combine manual creative probing with automated attack generation and known jailbreak suites, cover multi-turn escalation and indirect prompt injection (not just single prompts), and test in the real product surface rather than a bare API. Log every finding into a permanent regression suite, fix, and re-test — the deliverable is a living test suite plus a severity-ranked report, not a one-time exercise.

**Offline vs. online evaluation?**
Offline runs on fixed datasets before deployment — fast, cheap, repeatable, and it gates releases, but it's only as good as the dataset's coverage of reality. Online measures real traffic: A/B tests on task success, user thumbs, escalation and retry rates, plus continuous scoring of sampled production outputs. You need both — offline catches regressions before users see them, online catches what your dataset didn't anticipate, and the loop is that online failures become new offline test cases.

**A model gives confident but wrong answers in high-risk contexts — investigate and mitigate.**
First quantify it: build an eval set of high-risk prompts with known answers and measure how often the model is both wrong and confident, because "usually" needs a number before you can tell whether a fix helped. Then diagnose which of three things it is — a retrieval gap (it never had the facts), a calibration problem (wrong and confident regardless), or a prompt problem (nothing told it to express uncertainty or abstain). Mitigate in layers: ground high-risk answers in retrieval with citations so claims are checkable; instruct and few-shot the model to say "I'm not sure" and refuse outside its competence; add a verification pass or judge that checks the answer against sources before it ships; and for the highest-risk contexts route to a human. Re-run the eval to confirm the confident-wrong rate dropped *without* nuking helpfulness. The framing that matters: confidence and correctness are separate axes, and confident-and-wrong is the dangerous quadrant.
*PSW:* this is your project's entire thesis stated as a general principle. It should be your most fluent answer in the bank.

**How do you evaluate multi-turn conversations and agents end-to-end?**
For conversations, score at the session level, not the turn level: task completion rate, turns to resolution, context retention, recovery after a misunderstanding, and consistency of persona and facts. For agents, score the trajectory as well as the outcome — task success, tool-selection accuracy, parameter correctness, steps and cost per task, loop/stall rate, and whether guardrails fired appropriately. Build reproducible scenarios with mocked tools so runs are comparable, use full tracing (LangSmith, Arize Phoenix, OpenTelemetry-style spans) so you can see which step went wrong, and include an "agent should have escalated" category — knowing when to stop is a capability worth measuring.

**Classical metrics, for lineage.** BLEU measures n-gram precision against reference translations with a brevity penalty; ROUGE measures n-gram recall or longest common subsequence against reference summaries; BERTScore compares contextual embeddings so it credits paraphrase. All three assume a reference answer exists and correlate weakly with human judgment on open-ended generation — name them to show you know the lineage, then say you'd use LLM-as-judge plus task-specific checks for modern generative work.

---

## 8. Cost, Latency & Production Trade-offs

> **PSW anchor:** Bedrock is per-token, so every cost lever below was live for you. If you tracked cost per query or capped output length, lead with it. If you didn't, say "we weren't cost-constrained at our volume, but here's what I'd instrument first" — that's a fine answer and better than inventing numbers.

**How do you reduce token usage without losing essential context?**
Measure where tokens actually go first — usually a bloated system prompt repeated on every call, or over-retrieval. Then: trim the system prompt to what demonstrably changes behavior (ablate and measure), retrieve tighter top-k with a reranker instead of stuffing chunks, summarize or compact conversation history rather than resending it, filter tool outputs before they enter context, and cap max output tokens. Move stable content to the prompt prefix so provider caching applies. Validate each cut against your eval set — token reduction that costs accuracy is just a quieter regression.

**What batching and caching tricks keep latency low?**
Continuous batching for throughput without holding requests hostage to the longest sequence; length bucketing so padding doesn't dominate; a tuned wait window as the explicit latency/throughput dial. Caching at three levels: provider prompt/prefix caching for stable system prompts (biggest easy win), semantic caching for repeated or paraphrased queries, and application-level caching of retrieval results and embeddings. Plus streaming, which cuts *perceived* latency dramatically without touching actual compute.

**Hosted API vs. self-hosted open model?**
Hosted wins on time-to-market, frontier quality, zero ops, and elastic capacity — at per-token cost, rate limits, less control over model changes, and data-handling questions. Self-hosting wins at sustained high volume (fixed GPU cost amortizes), when data can't leave your environment, when you need a frozen model version or heavy fine-tuning, or when you need predictable latency without shared tenancy. Do the arithmetic out loud: compare per-token API spend at your projected volume against GPU-hours plus engineering headcount, and note the crossover is usually higher than people expect once you price the ops burden.
*PSW:* your answer is that "data can't leave the environment" did *not* force self-hosting, because Bedrock-in-VPC satisfied it. That's the insight — people assume data governance means running your own GPUs, and it often doesn't.

**When do you quantize, and when do you regret it?**
Quantize when memory or throughput is the binding constraint and you can measure the quality cost — INT8/FP8 is usually near-lossless, INT4 is where things get interesting. You regret it when you quantized on an average benchmark score and shipped: degradation is uneven, hitting long-tail knowledge, multi-step reasoning, non-English languages, and structured-output compliance first. Always re-run your own task evals post-quantization, prefer calibration-based methods (GPTQ/AWQ) over naive rounding, and keep the option of quantizing only some layers.

**How do you estimate the cost of a new AI feature?**
Model it bottom-up: requests per user per period × active users × (input tokens + output tokens × output price ratio) × price per token, plus retrieval/embedding costs, plus retries and failed calls, plus eval and monitoring overhead. Sanity-check with a prototype on real traffic samples rather than trusting your token estimates — prompt sizes are always bigger than people guess. Present it as cost per user per month and cost per successful task, model a pessimistic case (agent loops, long documents), and set a budget alert before launch, not after.

**How would you cut an AI feature's operating cost substantially without visibly hurting quality?**
Instrument first to find where the money goes by endpoint and user segment; spend is almost always concentrated. Then apply in order of effort-to-savings: prompt/prefix caching, prompt slimming, output token caps, semantic caching, tighter retrieval, model routing so the small model handles the easy majority, batching non-interactive work, and finally distillation or fine-tuning a small model for the highest-volume narrow task. Gate every change behind an A/B test with your quality evals as guardrail metrics, and report the result as **cost per successful task** — cheaper-but-failing requests aren't savings.

---

## 9. AI System Design

> Use the same skeleton every time: **clarify scope** (users, scale, latency SLA, cost ceiling, what a wrong answer costs) → **data and storage** → **model/serving choices with trade-offs named** → **guardrails and human fallback** → **evaluation and monitoring** → **cost**. Interviewers score the trade-offs you surface, not the diagram.
>
> **PSW anchor:** You've already shipped the "chat with your documents" design in a regulated environment. For any prompt below, start from what you actually built and adapt outward — including the build-vs-buy call you already defended (why not Bedrock Knowledge Bases: you wanted control over category-based chunking and the classify-then-retrieve flow).

**Design a "chat with your documents" RAG system.**
Ingestion: upload → virus scan → format-aware parsing (layout-aware for PDFs) → chunking with structure preservation → embedding → vector store with tenant/ACL metadata, tracking document versions. Query: rewrite the query using conversation history → hybrid retrieval with metadata pre-filtering by permission → rerank → assemble context → generate with mandatory citations → stream. Add conversation memory, per-tenant isolation, incremental re-indexing on document change, and hard deletes on removal. Evaluate retrieval and generation separately; monitor faithfulness, citation validity, latency, and cost per query. Name the failure modes you're designing against: scanned PDFs, tables, multi-hop questions, and stale documents.

**Design an AI document-processing pipeline for a regulated industry.**
Ingest → classify document type → layout-aware extraction (OCR plus a document-understanding model for tables and forms) → structured field extraction against a schema with per-field confidence → validation against business rules and cross-document consistency → human review queue for anything below threshold → downstream system write, with full lineage. The requirements that dominate the design: every extracted field traceable to a page region, confidence-based routing rather than blanket automation, immutable audit logs, data residency and encryption, and a golden-set eval with per-field accuracy so you can prove the automation rate you claim. Design the human-review UX carefully — that's where the actual throughput lives.
*PSW:* closest neighbor to your project. Same regulatory posture, same traceability requirement, plus extraction.

**Design a multi-agent customer-support system.**
Supervisor agent routes by intent to specialists (billing, technical, account, returns), each with a scoped tool set and its own retrieval namespace — the justification for multiple agents is different tools and permissions per domain, not fashion. Shared: conversation state, customer context, and a policy engine encoding hard rules in code. Escalation is a first-class path with confidence thresholds, sentiment/vulnerability detection, and full context handoff. Guardrails on every action tool; audit log of everything. Metrics: containment rate, resolution accuracy, escalation precision, handle time, CSAT, and cost per conversation — and compare honestly against a single agent with all the tools, which is often good enough.

**Design memory for a personal AI assistant.**
Layers: working memory (recent turns in context), episodic (past conversations, embedded and retrievable), semantic (extracted durable facts in a structured store), procedural (learned preferences and routines). Write path: after each session, an extraction step proposes candidate facts, deduplicates and reconciles them against existing memory (new information should *update*, not append), and writes with provenance and timestamps. Read path: retrieve only relevant memories per turn rather than injecting everything. Non-negotiables: user visibility and editability, deletion honoring GDPR, encryption, and a clear boundary on what you never store (health, financial, credentials) unless explicitly authorized.

**Design a deep-research agent.**
Plan-and-execute over search: decompose the question into sub-questions, run parallel retrieval across web and internal sources, evaluate source credibility and recency, extract claims with citations, identify contradictions between sources, and iterate on gaps until coverage is sufficient. Then synthesize with a strong model and verify every claim against its cited source before output. Controls: budget caps on searches and tokens, deduplication of near-identical sources, a hard stop with a partial report, and progress streaming since these run for minutes. Evaluate on citation accuracy, coverage against expert-written reports, and contradiction detection rate.

**Design an LLM evaluation platform.**
Core objects: datasets (versioned, with golden answers and metadata), evaluators (deterministic assertions, LLM judges with versioned rubrics, human review tasks), runs (a config version × dataset), and results with per-category breakdowns. Features: CI integration that blocks merges on regressions, side-by-side run comparison, drill-down to failing examples with full traces, a human labeling UI to calibrate judges, and production sampling that pipes real traffic into the same evaluators. Report judge-vs-human agreement as a first-class metric — an evaluation platform whose judges aren't validated is just generating confident numbers.

**Design a resume-screening system handling 100K applications/week.**
Lead with fairness and legal constraints, because that's what's being tested. Pipeline: parse → structured extraction of skills, experience, education → match against explicit job-requirement criteria → rank → human review. Critical choices: score against *stated job criteria* rather than similarity to past hires (which encodes historical bias), remove or mask name, gender, age, school, and photo signals, audit for proxy features (zip code, activities, employment gaps), and never auto-reject — the system surfaces and ranks, humans decide. Then: disaggregated selection-rate monitoring by protected group (four-fifths rule), candidate notification that AI is used and an appeals path, audit logs retained per regulation (NYC Local Law 144 requires a published bias audit; the EU AI Act classes this as high-risk). 100K/week is ~10/second — trivially handled with async batch processing, a cheap model for parsing and a stronger one for ranking.

**Design an AI coding agent.**
Context is the hard problem: index the repository (semantic search plus symbol- and syntax-aware indexing), retrieve relevant files and definitions for the task, and keep the working context focused rather than dumping the repo. Loop: understand the request → locate relevant code → propose a plan → edit files with precise diffs → run tests and the type checker → read failures → iterate. Tools: file read/write, search, sandboxed terminal, test runner, linter, LSP for symbol resolution. Guardrails: no destructive git operations, no network egress by default, secrets excluded from context, human review before merge. Evaluate on task completion on SWE-bench-style benchmarks (real GitHub issues), test pass rate, diff size, and how often the agent gives up cleanly rather than thrashing.

**How do you design graceful degradation?**
Rank features by criticality and define an explicit degraded mode per dependency failure: reranker down → serve vector-only results; primary model down → smaller or alternate-provider model; retrieval down → answer from the model with an explicit caveat, or fall back to keyword search; everything down → cached responses or a deterministic non-AI path. Implement with circuit breakers, timeouts on every call, and feature flags letting a human force a degradation level. Communicate degradation in the UI rather than silently serving worse results, and alert on degradation-mode entry so it never becomes the invisible steady state.
*PSW:* the natural degraded mode is "we couldn't find a matching procedure — here's the service-request index and a link to open a manual request." Failing *into the old manual workflow* is the right design in a compliance context.

---

## 10. Behavioral & Scenario-Based

> Use STAR — Situation, Task, Action, Result — and quantify the result. "Cut p95 latency from 4s to 900ms" beats "it got faster." Prepare 4–5 stories you can flex across questions rather than a story per question.
>
> **PSW anchor:** PSW is one of those stories, and it's your strongest. But it can't be all five — an interviewer who hears the same project answer every behavioral question concludes you've done one thing. Have a second and third: the resume-tailoring project (retry loops, structured output, a real quality bar), and one story that isn't about a project at all — a disagreement, a mistake, a handoff.

**Tell me about a challenging AI project.**
Structure: the problem and why it mattered commercially; the constraints you were under; the approach and the *alternatives you rejected and why* (this is where the signal is); the trade-offs you accepted; what went wrong and how you found out; the quantified outcome; what you'd do differently. Choose a project where you owned real decisions, not one where you were adjacent to the interesting part.
*PSW:* your rejected alternatives are unusually good material — public LLM API (governance), fine-tuning (no citations), Bedrock Knowledge Bases (wanted control over chunking and the classify-then-retrieve flow), fixed-token chunking (fragments procedures). Most candidates can't name four.

**Tell me about a time you were confident and later wrong.** *(Anthropic)*
Pick a real one with consequences, not a humblebrag. Show the debugging path: what evidence made you confident, what contradicted it, how quickly you noticed, how you communicated it, and what process change came out of it (a test, a metric, a review step). Interviewers are testing calibration and honesty — a story where nothing actually went wrong scores worse than a genuine miss handled well.

**Tell me about a time you had to build something that conflicted with your values.** *(Anthropic)*
Be specific and non-performative. Describe the concern, how you raised it and with whom, what you proposed as an alternative, and what actually happened — including if you were overruled and how you handled that. Avoid both extremes: "I've never had a concern" reads as unreflective, and a story where you unilaterally blocked the team reads as hard to work with. The signal is that you can voice a concern constructively through the right channels.

**How do you decide whether a problem needs AI at all?**
Ask what the deterministic baseline is and how far it gets you — regex, rules, SQL, or a small classifier solves a lot of "AI problems" at a fraction of the cost with none of the nondeterminism. Reach for AI when the input is genuinely unstructured or open-ended, the rules would be unenumerable or constantly changing, and imperfect output is acceptable with a fallback. Then check that you can evaluate it, that you can tolerate the failure mode, and that the cost per task works. "We tried the simple thing first" is a strong answer.
*PSW:* worth being able to say why a search box over the docs wasn't enough — admins didn't know which *category* their problem fell into, which is precisely the classification step. That's the honest justification for the AI, and it's specific.

**How do you measure the ROI of an AI feature?**
Define the business metric before building: deflected support tickets × cost per ticket, hours saved × loaded rate, conversion lift, or cycle-time reduction — and instrument the baseline first so you can attribute the change. Against that, count total cost: inference, retrieval infrastructure, evaluation and human review, engineering, and the ongoing maintenance AI features uniquely need. Measure with a holdout or A/B rather than pre/post comparison, and be willing to report that a feature didn't pay for itself.
*PSW:* the open item from your own follow-up list. Get real numbers if you can — admins served, ticket volume before/after, time per request — or state honestly what you measured and what you didn't.

**How would you explain a technical AI concept to a non-technical stakeholder?**
Start from what they care about, use one concrete analogy, avoid jargon and numbers they can't act on, and end with the decision they need to make. For "why can't it be 100% accurate": the model predicts likely text rather than looking up facts, so it can be fluent and wrong — which is why we ground it in your documents, cite sources, and route uncertain cases to a person. Then reframe from "is it perfect" to "is it better than the current process, and is the failure mode acceptable and contained." Offer to show examples of both success and failure — nothing builds calibrated trust faster.

**Your PM wants to ship with a known hallucination rate on edge cases — how do you communicate the risk?**
Quantify rather than object: how often it happens, on which query categories, what a wrong answer actually costs in that category, and whether the error is detectable by the user. Then present mitigation options with their costs and residual risk — restrict scope to the safe categories, add citations so errors are checkable, gate the risky category behind human review, add a confidence threshold with abstention — and make the trade-off explicit so the decision is informed and documented. Propose a staged rollout with monitoring and a kill switch, and name the specific metric that would trigger a rollback. Your job is to make the risk legible and the decision reversible, not to unilaterally block the launch.

**Complex agentic system that benchmarks better, vs. simpler RAG that's easier to maintain — how do you decide?**
Interrogate the benchmark first: is the gain on the traffic distribution that matters, is it statistically real, does it hold on your own eval set rather than a public one? Then price the complexity honestly — nondeterministic cost and latency, harder debugging, more failure modes, on-call burden, slower iteration. Default to the simpler system unless the gain lands on a business-critical slice, and consider the hybrid: ship RAG, add agentic behavior only for the query categories where it demonstrably wins. Say the decision rule out loud — "I'd need the gain to be on high-value queries and to survive on our own eval before taking on that operational cost."
*PSW:* you already made this call. Classify-then-retrieve is the simple pipeline; you didn't make it agentic because it didn't need to be.

**How do you stay current?**
Be specific and honest rather than listing everything. A workable answer: a couple of primary sources (lab technical reports and papers you actually read, not just abstracts), one or two curated newsletters, and — most importantly — building with new capabilities on a small project so the knowledge is hands-on. Add how you filter: most releases don't change what you'd build, so you evaluate against whether it changes a real constraint (cost, latency, context, capability). Have one recent thing you can discuss in genuine depth; that's what actually gets tested.

**Why this company? What recent advancement interests you?**
For "why here": connect something specific about their product, research direction, or constraints to work you've done or want to do — generic mission-speak reads as unprepared, especially at safety-focused labs where values questions appear in technical loops. For "what's interesting": pick something you can discuss two levels deep, explain why it changes what's buildable rather than just describing it, and be ready for "what are its limitations?" — enthusiasm without critique is a red flag.

---

# TIER 2 — Know the shape

Recognition-level. You should be able to hold a conversation and name a trade-off; you should not be memorizing derivations.

## 11. Fine-Tuning & Model Adaptation

**When to fine-tune at all.** When the problem is *behavior*, not knowledge: consistent output format, a specific tone, domain vocabulary the base model handles awkwardly, or a narrow high-volume task where a small fine-tuned model replaces an expensive frontier one. Don't fine-tune to inject facts — they go stale, can't be cited, and RAG does it better. Prerequisites: a few hundred to a few thousand high-quality examples, an eval set, and a plan for maintaining it as base models improve. *PSW:* this is exactly why you didn't fine-tune, and you should say it in one sentence: "the requirement was citable, current facts, which is a retrieval problem, not a behavior problem."

**Full fine-tuning vs. PEFT.** Full updates every weight — maximum capacity, but memory for weights + gradients + optimizer states (~12–16 bytes/param with Adam), a full model copy per task, and catastrophic-forgetting risk. PEFT freezes the base and trains <1% added parameters: an order of magnitude less memory, tiny hot-swappable artifacts per customer, and largely preserved general capability. PEFT is the default; full fine-tuning is for large domain shifts with lots of data and budget.

**LoRA and QLoRA.** LoRA freezes base weights and learns a low-rank update ΔW = BA with rank r (typically 8–64), on the observation that needed adaptation is intrinsically low-rank — 0.1–1% of parameters trained, adapters a few megabytes, mergeable into the base for zero added inference latency, many kept per task. QLoRA adds a 4-bit (NF4) quantized frozen base with double quantization and paged optimizers, so gradients flow through the quantized base into fp16 adapters — that's what makes fine-tuning a 30B+ model on a single consumer GPU possible, at some throughput cost. Prefix/prompt tuning trains even fewer parameters but consumes context length, underperforms LoRA except at very large scale, and can't be merged away.

**Data and hyperparameters.** Quality over quantity — a thousand curated examples routinely beats a hundred thousand noisy ones. Match the exact inference format, deduplicate aggressively, cover edge cases and refusals rather than only the happy path, decontaminate against your eval set, hold out a real validation split, strip PII. Learning rate matters most (roughly 1e-5–5e-5 for full fine-tuning, 1e-4–3e-4 for LoRA); 1–3 epochs is typical, more means memorization; for LoRA, rank 8–16 for style/format and 32–64+ for genuine new capability, alpha commonly 2r, attention projections at minimum. Sweep learning rate and rank first; everything else is second-order.

**Catastrophic forgetting.** The model overwrites general capability while specializing — aces your domain, forgets everything else. Prevent with PEFT, lower learning rates, fewer epochs, 5–20% general/replay data mixed in, and early stopping on a *general-capability* eval, not just your domain metric. The operational lesson: always evaluate on a general benchmark alongside your task metric, or you won't notice until users do.

**Instruction tuning and synthetic data.** Instruction tuning is supervised fine-tuning on (instruction, response) pairs across many task types — it's what converts a raw next-token predictor into something that follows directions, usually followed by preference alignment. Synthetic data (a strong model generating examples) works well for coverage of rare cases and for distillation; risks are inherited bias, mode collapse, and compounding factual errors — mitigate with seeded diversity, automated filtering and dedup, human verification on a sample, and always blending in real data.

**How to evaluate a fine-tune.** Against a held-out set the model never saw, with three comparisons: the base model with a good prompt (does fine-tuning actually beat prompting?), the base model with RAG, and the previous fine-tune. Measure task metrics, general-capability benchmarks, safety/refusal behavior, and format compliance. Probe for memorization with training-set prefixes, and confirm the cost/latency win is real — a fine-tune that merely matches a prompted small model isn't worth the maintenance burden.

## 12. Alignment & Learning from Human Feedback

> Everything else in classical reinforcement learning (Q-learning, SARSA, Bellman updates, model-based vs. model-free) was removed. These four paragraphs stay because they explain the behavior you engineer around every day: why models are sycophantic, why they pad answers, why they refuse oddly. That's operational knowledge, not trivia.

**PPO, DPO, GRPO.** Proximal Policy Optimization (PPO) is a policy-gradient method limiting how far each update moves the policy via a clipped surrogate objective, giving stable updates — the classic RLHF optimizer, run against a learned reward model. Direct Preference Optimization (DPO) removes the separate reward model and RL loop entirely, reformulating preference learning as a direct classification-style loss on chosen-vs-rejected response pairs — far simpler and more stable, which is why most labs moved to it. Group Relative Policy Optimization (GRPO) drops the value/critic network and normalizes rewards within a group of sampled responses to the same prompt, cutting memory cost — the method behind recent reasoning-model training.

**RLHF, reward hacking, and the alignment tax.** RLHF: collect human preference comparisons, train a reward model on them, then optimize the policy against that reward model with PPO plus a KL penalty — a mathematical leash keeping the tuned model close to the base model. **Reward hacking** is the model exploiting flaws in the reward model — verbose, sycophantic, or confidently formatted answers that score well without being better; counter it with the KL penalty, reward-model ensembles, adversarial/red-team data, and periodic reward-model retraining on fresh policy samples. The **alignment tax** is the capability drop alignment training can cause; mitigations include mixing pretraining or capability data into the alignment run and tuning the KL coefficient.
*Why you care operationally:* reward hacking is the reason a model will confidently pad an answer rather than say "I don't know." That's the exact failure your PSW grounding prompt was fighting, and connecting the two is a genuinely strong interview moment.

**Learning from AI feedback (RLAIF).** Replaces human preference labels with AI-generated ones — a model judges which response is better, often guided by an explicit written principle set (Constitutional AI). It scales far more cheaply and consistently than human annotation and removes annotator throughput as a bottleneck. The risks are inheriting the judge model's biases and blind spots, so in practice it's paired with human labels on the hardest and highest-stakes slices.

**Exploration vs. exploitation.** The one classical-RL idea worth keeping, because it recurs everywhere: exploitation uses current knowledge to take the best-known action; exploration tries unknown actions to gather information. Pure exploitation gets trapped in local optima; pure exploration never converges. You meet it again as temperature in sampling, as ε-greedy in routing and A/B allocation, and as the "try the small model first, escalate on low confidence" cascade.

## 13. AI Safety, Ethics & Responsible AI

> **PSW anchor:** You built in a regulated financial context, so these aren't abstract for you — governance is why the architecture looks the way it does. That's a real advantage over candidates who only know this as a checklist.

**What causes hallucinations, and how do you mitigate them?**
Fundamentally, LLMs are trained to produce plausible continuations, not to track truth — and nothing in next-token prediction or RLHF rewards saying "I don't know" (preference training often rewards confident answers). Contributing causes: knowledge gaps, outdated training data, ambiguous prompts, conflicting or distracting context. Mitigations in layers: ground answers in retrieval with mandatory citations, prompt and few-shot explicit abstention, constrain the task scope, verify with a second pass (entailment scoring, a judge model, or self-consistency), surface uncertainty in the UI, route high-stakes cases to a human. You reduce the rate; you don't eliminate it — say that.

**Privacy law and personal-data handling.** Establish a lawful basis and purpose limitation before sending anything to a model; minimize collection and retention; honor access, correction, deletion, and portability rights; document high-risk processing in a Data Protection Impact Assessment; check data residency and sub-processor terms with your vendor, including whether prompts are retained or used for training. Operationally: detect and redact personal data on the way in (named-entity recognition plus regex patterns), use tokenization/pseudonymization, scan outputs for leakage, keep prompt/response logs encrypted with short retention and access controls. The hard problem worth naming: the right to erasure conflicts with data baked into model weights — you handle it by keeping personal data in the retrievable (deletable) layer rather than in fine-tuned weights. *PSW:* Bedrock's no-retention/no-training terms plus VPC-endpoint access is a textbook answer to the vendor half of this. Say it in those terms.

**Bias.** Sources: data bias (historical outcomes, unrepresentative sampling, labeling), model bias (objective choice, proxy features standing in for protected attributes), and deployment bias (feedback loops where the model's decisions shape future training data). Reduce across the lifecycle: audit and rebalance data, remove or test proxy features, apply fairness constraints or reweighting, post-hoc threshold adjustment, and — most importantly — measure disaggregated metrics by subgroup including *intersectional* groups, since a model can pass on gender and race separately while failing badly at their intersection. Note that fairness definitions (demographic parity, equalized odds, calibration) are mathematically incompatible, so you choose which one your domain requires and defend it.

**Audit trails for AI decisions.** Log immutably, with retention matching the regulatory window: input, exact model and version, full prompt/config version, retrieved context with document IDs and versions, raw output, final decision, confidence, any human override and who made it, timestamp. Structure it so you can reconstruct *why* a decision was made months later — which means logging retrieved sources, not just the answer. Logs may contain PII, so encrypt, restrict access, define retention. The anti-pattern: discovering during an audit that you kept outputs but not the inputs or model version.

**EU AI Act.** Risk-tiered: unacceptable uses banned; high-risk (employment, credit, education, essential services, law enforcement, medical devices, critical infrastructure) carries substantial obligations; limited-risk requires transparency (disclose AI interaction, label synthetic media); minimal risk largely unregulated, with separate obligations for general-purpose model providers. High-risk means risk management, data governance, technical documentation, logging and traceability, human oversight, accuracy/robustness/cybersecurity, and conformity assessment. Practical answer: classify the use case early, because building documentation, logging, and human oversight in from the start is far cheaper than retrofitting.

**Consumer GenAI safety, layered.** Model layer: an aligned model, and don't erode safety training if you fine-tune. Input layer: classify and block prohibited requests, sanitize untrusted content, detect injection. Output layer: content filters, PII scanning, groundedness checks, helpful rather than curt refusals. System layer: least-privilege tools, human review for consequential actions, rate limiting, abuse monitoring. Product layer: set expectations in the UI, make AI-ness obvious, easy reporting and escalation, and explicit design for the vulnerable user. Then measure — red team pre-launch, monitor safety metrics post-launch, treat safety regressions like reliability regressions.

**Over-reliance and automation bias.** Reviewers rubber-stamp confident AI output, so a nominal "human in the loop" can provide no actual check. Counter it by design: show evidence and reasoning rather than a verdict, present calibrated uncertainty and force explicit engagement on low-confidence cases, avoid anchoring by letting the expert judge before revealing the AI's answer, occasionally withhold the suggestion to keep skills sharp. Measure it: track override rates and, critically, accuracy on cases where the AI was wrong — if reviewers agree just as often when it's wrong, your oversight is theater.

**Incident response.** Same shape as a security program with AI-specific detection: severity levels and triggers, an on-call owner, and a kill switch (a feature flag disabling the AI path and falling back to a deterministic or human process without a redeploy). Prepare rollback to a previous prompt/model version, user notification and remediation, preserved logs, and a blameless post-mortem template that asks why the eval suite missed it. Every incident becomes a permanent test case.

## 14. Practical / Take-Home Coding Prompts

> Graded on working code that survives edge cases, not cleverness. Narrate the plan before writing, handle empty/malformed/large inputs on purpose, and leave time for at least one test. The first four are the ones you should be able to write from memory — they're your project, stripped down.

**★ Implement a basic RAG pipeline.** Load documents → chunk with overlap → embed in batches → upsert to a vector store with metadata → at query time embed the query, search top-k, format context with source markers, and call the LLM with an "answer only from context" instruction. What separates a strong submission: batching embedding calls, retry with backoff, persisting the index rather than rebuilding, deterministic chunk IDs so re-ingestion updates rather than duplicates, and returning sources alongside the answer.

**★ Write different chunking strategies.** Fixed-size with overlap (slide a window of N tokens with stride N−overlap), recursive (split on paragraph, then sentence, then word separators, recursing until chunks fit), semantic (embed sentences, split where consecutive similarity drops below a threshold). Count in *tokens* using the real tokenizer, not characters. Preserve metadata and character offsets on every chunk so citations can point back to the source.

**★ Implement semantic search with cosine similarity from scratch.** Normalize each embedding to unit length, then cosine similarity reduces to a dot product; compute query·corpus as a single matrix-vector product with NumPy rather than a Python loop, and use `argpartition` for top-k instead of a full sort. Handle the zero-vector case, and mention this is exact O(n) search — fine to a few hundred thousand vectors, after which you'd move to an approximate-nearest-neighbour index. *This is your L2-normalization decision, written out.*

**★ Build a simple tool-using agent.** Define tools as functions with JSON schemas, pass them to the model's function-calling API, and loop: call the model, if it returns a tool call then execute it and append the result, else return the answer. Must-haves: a max-iteration cap, try/except around tool execution returning the error message back to the model rather than crashing, argument validation before execution, and a transcript log of every step.

**Build an LLM-as-a-judge evaluation pipeline.** Load a dataset of inputs with references or rubric criteria, generate outputs from the system under test, prompt a judge model with a structured rubric returning a score plus justification in a fixed schema, aggregate with per-category breakdowns. Quality touches: randomize order in pairwise comparisons to control position bias, judge at temperature 0, handle parse failures with a retry, include a human-labeled subset to report judge-human agreement.

**Implement streaming responses for an LLM API.** Server: iterate the provider's stream and yield Server-Sent Events (`data: {...}\n\n`), flushing per chunk and disabling proxy buffering. Client: read incrementally and render. Handle client disconnect (cancel upstream so you stop paying), errors mid-stream (you've already sent a 200, so signal the error in the event payload), and incremental parsing if the payload is structured.

**Implement conversation memory (sliding window / summary / buffer).** Sliding window keeps the last N turns; token-buffer keeps as many as fit a budget counted with the real tokenizer; summary memory compresses older turns into a running summary when the budget is exceeded. The robust version is hybrid: always preserve the system prompt and most recent turns verbatim, summarize the middle, never split a user/assistant pair. Handle a single message exceeding the budget.

**Implement retry with exponential backoff.** Retry only on retryable errors (429, 5xx, timeouts, connection errors) — never on 400s or content-policy refusals. Delay = min(base × 2^attempt, cap) plus jitter, honor `Retry-After`, cap total attempts and total elapsed time, log each retry. Bonus: a circuit breaker so a sustained outage fails fast instead of retrying every request.

**Write a function-calling handler.** Registry mapping tool name → (callable, JSON schema). On a call: look up the name (unknown → return an error message to the model, don't crash), validate arguments against the schema, execute with a timeout, serialize the result (truncating large outputs so they don't blow the context), append it as a tool-result message. Support parallel tool calls if the API returns several, and never `eval` arguments.

**Debug and extend a Python codebase to add async retries with timeouts.** *(Sierra)* Wrap the call with `asyncio.wait_for` for a per-attempt timeout inside a retry loop with exponential backoff and jitter. Distinguish per-attempt timeout from total deadline, propagate `CancelledError` rather than swallowing it, use `asyncio.sleep` not `time.sleep`, and bound concurrency with a semaphore. Write it as a decorator, and add a test with a mock that fails twice then succeeds.

**Classic data-structure prompts that still show up.** These are plain coding questions — no AI involved. Reported by candidates at the named companies.

- *Spreadsheet dependency traversal with cycle detection (Sierra).* Build a directed graph from the formula references, then walk it depth-first with three-colour marking (white = unvisited, grey = currently being visited, black = done). Hitting a grey node means a cycle — report the actual cycle path, not just `true`. Memoize computed values, handle cell ranges and self-references, and return a `#REF!` / `#CIRCULAR!` error value instead of throwing.
- *Duplicate file scan (Anthropic).* Three-stage funnel so you never hash more than you must: group files by size, then hash only the first and last 4KB of same-size files, then full-hash only the survivors. Read in chunks, handle permission errors and symlink loops, and use `os.scandir` / `os.walk` rather than your own recursion.
- *In-memory key-value store with transactions (OpenAI, xAI).* A base dictionary plus a stack of overlay dictionaries. `begin` pushes a new overlay; `set` and `delete` write to the top one (use a tombstone marker for deletes); `get` searches top-down then falls through to the base; `commit` merges the top overlay down; `rollback` pops it. Nested transactions come free from the stack.
- *Credit expiry from an event stream (OpenAI).* Sort events chronologically, keep credit grants in a min-heap ordered by expiry date, purge expired grants before each usage event, and consume the soonest-expiring credit first, splitting across grants when needed. The real test is the edge cases: usage exceeding the balance, credits expiring exactly at query time, out-of-order events, zero or negative amounts.
- *Image pipeline driven by per-image instruction files (Anthropic).* Discover the image/instruction pairs, parse instructions into an ordered list of operations, dispatch by operation name from a lookup table. Robustness is what's graded — skip and report malformed files rather than aborting the run, validate parameters, use a parallel worker pool, stream files rather than loading them whole, and write output atomically (temp file, then rename).

---

## Frameworks worth memorizing

**RAG / agent design:** Scope (inputs, outputs, latency and cost budget, cost of a wrong answer) → Ingest (chunk, embed, metadata) → Retrieve (tight top-k, hybrid, rerank) → Act/Generate (structured output; tools and approval gates for agents) → Guardrails (out-of-scope refusal, output validation, human fallback above thresholds) → Evaluate (retrieval and generation scored separately, logged with citations).

**LLM serving:** Requirements (QPS, latency SLA, sync vs. async, batch limits) → Batching (dynamic: size + wait window; continuous for generation) → Efficiency (KV-cache reuse, length bucketing, model routing) → Backpressure (queue limits, overflow behavior, bounded tail latency) → Cost (token budgets, caching, cheaper models for easy traffic).

**Debugging any LLM failure:** Reproduce with the exact logged context → isolate the layer (retrieval / prompt / model / parsing / tool) → quantify with an eval set before changing anything → fix one variable → re-measure → add it to the regression suite.

**STAR:** Situation (one or two sentences) → Task (your specific responsibility) → Action (what you did, with technical detail) → Result (quantified).

**The PSW spine — the four decisions you can defend, in order:**
1. **Bedrock in our own VPC with no-retention terms** — because compliance data couldn't leave Fidelity's boundary, and that did *not* require running our own GPUs.
2. **Retrieval with citations over fine-tuning** — because a hallucinated field has real operational consequences and traceability was non-negotiable.
3. **Category-based chunking over fixed-token** — because a retrieved chunk had to be a complete procedure, not a fragment.
4. **Classify-then-retrieve over managed Knowledge Bases** — a deliberate build-vs-buy call for control over chunking and flow.

Every Tier 1 question can be answered off one of those four. That's the whole point of this rewrite.

---

## Sources

1. **AI Engineering Interview Questions and Answers** — Amit Shekhar / Outcome School: https://github.com/amitshekhariitbhu/ai-engineering-interview-questions
2. **45+ AI Engineer Interview Questions & Answers (2026 Guide)** — UPenn Career Services, republished from Exponent; real candidate-reported questions from OpenAI, Anthropic, Scale AI, Sierra, xAI, Databricks, Perplexity: https://careerservices.upenn.edu/blog/2026/06/25/45-ai-engineer-interview-questions-answers-2026-guide/
3. **Top Artificial Intelligence (AI) Interview Questions and Answers** — GeeksforGeeks: https://www.geeksforgeeks.org/artificial-intelligence/artificial-intelligenceai-interview-questions-and-answers/
4. **AI Engineer Interview Questions and Answers (2026 Guide)** — hackajob: https://hackajob.com/en-us/talent/technical-assessment/ai-interview-questions-preparation-guide-for-2025
