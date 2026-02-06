import asyncio
import os
import json
import logging
import subprocess
from datetime import datetime
from typing import Optional

import yaml
from dotenv import load_dotenv, find_dotenv
from supabase import create_async_client, AsyncClient
import ollama

from secure_cv_loader import SecureCVLoader
from prompt_builder import PromptBuilder
from scorer import CVScorer
from models import JDExtraction, CVScore
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
        self.supabase: AsyncClient = await create_async_client(
            os.getenv("VITE_SUPABASE_URL") or os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_SERVICE_KEY")
        )
        
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

    async def handle_realtime(self, payload):
        """Callback for new job inserts via Realtime."""
        job = payload.get('new')
        if job and job.get('status') in ['pending', 'retry']:
            logger.info(f"Realtime Trigger: New job detected {job['id']}")
            # We don't await here to avoid blocking the channel; Semaphore handles concurrency
            asyncio.create_task(self.process_job(job))

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
                
                # 2. Stage 1: Extraction (with timeout)
                logger.info(f"Job {job_id}: Chain 1 - Extracting JD...")
                prompt_1 = PromptBuilder.build_extraction_prompt(job_record['description'])
                
                # Ollama call with 30s timeout simulation
                response_1 = await asyncio.wait_for(
                    asyncio.to_thread(ollama.generate, model=self.model_name, prompt=prompt_1),
                    timeout=45.0
                )
                
                # 3. Parse YAML
                try:
                    jd_data = yaml.safe_load(response_1['response'])
                    jd_extract = JDExtraction(**jd_data)
                except Exception as parse_err:
                    logger.error(f"Job {job_id}: Chain 1 Parse Fail - {parse_err}")
                    # Fallback default
                    jd_extract = JDExtraction(
                        seniority="Mid",
                        top_hard_skills=["Python"],
                        top_soft_skills=["Communication"],
                        keywords=["ATS"],
                        major_responsibilities=["Software Engineering"]
                    )

                # 4. Stage 2: Drafting
                logger.info(f"Job {job_id}: Chain 2 - Drafting CV...")
                prompt_2 = PromptBuilder.build_tailoring_prompt(jd_extract, master_cv)
                response_2 = await asyncio.to_thread(ollama.generate, model=self.model_name, prompt=prompt_2)
                raw_tailored = response_2['response']
                
                # Strip preamble/chatter
                tailored_text = raw_tailored
                if "**" in raw_tailored[:200] and "\n" in raw_tailored[:200]:
                    # Likely has a "Based on..." preamble
                    marker = raw_tailored.find("**")
                    if marker != -1 and marker < 300:
                        tailored_text = raw_tailored[marker:]
                
                # 5. Scorer (Validation)
                logger.info(f"Job {job_id}: Validating output...")
                score_result = self.scorer.calculate_score(tailored_text, jd_extract)
                
                # 6. Persistence & Logic Branching
                # Lowered threshold to 70 for local 8B model testing
                status = "completed" if score_result.total_score >= 70 and not score_result.hallucination_detected else "retry"
                if score_result.hallucination_detected:
                    status = "failed" # Permanent fail on hallucination
                
                # Initial update data (exclude pdf_url for now)
                update_data = {
                    "tailored_cv": tailored_text,
                    "ats_score": int(score_result.total_score),
                    "status": status,
                    "keyword_match_json": score_result.metrics,
                    "error_log": "\n".join(score_result.suggestions),
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
