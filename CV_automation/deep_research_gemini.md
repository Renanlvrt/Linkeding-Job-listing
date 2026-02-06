1. Meta Llama 3.1 8B Instruct (recommended primary)
Why considered

State‑of‑the‑art open 8B instruction model from Meta; strong on general writing, reasoning, and instruction following.

Officially instruction‑tuned for dialogue; robust adherence to system prompts and formatting constraints.

Widely available:

Ollama: ollama pull llama3.1:8b

LM Studio / llama.cpp: HF model meta-llama/Llama-3.1-8B-Instruct
​

Context window: 128k tokens per Meta docs, allowing entire CV + lengthy JD + prompts without truncation.

There is even a LoRA fine‑tune for CV/JD analysis built on this base (LlamaFactoryAI/Llama-3.1-8B-Instruct-cv-job-description-matching), indicating it works very well for resume–JD reasoning tasks.
​

Instruction following / editing behaviour

Meta reports strong instruction‑following (IFEval) and safety/accuracy improvements vs earlier Llama generations.
​

Community evaluations (e.g. Llama‑3.1‑Storm built on it) show very high instruction‑following scores, confirming it can reliably obey format constraints like “no tables, plain text headings.”
​

Long‑context + solid editing makes it good at:

Rewriting bullets while preserving core facts.

Inserting JD keywords in a natural way.

Respecting “do not invent experience” when explicitly instructed.

Hardware and deployment

Runs well via:

Ollama: CPU‑only or GPU‑assisted; default context ~2k; can raise num_ctx (e.g. 8192–16384) in custom models.

GGUF via llama.cpp / LM Studio from community conversions.

For typical 16–32 GB RAM and a mid‑range GPU:

Quantization recommendation (GGUF):

Q4_K_M: best balance of quality and speed on consumer hardware (common recommendation for 7–8B GGUF models).

Q5_K_M: if you have more RAM/VRAM and want slightly higher fidelity at modest speed cost.

Q6_K: near‑FP16 quality but more demanding; mainly if you have 24+ GB RAM or a 16+ GB GPU.

Pros

Excellent English writing; professional tone suited for CVs.

Strong adherence to system‑level constraints (ATS formatting, no hallucinated roles if clearly forbidden).

Very long context (128k) allows you to include CV + JD + some prior variants without token squeeze.

Broad ecosystem (Ollama, LM Studio, local frameworks) and community examples.

Proven basis for CV/JD‑matching fine‑tunes.
​

Cons

8B model is heavier than ultra‑small (3–4B) models; CPU‑only inference can be slower, though still usable with Q4 quantization.

As with any smallish open model, will hallucinate if constraints are weak; you must be explicit about “no invented experience.”

1. Qwen2.5‑7B‑Instruct
Why considered

Latest Alibaba open model family; 7B instruct version is very strong at instruction following and structured output (JSON, tables, etc.), and long‑text generation.

Specifically advertised improvements in:

Instruction following.

Long‑text generation (>8k tokens).

Resilience to diverse system prompts (good for strict ATS formatting instructions).
​

Available as GGUF with many quantizations and good tooling support, used with llama.cpp, LM Studio, etc.

Context window / hardware

Context window: up to 128k tokens.
​

GGUF quantizations from Q2_K to Q8_0; documentation and community guides suggest:

Q4_K_M as the default “good quality / good speed” choice.

Q5_K_M when you have extra memory and care about higher fidelity.

Hardware guidance for 7B GGUF:

CPU‑only: 8–16 GB RAM is enough for lower‑bit quantization; 16–32 GB is comfortable.
​

GPU: mid‑range GPU (8–12 GB) can offload most layers for good latency.

Pros

Excellent at honoring system prompts and emitting clean, structured outputs (useful when you want standard section headers and bullet lists).
​

Long context and multilingual support; good if you need non‑English JDs.

Strong general benchmarks and widely used, so well‑battle‑tested.

Cons

Slight tendency to be verbose; you may need to explicitly constrain bullet length.

English is very good, but stylistically Llama 3.1 tends to feel slightly more “native corporate” to many users.

1. Phi‑4‑Mini‑Instruct (≈3.8B) and Phi‑4 (14B) via Ollama
Why considered

Microsoft’s latest small‑model family; Phi‑4 mini (3.8B) targets strong reasoning and instruction‑following in a compact model.

GGUF versions of Phi‑4‑Mini‑Instruct exist with multiple quantizations (Q2–Q8), optimized for local inference, including low‑RAM systems.

Full Phi‑4 (14B) is available in Ollama (ollama pull phi4) with ~32k context window and ~11 GB VRAM footprint, showing strong performance in structured text extraction, summarization, and reasoning in local setups.
​

Context / quantization / hardware

Phi‑4‑Mini:

Context: up to 128k tokens in GGUF implementations.

Quantization guidance (from GGUF docs):

Q4_K_M typically recommended default; good balance for laptops and desktops (~2–3 GB).

Q6_K_L or Q8_0 if you want maximum quality and have sufficient memory.
​

Phi‑4 (14B) in Ollama:

Context: ~32k tokens.

Requires ≈11 GB VRAM for good performance, so best if you have a 12–16 GB GPU.
​

Pros

Very compact Phi‑4‑Mini is ideal if you want fast CPU‑only inference while still getting decent writing and instruction adherence.

Microsoft training emphasizes curated, textbook‑style data and reasoning‑dense content, which tends to reduce sloppy hallucinations and improves logical consistency.

Full Phi‑4 14B gives high‑quality writing and reasoning, suitable for more nuanced tailoring if your GPU allows it.

Cons

3.8B‑parameter models, even strong ones, are still a bit weaker stylistically than the best 7–8B models for polished corporate writing.

Ecosystem and community patterns for CV‑specific tasks are less mature than Llama 3.1’s at the moment.

1. Mistral‑7B‑Instruct‑v0.2 (GGUF)
Why considered

Classic, widely used 7B instruct model with a strong local‑first ecosystem and numerous GGUF builds.

Some 2025 resume‑writing reviews specifically call out Mistral 7B as strong for narrative cohesion and business‑style resumes, especially for tying varied experiences into a coherent story and cleaning up redundancy.
​

Available in many quantization levels via TheBloke’s GGUF conversions, easily usable in LM Studio or llama.cpp clients.

Context / hardware

v0.1 context: 4k tokens; newer Mistral 7B variants have 32k context windows.

GGUF quantizations from Q2_K to Q8_0; documentation highlights Q4_K_M as a particularly good general‑purpose trade‑off.

Pros

Good instruction‑following and coherent prose; historically popular for local setups, so very well understood.

Works well on CPU‑only systems with 16 GB RAM in Q4_K_M.

Community reports highlight strengths in narrative CV writing and summaries.
​

Cons

Older than Llama 3.1 / Qwen2.5 / Phi‑4; generally weaker on more recent benchmarks and safety/hallucination metrics.

Shorter context in v0.1 (4k) can be limiting for very long CVs and verbose JDs unless you pick newer 32k variants and configure them carefully.

1. Specialized fine‑tunes (optional note)
If you are comfortable going beyond vanilla models:

Llama‑3.1‑8B‑Instruct‑cv‑job‑description‑matching (LoRA)
A resume/JD matching fine‑tune on Llama 3.1 8B Instruct that explicitly analyzes CV–JD compatibility and provides structured scoring and recommendations.
​

Strong for analysis; could be combined with a generic Llama 3.1 instance for actual rewriting.

Requires loading the base model plus LoRA, which is more setup work than an Ollama one‑liner.

Primary recommended local model
Primary choice: Meta Llama 3.1 8B Instruct
Why this model is the best trade‑off for your use case

Quality of tailored CV output

Among open 7–8B models, Llama 3.1 8B is at or near the top on general language quality, reasoning, and instruction adherence.

The language style is very suitable for professional resumes: clear, concise, and not overly flowery by default.

The existence of a CV/JD‑matching fine‑tune on top of it indicates its strong baseline performance for CV semantics.
​

ATS‑friendliness

The model is highly responsive to system prompts; you can reliably enforce:

Plain text only.

Standard headings (Experience, Education, Skills, etc.).

Bullet point style and minimal formatting.

Modern ATS systems just need linear text with clear headings and bullets; this model easily stays within that guardrail when instructed clearly.

Speed on typical consumer hardware

At 8B parameters with Q4_K_M quantization, it runs comfortably on:

16–32 GB RAM CPU‑only (slower, but fine for resumes).

Mid‑range 8–12 GB GPU with llama.cpp/Ollama offloading for snappy responses.

Context can be reduced (e.g. 4k–8k) for speed, since a CV + JD + prompts will usually fit within that.

Ease of setup in local tools

Ollama: ollama pull llama3.1:8b then run directly.

LM Studio: point at meta-llama/Llama-3.1-8B-Instruct or a GGUF conversion.

Extensive tutorial ecosystem around Llama 3.1 and context configuration.

Suggested configuration

If using Ollama:

Base pull: ollama pull llama3.1:8b

For bigger contexts, define a custom model (e.g. llama3.1-cv:8b) with num_ctx set to 8192 or 16384 for safety (trade‑off vs speed).

If using GGUF (llama.cpp / LM Studio):

Start with Q4_K_M; upgrade to Q5_K_M if you have plenty of RAM/VRAM and want slightly better editing fidelity.

System prompt for the local CV‑tailoring model
Below is a reusable system prompt you can drop into Ollama / LM Studio / your chat UI for Llama 3.1 8B Instruct (also works well with other shortlist models).

You can adapt wording slightly, but try to keep the structure and constraints.

System prompt (paste as system/assistant configuration):

You are an ATS‑aware CV tailoring assistant. Your role is to rewrite and tailor a candidate’s CV or résumé to a specific job description while:

Preserving factual accuracy of all dates, job titles, employers, degrees, and certifications.

Producing ATS‑friendly, plain‑text output that parses cleanly in modern Applicant Tracking Systems.

Core behavioural rules

Never invent or fabricate:

Do not invent new employers, job titles, degrees, certifications, or employment dates.

Do not claim tools, technologies, or skills that are not at least implied by the original CV content.

Do not make up specific metrics that are clearly unsupported (e.g. “increased revenue by 400%”) unless the user’s CV already includes that number or a very close approximation.

Allowed extrapolation (conservative):

You may slightly elaborate on existing achievements using plausible detail that is strongly implied by the CV (e.g. specifying typical metrics ranges, clarifying scope, or naming reasonable stakeholders), but:

Keep these elaborations modest and realistic.

Avoid specific, unverifiable numbers unless the CV already suggests them (e.g. “reduced latency by 30–40%” can be turned into “reduced latency by ~35%” if that is clearly implied).

If in doubt, prefer vague but honest phrasing (“significantly improved”, “substantially reduced”) over fabricated precision.

Formatting and structure (ATS‑friendly):

Output must be plain text only:

No tables, columns, images, text boxes, or unusual symbols.

No Markdown tables or complex layouts.

Use a linear, top‑to‑bottom structure with standard section headings, for example:

Professional Summary (optional, short, tailored)

Key Skills or Skills

Experience

Education

Optional: Projects, Certifications, Publications, Awards, etc., only if present in the original CV.

Use simple bullet points with a leading dash - or similar plain marker.

Use clear, concise language with strong action verbs and focus on measurable or observable impact where possible.

ATS + human readability optimisation:

Optimise every bullet for:

Relevance to the target job description (keywords, responsibilities, domain).

Clarity and concision (avoid long, convoluted sentences).

Impact (results, scope, scale, technologies).

Naturally incorporate high‑value keywords from the job description without unnatural “keyword stuffing”.

Avoid overly generic buzzwords without evidence from the candidate’s experience.

Job‑description awareness:

Always start by analysing the job description:

Extract the top required skills, tools/technologies, and responsibilities.

Prioritise these when rewriting bullets and sections.

Emphasise the candidate’s most relevant achievements and experience.

Regional and style constraints:

When the user provides constraints (e.g. “UK CV style, no US spelling”, “keep to two pages”, “do not change job titles or dates”), treat them as strict requirements.

Respect spelling conventions (e.g. “organisation” vs “organization”) as instructed.

Output components

When requested, your response should contain, in this order:

A concise bullet list of top required skills/keywords from the job description.

A mapping of those skills/keywords to the candidate’s existing experience.

A brief bullet list of gaps or missing keywords.

A fully rewritten, tailored CV in ATS‑friendly plain text.

Optionally, a short, tailored, ATS‑friendly cover letter (≤ 1 page).

Version style (A/B/C)

The user may ask for a specific version style:

Version A – Conservative: Minimal edits. Mostly rephrase and re‑order, lightly injecting keywords. Preserve phrasing where possible.

Version B – Balanced: Moderate rephrasing, some restructuring, and added achievements where implied, while preserving clear factual content.

Version C – Creative: More aggressive rewriting for impact and clarity, while still strictly factually accurate. Do not change actual roles, dates, employers, or degrees.

Always clearly label which version style you applied.

If you are uncertain whether a detail is factually supported by the original CV, do not include it. When in doubt, remain conservative and honest.

User prompt template for each job application
This is a copy‑pasteable template for use with the above system prompt and Llama 3.1 8B Instruct. You can adapt formatting for your UI, but keep the structure and labels.

Use this as a user message.

User prompt template:

You are using the system instructions that define you as an ATS‑aware CV tailoring assistant.
Follow them carefully for this specific job application.

1. Constraints and preferences

Apply the following constraints and preferences exactly:

{{CONSTRAINTS}}

Examples of constraints you might see (these are examples only; follow whatever is actually provided above):

Keep the CV within two A4 pages when printed.

Use UK CV style: no headshot, no date of birth, no marital status.

Use UK spelling (e.g. “organisation”, “optimise”).

Do not change job titles, employer names, or employment dates.

Do not change degree names or qualification dates.

Do not add any tools, technologies, or certifications that are not at least implied by the CV.

Additionally, use the following rewrite style version:

Version requested: {{VERSION}}

Acceptable values:

Version A – Conservative

Version B – Balanced

Version C – Creative

If the user does not specify a version, default to Version B – Balanced.

1. Target job description

Here is the full job description for this application:

text
{{JOB_DESCRIPTION}}
3. Current CV / résumé

Here is my current CV / résumé in full:

text
{{CV}}
4. Task breakdown

Perform the following steps in order, and clearly label each section in your output.

Step 1 – Analyse the job description and extract key requirements

Carefully read the job description.

Identify and list the top 10–15 skills, tools/technologies, and keywords that:

Are explicitly required or strongly implied.

Would be important for ATS keyword matching.

Output this as:

Section 1 – JD key skills and keywords

Bullet list of 10–15 items, each in the form:

- Skill / keyword: short note on how it appears in the JD

Step 2 – Map job requirements to my existing experience

Analyse my CV and map each of the JD skills/keywords to specific roles, projects, or achievements in my experience.

For each JD keyword from Section 1, indicate:

Whether it is clearly present, weakly present / implied, or missing.

The most relevant role(s) and bullet(s) from my CV.

Output this as:

Section 2 – Mapping of JD requirements to CV
For each keyword:

Keyword:

Status: (clearly present / weakly present / missing)

Evidence from CV: (quote or paraphrase the most relevant existing bullet(s) or experience area)

Step 3 – Identify gaps and missing keywords

Based on the mapping in Section 2, list the most important gaps or missing/weak keywords that might hurt ATS or recruiter alignment.

Output this as:

Section 3 – Gaps and missing keywords

Bullet list (5–10 bullets) describing:

Missing or under‑emphasised skills/keywords.

Areas where the CV could better mirror the job description while remaining truthful.

Step 4 – Produce a fully rewritten, tailored CV (ATS‑friendly)

Rewrite my CV so that it is tailored to this specific job, while strictly obeying:

All constraints given in Section 1.

All system‑level rules (especially “no fabrication”).

The rewritten CV must:

Retain the same factual content:

Same jobs, employers, dates, degrees, and certifications.

Same core responsibilities and achievements, expressed more effectively.

Enhance and reorganise content to align with the job description:

Bring the most relevant experience and skills to the top.

Adjust bullet phrasing to highlight impact, scope, and relevant technologies.

Use an ATS‑friendly structure, with plain text headings such as:

Professional Summary (short and tailored to the JD; 2–5 lines).

Key Skills or Skills (prioritising JD‑relevant skills and tools).

Experience.

Education.

Optional: Projects, Certifications, Publications, Awards, etc., only if they existed in the original CV.

Use simple bullet points starting with a dash -.

Use clear, concise language and strong action verbs (e.g. “led”, “developed”, “optimised”, “reduced”, “improved”).

Respect the requested version style:

Version A – Conservative:

Minimal changes; mostly rephrase bullets and insert missing JD keywords where they naturally fit.

Preserve section ordering unless clearly suboptimal.

Version B – Balanced:

Moderate rephrasing and restructuring.

Add reasonable achievement details and metrics where they are strongly implied by the CV.

Carefully emphasise JD‑relevant responsibilities and outcomes.

Version C – Creative:

More substantial rewriting for clarity, flow, and impact.

Aggressively prioritise JD‑relevant content and streamline or merge weaker content.

Still must not change factual elements such as roles, dates, degrees, employers, or claim tools not present in the original CV.

Output the rewritten CV as:

Section 4 – Rewritten ATS‑friendly CV ({{VERSION}})
Then provide the full CV as plain text under that heading.

Step 5 – Optional: Tailored cover letter (≤ 1 page)

If and only if the constraints above explicitly ask for a cover letter, then:

Draft a concise, ATS‑friendly cover letter tailored to:

This specific job description.

The strengths of my CV as rewritten in Section 4.

Keep it to one page or less of plain text.

Use a professional, confident but not over‑hyped tone.

Use UK or US spelling and conventions as requested in the constraints.

Output the cover letter as:

Section 5 – Tailored cover letter (optional)

If the constraints do not ask for a cover letter, explicitly state:
“No cover letter requested; skipping Section 5.”

Please now perform all steps in order and provide your response with the five clearly labelled sections described above.

(Optional) Usage tips
A few practical tips to get the most out of this setup for local CV tailoring:

Context window management

For Llama 3.1 8B in Ollama:

Default num_ctx may be small (around 2k); for CV+JD work, define a custom model with num_ctx of 4096–8192 to avoid truncation while keeping memory use reasonable.

For GGUF in LM Studio / llama.cpp:

A 4k context is usually enough for a 2–3 page CV + long JD + prompts, but you can set 8k–16k for comfort if your RAM/VRAM allows.

Chunking long CVs / portfolios

If your CV plus JD significantly exceeds your local context limit:

First run a pass where the model summarises or extracts key experience blocks from very long project lists or publication lists.

Then feed only condensed sections plus the JD into the tailoring template.

This is rarely necessary with 8k+ contexts, but can matter for very long academic or consulting CVs.

Sanity‑checking hallucinations

After generating the tailored CV:

Diff against your original (or manually scan) focusing on:

New metrics or numbers.

New tools/technologies.

Any changed job titles, employers, or dates.

Delete or correct any invented details. If you notice a pattern, tighten the constraints in {{CONSTRAINTS}} (e.g. “Do not add any numeric performance metrics not explicitly present; use qualitative phrases instead.”).

Building a reusable workflow

Keep a master CV with full detail.

For each job:

Paste the job description and master CV into the template.

Save the tailored CV as a new file/version.

Over time, you can incorporate frequently used tailored bullets back into the master CV (while still being honest and generic).

Model choice per machine

On CPU‑only / low‑RAM setups:

Consider Phi‑4‑Mini‑Instruct Q4_K_M or Phi‑3‑Mini‑4K‑Instruct Q4_K_M for faster responses if Llama 3.1 8B feels too slow, using the same prompts.

On mid‑range GPU (8–12 GB):

Llama 3.1 8B Instruct Q4_K_M or Q5_K_M is an excellent default.

On high‑VRAM GPUs (16+ GB):

You can consider stepping up to Phi‑4 14B or even Llama 3.1 70B (if you’re comfortable with the hardware cost) for marginal gains in nuance.

Once you have Llama 3.1 8B Instruct running locally
