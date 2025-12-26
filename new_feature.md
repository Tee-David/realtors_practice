You are a senior data platform architect.

Context:
I run an enterprise-grade real estate aggregation system:
- Python scraper triggered via GitHub Actions.
- Dynamic configs to scrape many real estate websites at once.
- Produces raw data with 85+ fields across 9 schema categories.
- Rule-based cleaning, normalization, deduplication.
- Data stored in Firestore.
- Next.js frontend consuming 91 REST API endpoints.
- Current pain: fields, categories, and numeric values are often misaligned across sources; filters break; prices and types are inconsistent.

Goal:
I am considering adding a free LLM layer using ApiFreeLLM to improve schema alignment and data consistency.

Important:
I do NOT want code yet.
I want a strategic plan only.

What I want from you:
1) Propose where an LLM layer should live in my pipeline and why.
2) Define the responsibilities of this LLM stage versus existing rule-based logic.
3) Describe how ApiFreeLLM’s limitations (free, rate-limited, lower accuracy) affect the design.
4) Outline the data flow from raw scrape to frontend after introducing this layer.
5) Identify risks:
   - hallucinated values,
   - cost and rate limits,
   - schema drift,
   - latency,
   - debugging.
6) Propose safeguards and validation strategies.
7) Suggest how to phase this in:
   - pilot,
   - metrics,
   - rollback plan.
8) Recommend what inputs the LLM should see and what it must never see.

Do NOT:
- write code,
- draft prompts,
- suggest frontend AI usage.

Output:
A clear, step-by-step architectural plan with reasoning for each decision.
