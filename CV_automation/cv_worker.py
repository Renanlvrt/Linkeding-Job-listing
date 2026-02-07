import asyncio
import os
import json
import logging
import subprocess
import re
from datetime import datetime
from typing import Optional

import yaml
from dotenv import load_dotenv, find_dotenv
from supabase import create_async_client, AsyncClient
import ollama

from secure_cv_loader import SecureCVLoader
from prompt_builder import PromptBuilder
from scorer import CVScorer
from models import JDExtraction, CVMapping, CVScore
from generate_pdf import generate_sprout_pdf

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("cv_worker.log"), logging.StreamHandler()]
)
logger = logging.getLogger("CVWorker")

load_dotenv(find_dotenv())

class CVWorker:
    def __init__(self):
        self.supabase = None # Initialized in run()
        self.master_cv_path = "c:/Users/renan/Desktop/Side_projects/Ai agent/cold email agent/CV_automation/master_CV.md"
        self.loader = SecureCVLoader(self.master_cv_path)
        self.scorer = CVScorer(self.loader.load_and_sanitize())
        self.model_name = "cv-llama:8b"
        self.semaphore = None
        self.channel = None

    async def initialize(self):
        """Async initialization of Supabase client and Realtime."""
        # Force loading from root if not found locally
        root_env = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
        load_dotenv(root_env)
        
        url = os.getenv("VITE_SUPABASE_URL") or os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_SERVICE_KEY")
        
        if not url or not key:
            # Try find_dotenv as fallback
            load_dotenv(find_dotenv())
            url = os.getenv("VITE_SUPABASE_URL") or os.getenv("SUPABASE_URL")
            key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_SERVICE_KEY")

        if not url or not key:
            raise ValueError("Supabase URL or Key missing. Check .env in root or CV_automation.")

        self.supabase: AsyncClient = await create_async_client(url, key)
        
        # Realtime Channel
        self.channel = self.supabase.realtime.channel('cv_jobs')
        self.channel.on_postgres_changes(
            event='INSERT', 
            schema='public', 
            table='job_descriptions', 
            callback=lambda payload: asyncio.create_task(self.handle_realtime(payload))
        )
        await self.channel.subscribe()
        logger.info("Realtime subscription active.")

    def strip_chatter(self, llm_output: str) -> str:
        """
        Removes conversational filler from the start/end of the LLM output.
        """
        # 1. Regex to find the start of the CV (Standard headers)
        # Looks for "# Name" or "## Professional Summary" or similar
        match = re.search(r'(^#\s+|##\s+Professional|##\s+Experience|##\s+Skills)', llm_output, re.MULTILINE | re.IGNORECASE)
        
        if match:
            return llm_output[match.start():]
        
        # Fallback: specific removal of common chatty phrases
        lines = llm_output.split('\n')
        clean_lines = []
        started = False
        for line in lines:
            # Detect start of markdown content
            if line.strip().startswith('#') or line.strip().startswith('**'):
                started = True
            
            if started:
                clean_lines.append(line)
                
        return "\n".join(clean_lines) if clean_lines else llm_output

    async def handle_realtime(self, payload):
        """Callback for new job inserts via Realtime."""
        logger.info(f"Realtime Data: {payload}")
        job = payload.get('new')
        if job:
            status = job.get('status')
            logger.info(f"Job {job.get('id')} Status: {status}")
            if status in ['pending', 'retry']:
                logger.info(f"Realtime Trigger: Processing job {job['id']}")
                asyncio.create_task(self.process_job(job))
            else:
                logger.info(f"Ignoring job {job.get('id')} with status '{status}'")

    async def get_gpu_concurrency(self) -> int:
        """
        Dynamically determine concurrency based on GPU memory.
        """
        try:
            # nvidia-smi query
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=memory.used', '--format=csv,noheader,nounits'], 
                capture_output=True, text=True, check=True
            )
            used = int(result.stdout.strip())
            # Assume 8GB threshold for 3 concurrent 8B models
            limit = 3 if used < 4096 else 2
            logger.info(f"GPU Used: {used}MB. Setting concurrency to {limit}.")
            return limit
        except Exception as e:
            logger.warning(f"Failed to query GPU (pynvml/nvidia-smi): {e}. Defaulting to concurrency=1.")
            return 1

    async def process_job(self, job_record: dict):
        job_id = job_record['id']
        retry_count = job_record.get('retry_count', 0)
        
        async with self.semaphore:
            logger.info(f"Processing Job {job_id} (Retry: {retry_count})")
            try:
                # 1. Load and Sanitize CV
                master_cv = self.loader.load_and_sanitize()
                
                # 3. Stage 1: Extraction
                logger.info(f"Job {job_id}: Chain 1 - Extracting JD...")
                prompt_1 = PromptBuilder.build_extraction_prompt(job_record['description'])
                
                # Ollama call with timeout
                response_1 = await asyncio.wait_for(
                    asyncio.to_thread(ollama.generate, model=self.model_name, prompt=prompt_1),
                    timeout=45.0
                )
                
                raw_extraction = response_1['response']
                # Robust extraction: look for YAML blocks
                yaml_text = raw_extraction
                if "```yaml" in raw_extraction:
                    yaml_text = raw_extraction.split("```yaml")[1].split("```")[0]
                elif "```" in raw_extraction:
                    yaml_text = raw_extraction.split("```")[1].split("```")[0]
                
                try:
                    jd_data = yaml.safe_load(yaml_text)
                    jd_extract = JDExtraction(**jd_data)
                    logger.info(f"Job {job_id}: Extracted Keywords: {jd_extract.keywords}")
                except Exception as parse_err:
                    logger.error(f"Job {job_id}: Chain 1 Extraction Failed: {parse_err}")
                    # Fallback default
                    jd_extract = JDExtraction(
                        seniority="Mid",
                        top_hard_skills=["Python"],
                        top_soft_skills=["Communication"],
                        keywords=["Software", "Developer"],
                        major_responsibilities=["Software Engineering"]
                    )
                
                # 4. Stage 2: Mapping
                logger.info(f"Job {job_id}: Chain 2 - Mapping experience to keywords...")
                prompt_map = PromptBuilder.build_mapping_prompt(jd_extract, master_cv)
                response_map = await asyncio.to_thread(ollama.generate, model=self.model_name, prompt=prompt_map)
                raw_mapping = response_map['response']
                
                # Robust extraction: look for YAML blocks
                yaml_map_text = raw_mapping
                if "```yaml" in raw_mapping:
                    yaml_map_text = raw_mapping.split("```yaml")[1].split("```")[0]
                elif "```" in raw_mapping:
                    yaml_map_text = raw_mapping.split("```")[1].split("```")[0]
                
                try:
                    map_data = yaml.safe_load(yaml_map_text)
                    mapping = CVMapping(**map_data)
                    logger.info(f"Job {job_id}: Mapped {len(mapping.mapped_skills)} skills.")
                except Exception as map_err:
                    logger.error(f"Job {job_id}: Chain 2 Mapping Failed: {map_err}")
                    mapping = CVMapping(mapped_skills={}, missing_skills=jd_extract.keywords, suggested_phrasings={})

                # 5. Stage 3: Drafting
                logger.info(f"Job {job_id}: Chain 3 - Drafting CV...")
                prompt_3 = PromptBuilder.build_tailoring_prompt(jd_extract, mapping, master_cv)
                response_3 = await asyncio.to_thread(ollama.generate, model=self.model_name, prompt=prompt_3)
                raw_tailored = response_3['response']
                
                # 6. Post-process: Strip chatter and enforce UK spelling
                tailored_text = self.strip_chatter(raw_tailored)
                tailored_text = PromptBuilder.post_process_spelling(tailored_text)
                
                # 7. Scorer (Validation)
                logger.info(f"Job {job_id}: Validating output...")
                score_result = self.scorer.calculate_score(tailored_text, jd_extract)
                
                # 8. Persistence & Loop-Breaking Logic
                PASSING_SCORE = 70.0
                status = "completed" # Default to completed to break retry loops
                
                if score_result.hallucination_detected:
                    status = "failed" # Only hard fail on hallucination
                
                # If score is low, we still complete but log it
                error_prefix = ""
                if score_result.total_score < PASSING_SCORE:
                    logger.warning(f"Job {job_id}: Low score {score_result.total_score}. Completing anyway to prevent loop.")
                    error_prefix = f"⚠️ LOW SCORE WARNING ({score_result.total_score}): "

                # Initial update data (exclude pdf_url for now)
                update_data = {
                    "tailored_cv": tailored_text,
                    "ats_score": int(score_result.total_score),
                    "status": status,
                    "keyword_match_json": score_result.metrics,
                    "keywords_found": mapping.mapped_skills,
                    "missing_keywords": mapping.missing_skills,
                    "error_log": error_prefix + "\n".join(score_result.suggestions),
                    "retry_count": retry_count + 1 if status == "retry" else retry_count
                }
                
                # 7. PDF Generation
                logger.info(f"Job {job_id}: Generating PDF...")
                os.makedirs("output", exist_ok=True)
                pdf_path = f"output/{job_id}.pdf"
                await generate_sprout_pdf(tailored_text, pdf_path, 'ats_style.css')

                # Initial update (status/text)
                await self.supabase.table("job_descriptions").update(update_data).eq("id", job_id).execute()
                
                # Upload to Supabase Storage
                logger.info(f"Job {job_id}: Uploading to Storage...")
                try:
                    with open(pdf_path, 'rb') as f:
                        file_data = f.read()
                        # Upload to 'cv-pdfs' bucket
                        await self.supabase.storage.from_('cv-pdfs').upload(
                            path=f"{job_id}.pdf",
                            file=file_data,
                            file_options={"upsert": "true"}
                        )
                    
                    # Get public URL - NOTE: In some versions of supabase-py async, this might be sync or async
                    # We check and await if it's a coroutine
                    url_res = self.supabase.storage.from_('cv-pdfs').get_public_url(f"{job_id}.pdf")
                    if asyncio.iscoroutine(url_res):
                        url_res = await url_res
                    
                    # Store final URL
                    await self.supabase.table("job_descriptions").update({"pdf_url": str(url_res)}).eq("id", job_id).execute()
                except Exception as storage_err:
                    logger.warning(f"Storage Upload Failed for {job_id}: {storage_err}")

                logger.info(f"Job {job_id} Finished. Status: {status}. Score: {score_result.total_score}")

            except asyncio.TimeoutError:
                logger.error(f"Job {job_id} timed out.")
                await self.supabase.table("job_descriptions").update({"status": "retry", "error_log": "Timeout"}).eq("id", job_id).execute()
            except Exception as e:
                logger.error(f"Job {job_id} Critical Error: {e}")
                await self.supabase.table("job_descriptions").update({"status": "failed", "error_log": str(e)}).eq("id", job_id).execute()

    async def run(self, once=False):
        await self.initialize()
        concurrency = await self.get_gpu_concurrency()
        self.semaphore = asyncio.Semaphore(concurrency)
        
        logger.info("Worker started. Polling Supabase...")
        try:
            while True:
                try:
                    # Poll pending and retry (with backoff logic simplified here)
                    res = await self.supabase.table("job_descriptions")\
                        .select("*")\
                        .in_("status", ["pending", "retry"])\
                        .limit(10)\
                        .execute()
                    
                    jobs = res.data
                    if jobs:
                        tasks = [self.process_job(job) for job in jobs]
                        await asyncio.gather(*tasks)
                    
                    if once: break
                    await asyncio.sleep(30) # 30s poll interval
                except Exception as e:
                    logger.error(f"Main loop error: {e}")
                    await asyncio.sleep(60)
        except Exception as e:
            logger.critical(f"Worker crashed: {e}")

if __name__ == "__main__":
    worker = CVWorker()
    asyncio.run(worker.run())
