# Workflow: Batch Processing

## Goal

Efficiently process multiple job applications in a single run without overwhelming the local LLM or GPU resources.

## Steps

1. **Selection**: Query Supabase for top N records with `status='pending'`, ordered by `created_at` (FIFO).
2. **Resource Allocation**: Initialize a `Semaphore` with value 4 (or as configured for the GPU) to limit concurrent LLM calls.
3. **Execution**:
    - Wrap the **Tailoring Flow** in a `Task` or `Coroutine`.
    - Use `asyncio.gather` with `return_exceptions=True` to process the batch.
4. **Retry Logic**:
    - If an LLM call fails due to timeout or OOM, mark the record for retry in the next batch.
    - Track `retry_count` in the database. After 3 failures, mark as `permanently_failed`.
5. **Cooldown**: Add a short sleep (e.g., 30s) between batches to allow GPU memory cleanup if necessary.
6. **Logging**: Aggregate batch results and log success/failure counts.
