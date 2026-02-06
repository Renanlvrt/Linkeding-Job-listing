Mission: Build Secure CV_Worker.py Pipeline
Squad activation: Security → Schema → Prompt → Backend → QA

You are building a secure, async Python worker (cv_worker.py) that:

Fetches pending JDs from Supabase job_descriptions table (status='pending' OR tailored_cv IS NULL).

Loads local master_cv.md (gitignore'd).

Calls local Ollama llama3.1:8b (with custom Modelfile: num_ctx=16384) using the Perplexity-researched system prompt for ATS-perfect CV tailoring.

Updates Supabase with tailored_cv (TEXT) and status='completed'.

Handles errors idempotently, logs to file, retries failed LLM calls.

Your Durham CS researcher context: Linux/HPC setup, PyTorch experience—use asyncio + ThreadPoolExecutor for GPU-safe parallelism (max 4 concurrent Ollama calls). Prioritize security (RLS, no CV commit), efficiency (batch 10-50 JDs), validation (diff CVs, keyword match score).

Pre-reqs (assume done): ollama pull llama3.1:8b; Supabase URL/KEY in .env; master_cv.md local.

🛡️ Phase 1: Security Agent (Spawn first)
Agent role: Lock it down.

text

1. Generate .gitignore:
   - .env
   - master_cv.md
   - __pycache__/
   - .venv/
   - *.log
   - supabase/migrations/  # if schema changes

2. Supabase RLS policies for job_descriptions (run these SQL):
ALTER TABLE job_descriptions ENABLE ROW LEVEL SECURITY;

-- Service key can read/update all (for worker), but anon/auth users limited
CREATE POLICY "Worker full access" ON job_descriptions
FOR ALL TO service_role USING (true);

CREATE POLICY "Users view own pending" ON job_descriptions
FOR SELECT TO authenticated
USING (auth.uid() = created_by); -- assume created_by uuid column

text
Add `created_by uuid REFERENCES auth.users` if missing.

1. Python client: Use `supabase-py` async client from `.env` SUPABASE_URL/KEY (service_role key). Validate JWT if needed.

2. CV security: Read master_cv.md as str, never log/print content. Temp dir for processing.
Output: Commit-ready .gitignore + RLS SQL script (setup_rls.sql). Block until done.

🗄️ Phase 2: Schema Agent (Parallel with Security)
Agent role: Ensure DB ready.

text
Check/assume job_descriptions schema:

- id uuid PK
- description text (JD)
- status text DEFAULT 'pending'
- tailored_cv text
- created_by uuid
- created_at timestamptz

SQL migration if needed:
ALTER TABLE job_descriptions
ADD COLUMN IF NOT EXISTS tailored_cv text,
ADD COLUMN IF NOT EXISTS status text DEFAULT 'pending';
CREATE INDEX IF NOT EXISTS idx_pending_jds ON job_descriptions(status) WHERE status = 'pending';

text

Add trigger: After update, if status='completed', notify realtime channel 'cv-ready'.
Output: migrate_schema.sql + index for perf.

📝 Phase 3: Prompt Engineer Agent (Parallel)
Agent role: Perfect Llama3.1:8b prompt using Perplexity research.

text

1. Create Ollama Modelfile for CV work (save as cv-llama.modelfile):
FROM llama3.1:8b
PARAMETER num_ctx 16384
PARAMETER temperature 0.1
SYSTEM """[PASTE FULL PERPLEXITY SYSTEM PROMPT HERE - the long ATS-aware one with no fabrication, Version B Balanced, 5-step analysis: JD keys → Mapping → Gaps → Tailored CV → Optional cover]"""

text
Run: `ollama create cv-llama -f cv-llama.modelfile`

1. User message template (dynamic):
{{CONSTRAINTS}}:

UK style: organisation/optimise, no photo/DOB.

Version B – Balanced.

Max 2 A4 pages.

JD: {{job_description}}

Master CV: {{master_cv_text}}

[Full 5-step task from Perplexity template]

text
Extract ONLY Section 4 – Rewritten CV as tailored_cv.

1. Validate output: Regex for no tables/images, keyword overlap >70% (use difflib), length <5000 chars.
Output: Modelfile + prompt_builder() function. Test with dummy JD.

⚙️ Phase 4: Backend Agent (Wait for 1-3)
Agent role: Orchestrate cv_worker.py.

text
Use: asyncio, aiofiles, supabase async client, ollama-python async.

Structure:
import asyncio, os, logging
from dotenv import load_dotenv
from supabase import create_client, Client
import ollama
from pathlib import Path

load_dotenv()
logging.basicConfig(filename='cv_worker.log', level=logging.INFO)

async def main():
supabase: Client = supabase # async client
sem = asyncio.Semaphore(4) # GPU-safe concurrency

text
while True:  # Daemon loop
    pending = await supabase.table('job_descriptions')\
        .select('id, description')\
        .eq('status', 'pending').execute()

    tasks = []
    for jd in pending.data[:10]:  # Batch 10
        task = process_jd(supabase, jd, sem)
        tasks.append(task)
    
    if tasks:
        await asyncio.gather(*tasks, return_exceptions=True)
    
    await asyncio.sleep(30)  # Poll
async def process_jd(supabase, jd, sem):
async with sem:
try:
cv_text = await aiofiles.read_text('master_cv.md')
prompt = build_prompt(cv_text, jd['description']) # From Phase 3

text
        resp = await ollama.chat(model='cv-llama', messages=prompt)
        tailored = extract_cv(resp['message']['content'])  # Section 4 only

        # Validate: keywords, no fab, length
        if not validate(tailored, jd['description'], cv_text):
            raise ValueError("Invalid output")
        
        await supabase.table('job_descriptions')\
            .update({'tailored_cv': tailored, 'status': 'completed'})\
            .eq('id', jd['id']).execute()
        logging.info(f"Completed {jd['id']}")
        
    except Exception as e:
        logging.error(f"Failed {jd['id']}: {e}")
        # Update status='failed' + retry_count
text
CLI: `python cv_worker.py --once` for testing; systemd for prod.
Output: Full cv_worker.py + requirements.txt (supabase, ollama, aiofiles, python-dotenv, aiohttp).

✅ Phase 5: QA Agent (Final review)
Agent role: Test & ship.

text

1. Unit tests: mock_supabase, mock_ollama, test_prompt, test_validate.
2. Run: `python cv_worker.py --once` on test JD → verify DB update.
3. Security scan: No hardcodes, CV gitignore'd, RLS enforced.
4. Perf: 10 JDs <5min on your setup.
5. Edge: LLM fail → status='failed'; dup process → no overwrite.
Output: tests.py + README.md (setup/run/deploy). Merge all phases.

Squad sync: Parallel where possible (Security/Schema/Prompt). Orchestrator: Block Backend until deps done. Generate ALL files in repo root. Prioritize: Secure > Correct > Fast. Use UK spelling. Go! 🚀

I want you to work on the folder: CV_automation where you will put all the files regarding the LLM creating the CV taylored to the job.

I will put my CV into a master_CV.md file that contains not an example of my CV but an example of my CV experience that you can fetch from and have different experience that you can take to taylor for each roles that I am applying.
You will analyse the two prompts (this current one stored in the folder CV_automation/overall_prompt.md and the main implementation prompt: CV_automation_master_prompt
You will analyse these two files constantly to make sure that you know what you are doing and what you have to implement next.
Make sure to be very organised, for that you will create skills and workflows and store it in the folder CV_automation where you will constantly be working on for this CV automation. For indication on later enhancement, you will create a folder in the root of this project indicating all implementation of this CV automation will have to check the skills and the workflows that you will create for this.
This way, you will always have the best practices on how to create the perfect CV which is ATS proof. (see the guide in CV_automation_master).
You will research the best practices and tips on how to get a very clean and consistent automation. (deep research the web for that) then you will create these skills + workflows. (indicated in the root of project) but files located in CV_automation. Then implement the whole implementation
